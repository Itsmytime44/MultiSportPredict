#!/usr/bin/env python
"""
MLB Advanced Prop Edge Engine
==============================
Evaluates sabermetric edges for MLB player props using pybaseball
and Odds API market lines.

Calculates market-grade edges for three prop types:
    1. MLB_PROPS_K      — Pitcher Strikeout props (SwStr%, CSW%, Opp K%)
    2. MLB_PROPS_HR     — Home Run props (Barrel%, ISO, Pitcher HR/9)
    3. MLB_NRFI_YRFI    — No Run / Yes Run First Inning (1st-in xFIP, BB%, wRC+)

Each section outputs a standardized dictionary with lean, model_prob (0–100),
and supporting detail suitable for integration with `predict_match.py` and
the existing `mlb_module.py` pipeline.

Author: MultiSportPredict Team
"""

from __future__ import annotations

import math
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# ── Optional pybaseball imports ────────────────────────────────────────────
# Each is wrapped so the module loads even if pybaseball is missing or
# individual endpoints fail (Fangraphs 403, etc.).
try:
    from pybaseball import (
        statcast_batter_expected_stats,
        statcast_pitcher_expected_stats,
        statcast_batter_exitvelo_barrels,
        statcast_pitcher_exitvelo_barrels,
        statcast_pitcher_pitch_arsenal,
    )
    PYBASEBALL_AVAILABLE = True
except ImportError:
    PYBASEBALL_AVAILABLE = False

from mlb.mlb_park_factors import get_park_factor
from mlb.mlb_module import _normalize_team_name

logger = logging.getLogger(__name__)

# ── Fallback defaults (league-average-ish values) ──────────────────────────

FALLBACK_PITCHER = {
    "swstr_pct": 11.0,      # Swinging-strike %
    "csw_pct": 28.0,        # Called + Swinging strike %
    "k_pct": 22.0,          # Overall K%
    "bb_pct": 8.0,          # Walk %
    "hr_per_9": 1.2,        # HR allowed per 9 IP
    "xfip": 4.00,           # Expected FIP
    "xfip_1st": 4.20,       # 1st-inning xFIP (slightly worse)
    "bb_pct_1st": 9.0,      # 1st-inning BB%
}

FALLBACK_BATTER = {
    "barrel_pct": 6.0,      # Barrel% (league avg ~6%)
    "iso": 0.150,           # Isolated Power (SLG - AVG)
    "wrc_plus": 100,        # wRC+ (league average = 100)
    "k_pct": 22.0,
}

FALLBACK_TEAM_K_PCT = 22.5  # League-average opponent K%


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _american_to_implied(american_odds: int) -> float:
    """Convert American odds to implied probability (0–1)."""
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return abs(american_odds) / (abs(american_odds) + 100)


def _clamp_prob(prob: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, prob))


def _safe_float(val, default: float = 0.0) -> float:
    """Convert a value to float, returning *default* on failure."""
    try:
        v = float(val)
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except (TypeError, ValueError, OverflowError):
        return default


def _safe_pct(val, default: float = 0.0) -> float:
    """Parse a percentage column that might be stored as '22.5' or 22.5."""
    v = _safe_float(val, default)
    # If the value is already a proportion (e.g. 0.225) scale it
    if 0.0 < v <= 1.0:
        return v * 100.0
    return v


# ══════════════════════════════════════════════════════════════════════════════
# DATA FETCHING (with graceful fallbacks)
# ══════════════════════════════════════════════════════════════════════════════

