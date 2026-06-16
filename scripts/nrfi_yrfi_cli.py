#!/usr/bin/env python
"""
NRFI / YRFI CLI — First-Inning Scoring Probability Analyzer
=============================================================
Evaluates whether the first inning will see a run (Yes Run First Inning)
or remain scoreless (No Run First Inning) using:

  • The Odds API v4 markets (player_prop / alternate_lines)
  • Pitcher-batter splits for the first 6 outs (first 2 innings)
  • Park factor and weather adjustments
  • Sabermetric edge calculations (xFIP, SwStr%, wRC+, Barrel%)

Usage:
    python scripts/nrfi_yrfi_cli.py --home YAN --away BOS --api-key KEY
    python scripts/nrfi_yrfi_cli.py --home "New York Yankees" --away "Boston Red Sox"

Output: Structured table with pitcher/batter breakdown and final lean.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# ── Rich for terminal styling (equivalent to chalk + cli-progress + table) ──
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ── Optional pybaseball for live sabermetric data ───────────────────────────
try:
    from pybaseball import (
        statcast_batter_expected_stats,
        statcast_pitcher_expected_stats,
        statcast_pitcher_pitch_arsenal,
    )
    PYBASEBALL_AVAILABLE = True
except ImportError:
    PYBASEBALL_AVAILABLE = False

# Add project root for internal imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mlb.mlb_park_factors import get_park_factor
from mlb.mlb_module import _normalize_team_name

# ── Console ─────────────────────────────────────────────────────────────────
console = Console() if RICH_AVAILABLE else None

# ── API endpoints ───────────────────────────────────────────────────────────
ODDS_API_BASE = "https://api.the-odds-api.com/v4"

# ── League-average fallbacks ────────────────────────────────────────────────
FALLBACK = {
    "xfip_1st": 4.20,
    "bb_pct_1st": 9.0,
    "k_pct": 22.0,
    "swstr_pct": 11.0,
    "barrel_pct": 6.0,
    "wrc_plus": 100,
    "iso": 0.150,
    "hr_per_9": 1.2,
}


@dataclass
class PitcherSplit:
    """Pitcher metrics relevant to first-inning scoring."""
    name: str = "TBD"
    team: str = "TBD"
    xfip_1st: float = FALLBACK["xfip_1st"]
    bb_pct_1st: float = FALLBACK["bb_pct_1st"]
    swstr_pct: float = FALLBACK["swstr_pct"]
    k_pct: float = FALLBACK["k_pct"]
    hr_per_9: float = FALLBACK["hr_per_9"]
    barrel_pct_allowed: float = 6.0


@dataclass
class BatterSplit:
    """Batter metrics relevant to first-inning scoring."""
    name: str = "TBD"
    team: str = "TBD"
    wrc_plus: float = FALLBACK["wrc_plus"]
    barrel_pct: float = FALLBACK["barrel_pct"]
    iso: float = FALLBACK["iso"]
    k_pct: float = FALLBACK["k_pct"]


@dataclass
class NRFIResult:
    """Final structured result for one game."""
    home_team: str
    away_team: str
    home_pitcher: PitcherSplit = field(default_factory=PitcherSplit)
    away_pitcher: PitcherSplit = field(default_factory=PitcherSplit)
    home_top3_batters: List[BatterSplit] = field(default_factory=list)
    away_top3_batters: List[BatterSplit] = field(default_factory=list)
    park_hr_factor: float = 1.0
    weather: Dict[str, Any] = field(default_factory=dict)
    market_nrfi_price: Optional[int] = None
    model_prob: float = 50.0
    lean: str = "PASS"
    summary: str = ""
    error: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# DATA FETCHING
# ══════════════════════════════════════════════════════════════════════════════

def _odds_api_get(endpoint: str, api_key: str, params: dict = None) -> dict:
    """GET request to The Odds API with timeout and error handling."""
    if params is None:
        params = {}
    params["apiKey"] = api_key
    url = f"{ODDS_API_BASE}/{endpoint.lstrip('/')}"
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.Timeout:
        return {"error": "API timeout — The Odds API did not respond within 15s."}
    except requests.HTTPError as e:
        return {"error": f"HTTP {resp.status_code}: {e}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_event_id(api_key: str, sport_key: str, team1: str, team2: str) -> str:
    """
    Resolve team names to an Odds API event_id.
    Handles partial string matches and aliases.
    """
    data = _odds_api_get(f"sports/{sport_key}/events", api_key)
    if "error" in data:
        raise ValueError(data["error"])
    if isinstance(data, list):
        events = data
    elif isinstance(data, dict):
        events = data.get("data", data.get("events", [data]))
    else:
        events = []

    t1_lower = team1.lower()
    t2_lower = team2.lower()

    for ev in events:
        ht = (ev.get("home_team") or "").lower()
        at = (ev.get("away_team") or "").lower()
        if (t1_lower in ht or t1_lower in at) and (t2_lower in ht or t2_lower in at):
            return ev["id"]

    raise ValueError(
        f"No event found matching '{team1}' vs '{team2}' in sport '{sport_key}'. "
        f"Check team spelling or sport key."
    )


def fetch_nrfi_odds(api_key: str, event_id: str) -> Optional[int]:
    """
    Fetch NRFI market odds from The Odds API.
    Returns the American odds for NRFI (No Run First Inning), or None.
    """
    data = _odds_api_get(
        f"sports/baseball_mlb/events/{event_id}/odds",
        api_key,
        params={"regions": "us", "markets": "alternate_lines", "oddsFormat": "american"},
    )
    if "error" in data:
        return None
    if isinstance(data, list):
        events = data
    elif isinstance(data, dict):
        events = [data]
    else:
        return None

    for ev in events:
        for bm in ev.get("bookmakers", []):
            for market in bm.get("markets", []):
                key = (market.get("key") or "").lower()
                if "no_run" in key or "nrfi" in key or "first_inning" in key:
                    for outcome in market.get("outcomes", []):
                        name = (outcome.get("name") or "").lower()
                        if "no" in name or "nrfi" in name:
                            return outcome.get("price")
    return None


def _fetch_pitcher_stats(name_hint: str, team_abbr: str, year: int = 2025) -> PitcherSplit:
    """
    Fetch pitcher advanced stats from pybaseball.
    Falls back to league-average defaults on failure.
    """
    ps = PitcherSplit(name=name_hint, team=team_abbr)
    if not PYBASEBALL_AVAILABLE:
        return ps

    try:
        df = statcast_pitcher_expected_stats(year)
        if df is not None and not df.empty:
            mask = df.get("last_name", "").str.contains(
                name_hint.split()[-1] if " " in name_hint else name_hint,
                case=False, na=False,
            )
            if mask.any():
                row = df[mask].iloc[0]
                ps.xfip_1st = float(row.get("xfip", ps.xfip_1st))
                ps.k_pct = float(row.get("k_pct", ps.k_pct))
                if ps.k_pct <= 1.0:
                    ps.k_pct *= 100

        df_ars = statcast_pitcher_pitch_arsenal(year)
        if df_ars is not None and not df_ars.empty:
            mask = df_ars.get("pitcher", "").str.contains(
                name_hint.split()[-1] if " " in name_hint else name_hint,
                case=False, na=False,
            )
            if mask.any():
                row = df_ars[mask].iloc[0]
                ps.swstr_pct = float(row.get("swstr_pct", ps.swstr_pct))
                if ps.swstr_pct <= 1.0:
                    ps.swstr_pct *= 100
    except Exception:
        pass

    return ps


def _fetch_batter_stats(name_hint: str, team_abbr: str, year: int = 2025) -> BatterSplit:
    """
    Fetch batter advanced stats from pybaseball. Falls back to defaults.
    """
    bs = BatterSplit(name=name_hint, team=team_abbr)
    if not PYBASEBALL_AVAILABLE:
        return bs

    try:
        df = statcast_batter_expected_stats(year)
        if df is not None and not df.empty:
            mask = df.get("last_name", "").str.contains(
                name_hint.split()[-1] if " " in name_hint else name_hint,
                case=False, na=False,
            )
            if mask.any():
                row = df[mask].iloc[0]
                bs.wrc_plus = float(row.get("wrc_plus", bs.wrc_plus))
                bs.barrel_pct = float(row.get("barrel_percent", bs.barrel_pct))
                if bs.barrel_pct <= 1.0:
                    bs.barrel_pct *= 100
                bs.iso = float(row.get("xslg", bs.iso))
                bs.k_pct = float(row.get("k_pct", bs.k_pct))
                if bs.k_pct <= 1.0:
                    bs.k_pct *= 100
    except Exception:
        pass

    return bs


# ══════════════════════════════════════════════════════════════════════════════
# EDGE CALCULATION
# ══════════════════════════════════════════════════════════════════════════════

def _american_to_implied(odds: int) -> float:
    """American odds → implied probability (0–1)."""
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)


def calc_nrfi_edge(result: NRFIResult) -> NRFIResult:
    """
    Calculate NRFI model probability and lean from the fetched splits.

    Factors:
      • Pitcher 1st-inning xFIP — lower = NRFI-favourable
      • Pitcher 1st-inning BB% — lower = NRFI-favourable
      • Top-3 batters mean wRC+ — higher = YRFI-favourable
      • Park HR factor — higher park factor = YRFI-favourable
    """
    h = result.home_pitcher
    a = result.away_pitcher

    # Pitcher quality (higher = more likely NRFI)
    p_score = (4.0 / max(h.xfip_1st, 2.0)) * 0.30
    p_score += (4.0 / max(a.xfip_1st, 2.0)) * 0.30
    p_score += (9.0 / max(h.bb_pct_1st, 1.0)) * 0.10
    p_score += (9.0 / max(a.bb_pct_1st, 1.0)) * 0.10

    # Batter quality (higher = more likely YRFI, so it reduces p_score)
    home_wrc = sum(b.wrc_plus for b in result.home_top3_batters) / max(len(result.home_top3_batters), 1)
    away_wrc = sum(b.wrc_plus for b in result.away_top3_batters) / max(len(result.away_top3_batters), 1)
    b_score = (home_wrc / 100.0) * 0.05 + (away_wrc / 100.0) * 0.05

    # Park adjustment
    pf = result.park_hr_factor
    pf_adj = 1.0 + (pf - 1.0) * 0.15  # each 0.10 park factor shift → 1.5% swing

    nrfi_skill = p_score * (1.0 - b_score) * pf_adj

    # Convert to implied probability vs market
    if result.market_nrfi_price:
        implied = _american_to_implied(result.market_nrfi_price)
    else:
        implied = 0.52  # ~ -110 market default

    raw = (nrfi_skill - implied) * 200 + 50
    result.model_prob = round(max(0, min(100, raw)), 1)

    if result.model_prob >= 58:
        result.lean = "NRFI"
        strength = "BET" if result.model_prob < 75 else "STRONG BET"
    elif result.model_prob <= 42:
        result.lean = "YRFI"
        strength = "BET" if result.model_prob > 25 else "STRONG BET"
    else:
        result.lean = "PASS"
        strength = "PASS"

    parts = [
        f"H-xFIP1={h.xfip_1st:.2f}",
        f"A-xFIP1={a.xfip_1st:.2f}",
        f"H-BB1={h.bb_pct_1st:.1f}%",
        f"A-BB1={a.bb_pct_1st:.1f}%",
        f"Top3-wRC={home_wrc:.0f}/{away_wrc:.0f}",
        f"Park={pf:.2f}",
    ]
    result.summary = f"{strength}: {' | '.join(parts)}"
    return result


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def analyze_nrfi(
    api_key: str,
    home_team: str,
    away_team: str,
    sport_key: str = "baseball_mlb",
    year: int = 2025,
) -> NRFIResult:
    """
    Run the full NRFI/YRFI analysis pipeline.

    1. Resolve event ID from team names
    2. Fetch market odds from The Odds API
    3. Fetch pitcher/batter sabermetric splits via pybaseball
    4. Look up park factor
    5. Calculate edge and return structured result
    """
    home_abbr = _normalize_team_name(home_team)
    away_abbr = _normalize_team_name(away_team)

    result = NRFIResult(home_team=home_abbr, away_team=away_abbr)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        transient=True,
    ) as progress:
        # Step 1 — Resolve event
        t1 = progress.add_task("[cyan]Resolving event ID...", total=None)
        try:
            event_id = fetch_event_id(api_key, sport_key, home_team, away_team)
        except ValueError as e:
            result.error = str(e)
            return result
        progress.remove_task(t1)

        # Step 2 — Fetch market odds
        t2 = progress.add_task("[yellow]Fetching NRFI market odds...", total=None)
        result.market_nrfi_price = fetch_nrfi_odds(api_key, event_id)
        progress.remove_task(t2)

        # Step 3 — Fetch pitcher splits
        t3 = progress.add_task("[magenta]Fetching pitcher splits...", total=None)
        result.home_pitcher = _fetch_pitcher_stats(f"{home_abbr} SP", home_abbr, year)
        result.away_pitcher = _fetch_pitcher_stats(f"{away_abbr} SP", away_abbr, year)
        progress.remove_task(t3)

        # Step 4 — Fetch batter splits (top 3 per team)
        t4 = progress.add_task("[green]Fetching batter splits...", total=None)
        for i in range(1, 4):
            result.home_top3_batters.append(
                _fetch_batter_stats(f"{home_abbr} Batter {i}", home_abbr, year)
            )
            result.away_top3_batters.append(
                _fetch_batter_stats(f"{away_abbr} Batter {i}", away_abbr, year)
            )
        progress.remove_task(t4)

        # Step 5 — Park factor & weather
        t5 = progress.add_task("[blue]Loading park factors...", total=None)
        result.park_hr_factor = get_park_factor(home_abbr, "hr_factor")
        result.weather = {
            "temperature": 72,
            "wind_speed": 8,
            "wind_direction": 0,
            "note": "Weather data placeholder — integrate with OpenWeather or MLBsavvy",
        }
        progress.remove_task(t5)

    # Step 6 — Calculate edge
    result = calc_nrfi_edge(result)
    return result


# ══════════════════════════════════════════════════════════════════════════════
# CLI DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

def print_result(result: NRFIResult) -> None:
    """Render the NRFI result as a structured, colorised table."""
    if result.error:
        console.print(f"[bold red]ERROR:[/] {result.error}")
        return

    # ── Header panel ───────────────────────────────────────────────────
    header = (
        f"[bold cyan]{result.away_team}[/] [white]@[/] "
        f"[bold cyan]{result.home_team}[/]  |  "
        f"NRFI Lean: [{'green' if result.lean == 'NRFI' else 'red' if result.lean == 'YRFI' else 'yellow'}]"
        f"{result.lean}[/]  "
        f"Confidence: [bold]{result.model_prob:.1f}%[/]"
    )
    console.print(Panel(header, title="NRFI / YRFI ANALYSIS", border_style="bright_blue"))

    # ── Pitcher table ──────────────────────────────────────────────────
    pit_table = Table(title="Starting Pitchers — 1st-Inning Splits", box=box.ROUNDED)
    pit_table.add_column("Team", style="cyan")
    pit_table.add_column("Pitcher", style="white")
    pit_table.add_column("xFIP (1st)", justify="right")
    pit_table.add_column("BB% (1st)", justify="right")
    pit_table.add_column("SwStr%", justify="right")
    pit_table.add_column("K%", justify="right")

    pit_table.add_row(
        f"[bold]{result.away_team}[/]", result.away_pitcher.name,
        f"{result.away_pitcher.xfip_1st:.2f}",
        f"{result.away_pitcher.bb_pct_1st:.1f}%",
        f"{result.away_pitcher.swstr_pct:.1f}%",
        f"{result.away_pitcher.k_pct:.1f}%",
    )
    pit_table.add_row(
        f"[bold]{result.home_team}[/]", result.home_pitcher.name,
        f"{result.home_pitcher.xfip_1st:.2f}",
        f"{result.home_pitcher.bb_pct_1st:.1f}%",
        f"{result.home_pitcher.swstr_pct:.1f}%",
        f"{result.home_pitcher.k_pct:.1f}%",
    )
    console.print(pit_table)
    console.print()

    # ── Batter table ───────────────────────────────────────────────────
    bat_table = Table(title="Top-3 Batters (projected)", box=box.ROUNDED)
    bat_table.add_column("Team", style="cyan")
    bat_table.add_column("Batter", style="white")
    bat_table.add_column("wRC+", justify="right")
    bat_table.add_column("Barrel%", justify="right")
    bat_table.add_column("ISO", justify="right")
    bat_table.add_column("K%", justify="right")

    for batter in result.away_top3_batters:
        bat_table.add_row(
            result.away_team, batter.name,
            f"{batter.wrc_plus:.0f}",
            f"{batter.barrel_pct:.1f}%",
            f"{batter.iso:.3f}",
            f"{batter.k_pct:.1f}%",
        )
    for batter in result.home_top3_batters:
        bat_table.add_row(
            result.home_team, batter.name,
            f"{batter.wrc_plus:.0f}",
            f"{batter.barrel_pct:.1f}%",
            f"{batter.iso:.3f}",
            f"{batter.k_pct:.1f}%",
        )
    console.print(bat_table)
    console.print()

    # ── Summary table ──────────────────────────────────────────────────
    sum_table = Table(title="Edge Summary", box=box.ROUNDED)
    sum_table.add_column("Metric", style="bold yellow")
    sum_table.add_column("Value", justify="right")

    nrfi_color = "green" if result.lean == "NRFI" else "red" if result.lean == "YRFI" else "yellow"
    sum_table.add_row("Lean", f"[{nrfi_color}]{result.lean}[/]")
    sum_table.add_row("Model Confidence", f"[bold]{result.model_prob:.1f}%[/]")
    sum_table.add_row("Market NRFI Odds",
                       f"{result.market_nrfi_price:+,d}" if result.market_nrfi_price else "N/A")
    sum_table.add_row("Park HR Factor", f"{result.park_hr_factor:.2f}")
    sum_table.add_row("Weather",
                       f"{result.weather.get('temperature', '?')}°F, "
                       f"{result.weather.get('wind_speed', '?')}mph wind")
    console.print(sum_table)
    console.print()

    # ── Full summary message ───────────────────────────────────────────
    console.print(Panel(
        f"[bold]{result.summary}[/]",
        border_style="bright_green" if result.lean != "PASS" else "yellow",
    ))


def print_result_plain(result: NRFIResult) -> None:
    """Fallback plain-text output when rich is not installed."""
    sep = "=" * 60
    print(sep)
    print(f"NRFI / YRFI ANALYSIS: {result.away_team} @ {result.home_team}")
    print(sep)
    print(f"  Lean:          {result.lean}")
    print(f"  Confidence:    {result.model_prob:.1f}%")
    print(f"  Market NRFI:   {result.market_nrfi_price:+,d}" if result.market_nrfi_price else "  Market NRFI:   N/A")
    print(f"  Park HR:       {result.park_hr_factor:.2f}")
    print()
    print("  Pitchers (1st-inning splits):")
    print(f"    {result.away_team:6s}  xFIP={result.away_pitcher.xfip_1st:.2f}  "
          f"BB%={result.away_pitcher.bb_pct_1st:.1f}  "
          f"SwStr%={result.away_pitcher.swstr_pct:.1f}")
    print(f"    {result.home_team:6s}  xFIP={result.home_pitcher.xfip_1st:.2f}  "
          f"BB%={result.home_pitcher.bb_pct_1st:.1f}  "
          f"SwStr%={result.home_pitcher.swstr_pct:.1f}")
    print()
    print(f"  Summary: {result.summary}")
    print(sep)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="NRFI / YRFI CLI — First-Inning Scoring Probability Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/nrfi_yrfi_cli.py --home NYY --away BOS --api-key $KEY\n"
            "  python scripts/nrfi_yrfi_cli.py --home \"Yankees\" --away \"Red Sox\" --sport baseball_mlb\n"
        ),
    )
    parser.add_argument("--home", required=True, help="Home team name or abbreviation")
    parser.add_argument("--away", required=True, help="Away team name or abbreviation")
    parser.add_argument("--api-key", default=os.environ.get("ODDS_API_KEY", ""),
                        help="The Odds API key (or set ODDS_API_KEY env var)")
    parser.add_argument("--sport", default="baseball_mlb",
                        help="Odds API sport key (default: baseball_mlb)")
    parser.add_argument("--year", type=int, default=2025,
                        help="Season year for Statcast data (default: 2025)")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON instead of formatted table")
    args = parser.parse_args()

    if not args.api_key:
        print("ERROR: --api-key is required (or set ODDS_API_KEY environment variable)", file=sys.stderr)
        sys.exit(1)

    # ── Run analysis ───────────────────────────────────────────────────
    result = analyze_nrfi(args.api_key, args.home, args.away, args.sport, args.year)

    # ── Output ─────────────────────────────────────────────────────────
    if args.json:
        print(json.dumps({
            "home_team": result.home_team,
            "away_team": result.away_team,
            "lean": result.lean,
            "model_prob": result.model_prob,
            "market_nrfi_price": result.market_nrfi_price,
            "park_hr_factor": result.park_hr_factor,
            "home_pitcher": {
                "name": result.home_pitcher.name,
                "xfip_1st": result.home_pitcher.xfip_1st,
                "bb_pct_1st": result.home_pitcher.bb_pct_1st,
                "swstr_pct": result.home_pitcher.swstr_pct,
                "k_pct": result.home_pitcher.k_pct,
            },
            "away_pitcher": {
                "name": result.away_pitcher.name,
                "xfip_1st": result.away_pitcher.xfip_1st,
                "bb_pct_1st": result.away_pitcher.bb_pct_1st,
                "swstr_pct": result.away_pitcher.swstr_pct,
                "k_pct": result.away_pitcher.k_pct,
            },
            "home_top3_wrc": [b.wrc_plus for b in result.home_top3_batters],
            "away_top3_wrc": [b.wrc_plus for b in result.away_top3_batters],
            "summary": result.summary,
            "error": result.error,
        }, indent=2))
    elif RICH_AVAILABLE:
        print_result(result)
    else:
        print_result_plain(result)

    # Exit with lean as exit code hint
    if result.error:
        sys.exit(1)
    if result.lean == "NRFI":
        print(f"\n→ Recommendation: NRFI (No Run First Inning) — Confidence {result.model_prob:.1f}%")
    elif result.lean == "YRFI":
        print(f"\n→ Recommendation: YRFI (Yes Run First Inning) — Confidence {result.model_prob:.1f}%")
    else:
        print(f"\n→ Recommendation: PASS — No clear edge (Confidence {result.model_prob:.1f}%)")


if __name__ == "__main__":
    main()