def _fetch_pitcher_stats(player_name: str, team_abbr: str, year: int = 2025) -> Dict[str, Any]:
    """
    Gather pitcher advanced stats from pybaseball Statcast endpoints.
    Falls back to FALLBACK_PITCHER dict on any failure.
    """
    stats = dict(FALLBACK_PITCHER)

    if not PYBASEBALL_AVAILABLE:
        logger.debug("pybaseball not available; using fallback pitcher stats")
        return stats

    try:
        # 1) Expected stats (xERA, xFIP, K%, BB%)
        df_exp = statcast_pitcher_expected_stats(year)
        if df_exp is not None and not df_exp.empty:
            # Try to find the pitcher by name (partial match) or team
            mask = df_exp.get("last_name", "").str.contains(
                player_name.split()[-1] if " " in player_name else player_name,
                case=False, na=False
            )
            if mask.any():
                row = df_exp[mask].iloc[0]
                stats["k_pct"] = _safe_pct(row.get("k_pct", stats["k_pct"]), stats["k_pct"])
                stats["bb_pct"] = _safe_pct(row.get("bb_pct", stats["bb_pct"]), stats["bb_pct"])
                stats["xfip"] = _safe_float(row.get("xfip", stats["xfip"]), stats["xfip"])

        # 2) Pitch arsenal (SwStr%, CSW%)
        df_ars = statcast_pitcher_pitch_arsenal(year)
        if df_ars is not None and not df_ars.empty:
            mask = df_ars.get("pitcher", "").str.contains(
                player_name.split()[-1] if " " in player_name else player_name,
                case=False, na=False
            )
            if mask.any():
                row = df_ars[mask].iloc[0]
                stats["swstr_pct"] = _safe_pct(row.get("swstr_pct", stats["swstr_pct"]), stats["swstr_pct"])
                csw = _safe_pct(row.get("csw_pct", row.get("csw", stats["csw_pct"])), stats["csw_pct"])
                stats["csw_pct"] = csw

        # 3) Exit velo / barrels (HR/9 proxy)
        df_ev = statcast_pitcher_exitvelo_barrels(year)
        if df_ev is not None and not df_ev.empty:
            mask = df_ev.get("pitcher", "").str.contains(
                player_name.split()[-1] if " " in player_name else player_name,
                case=False, na=False
            )
            if mask.any():
                row = df_ev[mask].iloc[0]
                stats["hr_per_9"] = _safe_float(row.get("hr_per_9", stats["hr_per_9"]), stats["hr_per_9"])
                stats["barrel_pct_allowed"] = _safe_pct(
                    row.get("barrel_pct", None), 6.0
                )

    except Exception as e:
        logger.warning(f"pybaseball pitcher fetch failed for {player_name}: {e}")

    return stats


def _fetch_batter_stats(player_name: str, team_abbr: str, year: int = 2025) -> Dict[str, Any]:
    """
    Gather batter advanced stats. Falls back to FALLBACK_BATTER.
    """
    stats = dict(FALLBACK_BATTER)

    if not PYBASEBALL_AVAILABLE:
        return stats

    try:
        # 1) Expected stats (xwOBA, xSLG, barrel%, K%)
        df_exp = statcast_batter_expected_stats(year)
        if df_exp is not None and not df_exp.empty:
            mask = df_exp.get("last_name", "").str.contains(
                player_name.split()[-1] if " " in player_name else player_name,
                case=False, na=False
            )
            if mask.any():
                row = df_exp[mask].iloc[0]
                stats["barrel_pct"] = _safe_pct(row.get("barrel_percent", stats["barrel_pct"]), stats["barrel_pct"])
                stats["iso"] = _safe_float(row.get("xslg", stats["iso"]), stats["iso"])
                stats["k_pct"] = _safe_pct(row.get("k_pct", stats["k_pct"]), stats["k_pct"])
                stats["wrc_plus"] = _safe_float(row.get("wrc_plus", stats["wrc_plus"]), stats["wrc_plus"])

        # 2) Exit velo / barrels (alternate source)
        df_brl = statcast_batter_exitvelo_barrels(year)
        if df_brl is not None and not df_brl.empty:
            mask = df_brl.get("batter", "").str.contains(
                player_name.split()[-1] if " " in player_name else player_name,
                case=False, na=False
            )
            if mask.any():
                row = df_brl[mask].iloc[0]
                stats["barrel_pct"] = _safe_pct(
                    row.get("barrel_batted_balls", stats["barrel_pct"]),
                    stats["barrel_pct"]
                )

    except Exception as e:
        logger.warning(f"pybaseball batter fetch failed for {player_name}: {e}")

    return stats


def _fetch_team_k_pct(team_abbr: str, year: int = 2025) -> float:
    """
    Fetch a team's overall K% (opponent perspective — how often does
    this team's batters strike out?). Falls back to league average.
    """
    if not PYBASEBALL_AVAILABLE:
        return FALLBACK_TEAM_K_PCT

    try:
        # Use statcast_batter_expected_stats with team filter
        df_exp = statcast_batter_expected_stats(year)
        if df_exp is not None and not df_exp.empty and "team" in df_exp.columns:
            team_rows = df_exp[df_exp["team"].str.upper() == team_abbr.upper()]
            if not team_rows.empty:
                return _safe_pct(team_rows["k_pct"].mean(), FALLBACK_TEAM_K_PCT)
    except Exception:
        pass

    return FALLBACK_TEAM_K_PCT


# ══════════════════════════════════════════════════════════════════════════════
# EDGE CALCULATORS
# ══════════════════════════════════════════════════════════════════════════════

def _calc_k_edge(
    pitcher_stats: Dict[str, Any],
    opponent_k_pct: float,
    market_american_odds: int = 0,
) -> Dict[str, Any]:
    """
    Strikeout prop edge calculation.
    
    Uses a composite of SwStr%, CSW%, and opponent K% to produce a
    k_skill score, then compares it to the market-implied probability.

    Returns dict with 'lean', 'model_prob' (0–100), 'edge_pct', and 'summary'.
    """
    swstr = pitcher_stats.get("swstr_pct", 11.0)
    csw = pitcher_stats.get("csw_pct", 28.0)
    opp_k = opponent_k_pct

    # Composite K skill (weighted toward SwStr as the most predictive)
    k_skill = 0.50 * (swstr / 11.0) + 0.30 * (csw / 28.0) + 0.20 * (opp_k / 22.5)

    # Market implied probability (use default ~50% if no market odds)
    if market_american_odds != 0:
        implied = _american_to_implied(market_american_odds)
    else:
        implied = 0.50

    # Scale to 0–100 confidence
    raw = (k_skill - implied) * 400 + 50
    model_prob = round(_clamp_prob(raw, 0, 100), 1)

    # Lean / recommendation
    if model_prob >= 55:
        lean = "Over"
        strength = "STRONG BET" if (swstr > 15 and opp_k > 25) else "BET"
    elif model_prob <= 45:
        lean = "Under"
        strength = "STRONG BET" if (swstr < 8 and opp_k < 20) else "BET"
    else:
        lean = "PASS"
        strength = "PASS"

    summary_parts = []
    summary_parts.append(f"SwStr={swstr:.1f}%")
    summary_parts.append(f"CSW={csw:.1f}%")
    summary_parts.append(f"OppK={opp_k:.1f}%")
    if swstr > 15 and opp_k > 25:
        summary_parts.append("FLAG: SwStr>15% & OppK>25%")

    return {
        "lean": lean,
        "model_prob": model_prob,
        "edge_pct": round((k_skill - implied) * 100, 2),
        "summary": f"{strength}: {' | '.join(summary_parts)}",
        "pitcher_swstr_pct": round(swstr, 1),
        "pitcher_csw_pct": round(csw, 1),
        "opponent_k_pct": round(opp_k, 1),
    }


def _calc_hr_edge(
    batter_stats: Dict[str, Any],
    pitcher_hr9: float,
    park_hr_factor: float,
    market_american_odds: int = 0,
) -> Dict[str, Any]:
    """
    Home Run prop edge calculation.
    
    Combines batter Barrel%, ISO, and opposing pitcher HR/9, adjusted
    by park factor, to estimate HR probability vs market.
    """
    barrel = batter_stats.get("barrel_pct", 6.0)
    iso = batter_stats.get("iso", 0.150)

    # Composite HR skill (centered on league-average barrel ~6%, ISO ~.150)
    hr_skill = 0.50 * (barrel / 6.0) + 0.30 * (iso / 0.150) + 0.20 * (pitcher_hr9 / 1.2)
    hr_skill *= park_hr_factor

    if market_american_odds != 0:
        implied = _american_to_implied(market_american_odds)
    else:
        implied = 0.12  # Typical market break-even for HR Yes prop

    raw = (hr_skill * 0.12 - implied) * 300 + 50
    model_prob = round(_clamp_prob(raw, 0, 100), 1)

    if model_prob >= 55:
        lean = "Yes HR"
    elif model_prob <= 45:
        lean = "No HR"
    else:
        lean = "PASS"

    summary_parts = [
        f"Barrel={barrel:.1f}%",
        f"ISO={iso:.3f}",
        f"HR/9={pitcher_hr9:.2f}",
        f"Park={park_hr_factor:.2f}",
    ]

    return {
        "lean": lean,
        "model_prob": model_prob,
        "edge_pct": round((hr_skill * 0.12 - implied) * 100, 2),
        "summary": ' | '.join(summary_parts),
        "batter_barrel_pct": round(barrel, 1),
        "batter_iso": round(iso, 3),
        "pitcher_hr_per_9": round(pitcher_hr9, 2),
        "park_hr_factor": round(park_hr_factor, 2),
    }


def _calc_nrfi_edge(
    home_pitcher: Dict[str, Any],
    away_pitcher: Dict[str, Any],
    home_top3_wrc: List[float],
    away_top3_wrc: List[float],
    market_american_odds: int = 0,
) -> Dict[str, Any]:
    """
    NRFI / YRFI edge calculation.
    
    Evaluates 1st-inning run probability by considering:
      - Starting pitchers' 1st-inning xFIP (lower = better)
      - Starting pitchers' 1st-inning BB% (lower = better)
      - Top 3 batters' wRC+ (higher = more likely to score)
    """
    h_xfip_1st = home_pitcher.get("xfip_1st", FALLBACK_PITCHER["xfip_1st"])
    a_xfip_1st = away_pitcher.get("xfip_1st", FALLBACK_PITCHER["xfip_1st"])
    h_bb_1st = home_pitcher.get("bb_pct_1st", FALLBACK_PITCHER["bb_pct_1st"])
    a_bb_1st = away_pitcher.get("bb_pct_1st", FALLBACK_PITCHER["bb_pct_1st"])
    h_wrc = np.mean(home_top3_wrc) if home_top3_wrc else 100.0
    a_wrc = np.mean(away_top3_wrc) if away_top3_wrc else 100.0

    # 1st-inning skill: lower xFIP and BB% favour NRFI; higher wRC+ favours YRFI.
    # Scale factors: xFIP of 4.0 → 1.0, BB% of 9% → 1.0, wRC+ of 100 → 1.0
    pitcher_score = (4.0 / h_xfip_1st) * 0.25 + (4.0 / a_xfip_1st) * 0.25
    pitcher_score += (9.0 / max(h_bb_1st, 1.0)) * 0.15 + (9.0 / max(a_bb_1st, 1.0)) * 0.15
    batter_score = (h_wrc / 100.0) * 0.10 + (a_wrc / 100.0) * 0.10

    # Composite: >1.0 favours NRFI, <1.0 favours YRFI
    nrfi_skill = pitcher_score * (1.0 - batter_score * 0.3)

    if market_american_odds != 0:
        implied = _american_to_implied(market_american_odds)
    else:
        implied = 0.52  # Typical NRFI market is ~ -110 / -120

    raw = (nrfi_skill - implied) * 200 + 50
    model_prob = round(_clamp_prob(raw, 0, 100), 1)

    if model_prob >= 55:
        lean = "NRFI"
    elif model_prob <= 45:
        lean = "YRFI"
    else:
        lean = "PASS"

    summary_parts = [
        f"H-xFIP1={h_xfip_1st:.2f}",
        f"A-xFIP1={a_xfip_1st:.2f}",
        f"H-BB1={h_bb_1st:.1f}%",
        f"A-BB1={a_bb_1st:.1f}%",
        f"Top3wRC={h_wrc:.0f}/{a_wrc:.0f}",
    ]

    return {
        "lean": lean,
        "model_prob": model_prob,
        "edge_pct": round((nrfi_skill - implied) * 100, 2),
        "summary": ' | '.join(summary_parts),
        "home_pitcher_xfip_1st": round(h_xfip_1st, 2),
        "away_pitcher_xfip_1st": round(a_xfip_1st, 2),
        "home_pitcher_bb_pct_1st": round(h_bb_1st, 1),
        "away_pitcher_bb_pct_1st": round(a_bb_1st, 1),
        "home_top3_mean_wrc": round(h_wrc, 1),
        "away_top3_mean_wrc": round(a_wrc, 1),
    }


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def fetch_mlb_advanced_markets(
    api_key: str,
    home_team: str,
    away_team: str,
    market_odds: Optional[Dict[str, int]] = None,
    year: int = 2025,
) -> Dict[str, Any]:
    """
    Evaluate all three advanced prop markets for an MLB game.

    Parameters
    ----------
    api_key : str
        The Odds API key (used for market line lookup; may be ignored
        if *market_odds* is provided directly).
    home_team : str
        Home team name or abbreviation (e.g. "NYY", "Yankees").
    away_team : str
        Away team name or abbreviation.
    market_odds : dict, optional
        Pre-fetched Odds API lines keyed by market:
        ``{"k_over": +110, "hr_yes": +250, "nrfi": -120}``
        If omitted, default break-even probabilities are used.
    year : int
        Season year for Statcast data queries (default 2025).

    Returns
    -------
    dict
        Nested dictionary with keys ``MLB_PROPS_K``, ``MLB_PROPS_HR``,
        ``MLB_NRFI_YRFI``.
    """
    if market_odds is None:
        market_odds = {}

    home_abbr = _normalize_team_name(home_team)
    away_abbr = _normalize_team_name(away_team)

    # ── Fetch pitcher & batter stats ─────────────────────────────────
    # In production these player names would come from a roster DB or
    # the Odds API event details. Here we use placeholder names that
    # will match pybaseball if they happen to be on the active roster.
    home_pitcher_name = f"{home_abbr} SP"
    away_pitcher_name = f"{away_abbr} SP"

    home_pitcher = _fetch_pitcher_stats(home_pitcher_name, home_abbr, year)
    away_pitcher = _fetch_pitcher_stats(away_pitcher_name, away_abbr, year)

    # Team-level opponent K%
    home_opp_k = _fetch_team_k_pct(away_abbr, year)   # Away batters → home pitcher
    away_opp_k = _fetch_team_k_pct(home_abbr, year)   # Home batters → away pitcher

    # Batter stats (sample top-3 batters per team — in production these
    # would come from the confirmed lineup)
    # Placeholder: we create 3 generic batters per team
    home_batters_stats = [
        _fetch_batter_stats(f"{home_abbr} Batter 1", home_abbr, year),
        _fetch_batter_stats(f"{home_abbr} Batter 2", home_abbr, year),
        _fetch_batter_stats(f"{home_abbr} Batter 3", home_abbr, year),
    ]
    away_batters_stats = [
        _fetch_batter_stats(f"{away_abbr} Batter 1", away_abbr, year),
        _fetch_batter_stats(f"{away_abbr} Batter 2", away_abbr, year),
        _fetch_batter_stats(f"{away_abbr} Batter 3", away_abbr, year),
    ]

    # Park factors
    park_hr = get_park_factor(home_abbr, "hr_factor")

    # ── MLB_PROPS_K ──────────────────────────────────────────────────
    k_home = _calc_k_edge(
        home_pitcher, home_opp_k, market_odds.get("k_over_home", 0)
    )
    k_away = _calc_k_edge(
        away_pitcher, away_opp_k, market_odds.get("k_over_away", 0)
    )

    # Overall K market lean: pick the side with higher model_prob
    k_lean = k_home["lean"] if k_home["model_prob"] >= k_away["model_prob"] else k_away["lean"]
    k_prob = max(k_home["model_prob"], k_away["model_prob"])

    mlb_props_k = {
        "home_pitcher": {
            "team": home_abbr,
            "swstr_pct": k_home["pitcher_swstr_pct"],
            "csw_pct": k_home["pitcher_csw_pct"],
            "opp_k_pct": k_home["opponent_k_pct"],
            "lean": k_home["lean"],
            "model_prob": k_home["model_prob"],
        },
        "away_pitcher": {
            "team": away_abbr,
            "swstr_pct": k_away["pitcher_swstr_pct"],
            "csw_pct": k_away["pitcher_csw_pct"],
            "opp_k_pct": k_away["opponent_k_pct"],
            "lean": k_away["lean"],
            "model_prob": k_away["model_prob"],
        },
        "lean": k_lean,
        "model_prob": k_prob,
        "summary_home": k_home["summary"],
        "summary_away": k_away["summary"],
    }

    # ── MLB_PROPS_HR ─────────────────────────────────────────────────
    hr_results = []
    for batter_stat, abbr in zip(
        home_batters_stats + away_batters_stats,
        [home_abbr] * 3 + [away_abbr] * 3,
    ):
        # For home batters, the opposing pitcher is away_pitcher (and vice versa)
        pitcher_hr9 = (away_pitcher["hr_per_9"] if abbr == home_abbr
                       else home_pitcher["hr_per_9"])
        edge = _calc_hr_edge(batter_stat, pitcher_hr9, park_hr)
        hr_results.append({
            "team": abbr,
            "barrel_pct": edge["batter_barrel_pct"],
            "iso": edge["batter_iso"],
            "lean": edge["lean"],
            "model_prob": edge["model_prob"],
            "summary_factors": edge["summary"],
        })

    # Aggregate HR lean: highest model_prob across batters
    best_hr = max(hr_results, key=lambda x: x["model_prob"])
    hr_lean = best_hr["lean"]
    hr_prob = best_hr["model_prob"]

    mlb_props_hr = {
        "top_batters": hr_results,
        "lean": hr_lean,
        "model_prob": hr_prob,
    }

    # ── MLB_NRFI_YRFI ────────────────────────────────────────────────
    home_top3_wrc = [b.get("wrc_plus", 100) for b in home_batters_stats]
    away_top3_wrc = [b.get("wrc_plus", 100) for b in away_batters_stats]

    nrfi = _calc_nrfi_edge(
        home_pitcher, away_pitcher,
        home_top3_wrc, away_top3_wrc,
        market_odds.get("nrfi", 0),
    )

    mlb_nrfi_yrfi = {
        "home_pitcher": {
            "team": home_abbr,
            "xfip_1st": nrfi["home_pitcher_xfip_1st"],
            "bb_pct_1st": nrfi["home_pitcher_bb_pct_1st"],
        },
        "away_pitcher": {
            "team": away_abbr,
            "xfip_1st": nrfi["away_pitcher_xfip_1st"],
            "bb_pct_1st": nrfi["away_pitcher_bb_pct_1st"],
        },
        "top_3_batters": {
            "home_wrc_plus": home_top3_wrc,
            "away_wrc_plus": away_top3_wrc,
        },
        "lean": nrfi["lean"],
        "model_prob": nrfi["model_prob"],
        "summary": nrfi["summary"],
    }

    # ── Assemble result ──────────────────────────────────────────────
    return {
        "MLB_PROPS_K": mlb_props_k,
        "MLB_PROPS_HR": mlb_props_hr,
        "MLB_NRFI_YRFI": mlb_nrfi_yrfi,
        "meta": {
            "year": year,
            "home_team": home_abbr,
            "away_team": away_abbr,
            "park_hr_factor": round(park_hr, 2),
            "pybaseball_available": PYBASEBALL_AVAILABLE,
            "note": (
                "Player names are placeholder-based. For best results, pass "
                "actual starting pitcher and lineup data."
            ),
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# CLI TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 3:
        print("Usage: python mlb/mlb_prop_edges.py <home_team> <away_team> [api_key]")
        sys.exit(1)

    home = sys.argv[1]
    away = sys.argv[2]
    key = sys.argv[3] if len(sys.argv) > 3 else ""

    result = fetch_mlb_advanced_markets(api_key=key, home_team=home, away_team=away)
    print(json.dumps(result, indent=2, default=str))