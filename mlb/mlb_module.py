"""
MLB Module for MultiSportPredict
=================================
Comprehensive MLB prediction module with:
- Statcast data ingestion via pybaseball
- Feature engineering for pitchers, hitters, umpires, and game contexts
- Full game prediction model (totals + sides)
- Player prop projections (K, HR, TB, Hits, Walks, RBIs)
"""
from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from pybaseball import statcast
except Exception:
    statcast = None

# Directory configuration
DATA_DIR = Path("data/mlb")
RAW_DIR = DATA_DIR / "raw"
FEAT_DIR = DATA_DIR / "features"
MODEL_DIR = DATA_DIR / "models"
OUT_DIR = Path("output/mlb")

# Create directories if they don't exist
for p in [RAW_DIR, FEAT_DIR, MODEL_DIR, OUT_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# Team name aliases for normalization
TEAM_ALIASES = {
    "Yankees": "NYY",
    "New York Yankees": "NYY",
    "Red Sox": "BOS",
    "Boston Red Sox": "BOS",
    "Dodgers": "LAD",
    "Los Angeles Dodgers": "LAD",
    "Mets": "NYM",
    "New York Mets": "NYM",
    "Cubs": "CHC",
    "Chicago Cubs": "CHC",
    "White Sox": "CWS",
    "Chicago White Sox": "CWS",
    "Astros": "HOU",
    "Houston Astros": "HOU",
    "Phillies": "PHI",
    "Philadelphia Phillies": "PHI",
    "Braves": "ATL",
    "Atlanta Braves": "ATL",
    "Giants": "SF",
    "San Francisco Giants": "SF",
    "Athletics": "OAK",
    "Oakland Athletics": "OAK",
    "Reds": "CIN",
    "Cincinnati Reds": "CIN",
    "Cardinals": "STL",
    "St. Louis Cardinals": "STL",
    "Pirates": "PIT",
    "Pittsburgh Pirates": "PIT",
    "Brewers": "MIL",
    "Milwaukee Brewers": "MIL",
    "Tigers": "DET",
    "Detroit Tigers": "DET",
    "Guardians": "CLE",
    "Cleveland Guardians": "CLE",
    "Royals": "KC",
    "Kansas City Royals": "KC",
    "Twins": "MIN",
    "Minnesota Twins": "MIN",
    "Rangers": "TEX",
    "Texas Rangers": "TEX",
    "Angels": "LAA",
    "Los Angeles Angels": "LAA",
    "Mariners": "SEA",
    "Seattle Mariners": "SEA",
    "Athletics": "OAK",
    "Rays": "TB",
    "Tampa Bay Rays": "TB",
    "Orioles": "BAL",
    "Baltimore Orioles": "BAL",
    "Blue Jays": "TOR",
    "Toronto Blue Jays": "TOR",
    "Marlins": "MIA",
    "Miami Marlins": "MIA",
    "Nationals": "WSH",
    "Washington Nationals": "WSH",
    "Padres": "SD",
    "San Diego Padres": "SD",
    "Rockies": "COL",
    "Colorado Rockies": "COL",
    "Diamondbacks": "ARI",
    "Arizona Diamondbacks": "ARI",
}


@dataclass
class WeatherContext:
    """Weather conditions for a game"""
    temperature: float = 75.0
    wind_speed: float = 8.0
    wind_direction_factor: float = 0.5


def _normalize_team_name(team: str) -> str:
    """Normalize team name to standard abbreviation"""
    team = str(team).strip()
    return TEAM_ALIASES.get(team, team.upper())


def _safe_read_csv(path: Path) -> pd.DataFrame:
    """Safely read CSV file, return empty DataFrame if not found"""
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _safe_write_json(path: Path, payload: Dict[str, Any]) -> None:
    """Write JSON file with proper encoding"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _safe_rate(num, den):
    """Safely calculate rate, handling division by zero"""
    if isinstance(den, pd.Series):
        den = den.replace(0, np.nan)
    else:
        den = np.nan if den == 0 else den
    return num / den


# =============================================================================
# DATA INGESTION
# =============================================================================

def ingest_statcast(start_dt: str, end_dt: str, save: bool = True) -> pd.DataFrame:
    """
    Ingest Statcast data for a date range using pybaseball.
    
    Args:
        start_dt: Start date in YYYY-MM-DD format
        end_dt: End date in YYYY-MM-DD format
        save: Whether to save raw data to CSV
        
    Returns:
        DataFrame with Statcast data
    """
    if statcast is None:
        raise ImportError("pybaseball is not installed. Run: pip install pybaseball")
    
    print(f"Ingesting Statcast data from {start_dt} to {end_dt}...")
    df = statcast(start_dt=start_dt, end_dt=end_dt)
    
    if save and not df.empty:
        out_path = RAW_DIR / f"statcast_{start_dt}_to_{end_dt}.csv"
        df.to_csv(out_path, index=False)
        print(f"Saved {len(df)} rows to {out_path}")
    
    return df


def ingest_recent(days_back: int = 1, save: bool = True) -> pd.DataFrame:
    """
    Ingest Statcast data for the last N days.
    
    Args:
        days_back: Number of days to look back
        save: Whether to save raw data to CSV
        
    Returns:
        DataFrame with Statcast data
    """
    end = date.today()
    start = end - timedelta(days=days_back)
    return ingest_statcast(
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d"),
        save=save
    )


# =============================================================================
# FEATURE ENGINEERING
# =============================================================================

def engineer_pitcher_features(stat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer pitcher-level features from Statcast data.
    
    Features created:
    - pitches, strikeouts, walks, home runs, hits
    - k_rate, bb_rate, hr_per_100_pitches, hard_hit_rate
    - avg_velo, avg_launch_speed
    """
    df = stat_df.copy()
    
    if "pitcher" not in df.columns:
        print("Warning: 'pitcher' column not found in data")
        return pd.DataFrame()
    
    if "events" not in df.columns:
        df["events"] = ""
    
    grp = df.groupby(["game_pk", "pitcher"], dropna=False)
    
    out = grp.agg(
        pitches=("pitch_number", "count"),
        strikeouts=("events", lambda x: (x == "strikeout").sum()),
        walks=("events", lambda x: (x == "walk").sum()),
        home_runs=("events", lambda x: (x == "home_run").sum()),
        hits=("events", lambda x: x.isin(["single", "double", "triple", "home_run"]).sum()),
        hard_hit=("launch_speed", lambda x: (x >= 95).sum()),
        avg_velo=("release_speed", "mean"),
        avg_launch_speed=("launch_speed", "mean"),
    ).reset_index()
    
    out["k_rate"] = _safe_rate(out["strikeouts"], out["pitches"])
    out["bb_rate"] = _safe_rate(out["walks"], out["pitches"])
    out["hr_per_100_pitches"] = _safe_rate(out["home_runs"], out["pitches"]) * 100
    out["hard_hit_rate"] = _safe_rate(out["hard_hit"], out["pitches"])
    
    out.to_csv(FEAT_DIR / "pitcher_features.csv", index=False)
    print(f"Engineered pitcher features: {len(out)} rows")
    return out


def engineer_hitter_features(stat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer hitter-level features from Statcast data.
    
    Features created:
    - pa, hits, walks, strikeouts, home runs
    - obp_proxy, hr_rate, k_rate
    - avg_exit_velo, barrel_rate, hard_hit_rate
    """
    df = stat_df.copy()
    
    if "batter" not in df.columns:
        print("Warning: 'batter' column not found in data")
        return pd.DataFrame()
    
    if "events" not in df.columns:
        df["events"] = ""
    
    grp = df.groupby(["game_pk", "batter"], dropna=False)
    
    out = grp.agg(
        pa=("events", "count"),
        hits=("events", lambda x: x.isin(["single", "double", "triple", "home_run"]).sum()),
        walks=("events", lambda x: (x == "walk").sum()),
        strikeouts=("events", lambda x: (x == "strikeout").sum()),
        home_runs=("events", lambda x: (x == "home_run").sum()),
        avg_exit_velo=("launch_speed", "mean"),
        barrel_rate=("launch_speed", lambda x: (x >= 98).mean()),
        hard_hit_rate=("launch_speed", lambda x: (x >= 95).mean()),
    ).reset_index()
    
    out["obp_proxy"] = _safe_rate(out["hits"] + out["walks"], out["pa"])
    out["hr_rate"] = _safe_rate(out["home_runs"], out["pa"])
    out["k_rate"] = _safe_rate(out["strikeouts"], out["pa"])
    
    out.to_csv(FEAT_DIR / "hitter_features.csv", index=False)
    print(f"Engineered hitter features: {len(out)} rows")
    return out


def engineer_umpire_features(stat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer umpire-level features from Statcast data.
    
    Features created:
    - pitches, strikeouts, walks, runs
    - k_rate, bb_rate
    - avg_release_speed
    """
    df = stat_df.copy()
    
    if "umpire" not in df.columns:
        print("Warning: 'umpire' column not found in data")
        return pd.DataFrame()
    
    if "events" not in df.columns:
        df["events"] = ""
    
    grp = df.groupby(["game_pk", "umpire"], dropna=False)
    
    out = grp.agg(
        pitches=("pitch_number", "count"),
        strikeouts=("events", lambda x: (x == "strikeout").sum()),
        walks=("events", lambda x: (x == "walk").sum()),
        runs=("events", lambda x: x.isin(["single", "double", "triple", "home_run"]).sum()),
        avg_release_speed=("release_speed", "mean"),
    ).reset_index()
    
    out["k_rate"] = _safe_rate(out["strikeouts"], out["pitches"])
    out["bb_rate"] = _safe_rate(out["walks"], out["pitches"])
    
    out.to_csv(FEAT_DIR / "umpire_features.csv", index=False)
    print(f"Engineered umpire features: {len(out)} rows")
    return out


def engineer_team_game_features(stat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer team-level game features from Statcast data.
    
    Features created:
    - home_runs, away_runs, hits, walks, strikeouts
    - total_runs
    """
    df = stat_df.copy()
    
    needed = {"game_pk", "home_team", "away_team"}
    if not needed.issubset(df.columns):
        print("Warning: Required columns not found in data")
        return pd.DataFrame()
    
    if "events" not in df.columns:
        df["events"] = ""
    
    if "home_score" not in df.columns:
        df["home_score"] = np.nan
    if "away_score" not in df.columns:
        df["away_score"] = np.nan
    
    games = df.groupby(["game_pk", "home_team", "away_team"], dropna=False).agg(
        home_runs=("home_score", "max"),
        away_runs=("away_score", "max"),
        hits=("events", lambda x: x.isin(["single", "double", "triple", "home_run"]).sum()),
        walks=("events", lambda x: (x == "walk").sum()),
        strikeouts=("events", lambda x: (x == "strikeout").sum()),
    ).reset_index()
    
    # Normalize team names
    games["home_team"] = games["home_team"].map(_normalize_team_name)
    games["away_team"] = games["away_team"].map(_normalize_team_name)
    
    games["total_runs"] = games["home_runs"].fillna(0) + games["away_runs"].fillna(0)
    
    games.to_csv(FEAT_DIR / "games_full_features.csv", index=False)
    print(f"Engineered game features: {len(games)} rows")
    return games


# =============================================================================
# PROP PROJECTIONS
# =============================================================================

def project_k_prop(
    pitcher_stats: Dict[str, Any],
    opponent_stats: Dict[str, Any],
    umpire_stats: Optional[Dict[str, Any]],
    park_factor: float = 1.0
) -> Dict[str, Any]:
    """
    Project pitcher strikeout props.
    
    Args:
        pitcher_stats: Pitcher statistics including k_rate, handedness, innings_proj
        opponent_stats: Opponent statistics including k_rate_vs_L/R
        umpire_stats: Umpire statistics including k_rate
        park_factor: Park factor for strikeouts
        
    Returns:
        Dictionary with projection, edge, lean, and line
    """
    handedness = pitcher_stats.get("handedness", "R")
    opp_k = opponent_stats.get("k_rate_vs_R", opponent_stats.get("k_rate", 0.22))
    if handedness == "L":
        opp_k = opponent_stats.get("k_rate_vs_L", opp_k)
    
    pitcher_k = float(pitcher_stats.get("k_rate", 0.22))
    innings_proj = float(pitcher_stats.get("innings_proj", 5.5))
    line = float(pitcher_stats.get("prop_line", 5.5))
    
    ump_k = float(umpire_stats.get("k_rate", 0.23)) if umpire_stats else 0.23
    ump_adj = 1 + (ump_k - 0.23) * 1.5
    
    proj_ks = pitcher_k * opp_k * ump_adj * park_factor * innings_proj * 3.0
    
    return {
        "projection": round(proj_ks, 2),
        "edge": round(proj_ks - line, 2),
        "lean": "Over" if proj_ks > line else "Under",
        "line": line
    }


def project_hr_prop(
    hitter_stats: Dict[str, Any],
    pitcher_stats: Dict[str, Any],
    park_factor: float,
    weather: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Project home run probability for a hitter.
    
    Args:
        hitter_stats: Hitter statistics including hr_rate, barrel_rate, hard_hit_rate
        pitcher_stats: Pitcher statistics including hr_per_9, handedness
        park_factor: Park factor for home runs
        weather: Weather conditions including wind_speed, temperature, wind_direction_factor
        
    Returns:
        Dictionary with hr_probability and lean
    """
    pitcher_hand = pitcher_stats.get("handedness", "R")
    hr_split = hitter_stats.get("hr_rate_vs_R", hitter_stats.get("hr_rate", 0.03))
    if pitcher_hand == "L":
        hr_split = hitter_stats.get("hr_rate_vs_L", hr_split)
    
    barrel_rate = float(hitter_stats.get("barrel_rate", 0.05))
    hard_hit = float(hitter_stats.get("hard_hit_rate", 0.35))
    hr9 = float(pitcher_stats.get("hr_per_9", 1.0))
    
    wind = float(weather.get("wind_speed", 0))
    temp = float(weather.get("temperature", 70))
    wind_dir = float(weather.get("wind_direction_factor", 0.0))
    
    base = hr_split * 0.6 + barrel_rate * 0.25 + hard_hit * 0.15
    base *= (1 + (hr9 - 1.0) * 0.25)
    base *= park_factor
    base *= (1 + (wind * wind_dir * 0.03) + ((temp - 70) * 0.005))
    base = max(0.01, min(base, 0.50))
    
    return {
        "hr_probability": round(base, 3),
        "lean": "Yes HR" if base > 0.12 else "No HR"
    }


def project_total_bases(hitter_stats: Dict[str, Any]) -> Dict[str, Any]:
    """Project total bases for a hitter"""
    slg = float(hitter_stats.get("slg", 0.400))
    pa_proj = float(hitter_stats.get("pa_proj", 4.0))
    line = float(hitter_stats.get("prop_line", 1.5))
    
    proj = slg * pa_proj
    
    return {
        "player_name": hitter_stats.get("player_name", "Unknown"),
        "team": hitter_stats.get("team", "Unknown"),
        "prop_type": "Total Bases",
        "projection": round(proj, 2),
        "edge": round(proj - line, 2),
        "lean": "Over" if proj > line else "Under",
        "line": line
    }


def project_hits(hitter_stats: Dict[str, Any]) -> Dict[str, Any]:
    """Project hits for a hitter"""
    avg = float(hitter_stats.get("avg", 0.250))
    pa_proj = float(hitter_stats.get("pa_proj", 4.0))
    line = float(hitter_stats.get("prop_line", 0.5))
    
    proj = avg * pa_proj
    
    return {
        "player_name": hitter_stats.get("player_name", "Unknown"),
        "team": hitter_stats.get("team", "Unknown"),
        "prop_type": "Hits",
        "projection": round(proj, 2),
        "edge": round(proj - line, 2),
        "lean": "Over" if proj > line else "Under",
        "line": line
    }


def project_walks(
    hitter_stats: Dict[str, Any],
    pitcher_stats: Dict[str, Any]
) -> Dict[str, Any]:
    """Project walks for a hitter"""
    bb = (float(hitter_stats.get("bb_rate", 0.08)) + float(pitcher_stats.get("bb_rate_allowed", 0.08))) / 2
    pa_proj = float(hitter_stats.get("pa_proj", 4.0))
    line = float(hitter_stats.get("prop_line", 0.5))
    
    proj = bb * pa_proj
    
    return {
        "player_name": hitter_stats.get("player_name", "Unknown"),
        "team": hitter_stats.get("team", "Unknown"),
        "prop_type": "Walks",
        "projection": round(proj, 2),
        "edge": round(proj - line, 2),
        "lean": "Over" if proj > line else "Under",
        "line": line
    }


def project_rbis(
    hitter_stats: Dict[str, Any],
    lineup_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Project RBIs for a hitter"""
    hr_rate = float(hitter_stats.get("hr_rate", 0.03))
    avg = float(hitter_stats.get("avg", 0.250))
    runners = float(lineup_context.get("runners_on_base_rate", 0.32))
    pa_proj = float(lineup_context.get("pa_proj", 4.0))
    line = float(hitter_stats.get("prop_line", 0.5))
    
    proj = (hr_rate * 1.4 + avg * runners * 0.6) * pa_proj
    
    return {
        "player_name": hitter_stats.get("player_name", "Unknown"),
        "team": hitter_stats.get("team", "Unknown"),
        "prop_type": "RBIs",
        "projection": round(proj, 2),
        "edge": round(proj - line, 2),
        "lean": "Over" if proj > line else "Under",
        "line": line
    }


# =============================================================================
# FULL GAME MODEL
# =============================================================================

class MLBFullGameModel:
    """
    Full game prediction model for MLB games.
    Predicts total runs and run differential.
    """
    
    def __init__(self):
        self.total_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(
                n_estimators=300,
                max_depth=10,
                random_state=42
            ))
        ])
        self.side_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(
                n_estimators=300,
                max_depth=10,
                random_state=42
            ))
        ])
    
    def fit(self, df: pd.DataFrame) -> None:
        """
        Train the model on historical game data.
        
        Args:
            df: DataFrame with columns: hits, walks, strikeouts, total_runs, home_runs, away_runs
        """
        X = df[["hits", "walks", "strikeouts"]].copy()
        X = X.fillna(X.median(numeric_only=True))
        
        y_total = df["total_runs"].fillna(0)
        y_side = (df["home_runs"].fillna(0) - df["away_runs"].fillna(0))
        
        self.total_pipeline.fit(X, y_total)
        self.side_pipeline.fit(X, y_side)
    
    def predict(self, row: pd.Series) -> tuple:
        """
        Predict total runs and run differential for a game.
        
        Args:
            row: Series with columns: hits, walks, strikeouts
            
        Returns:
            Tuple of (total_pred, side_pred)
        """
        X = row[["hits", "walks", "strikeouts"]].to_frame().T
        total = float(self.total_pipeline.predict(X)[0])
        side = float(self.side_pipeline.predict(X)[0])
        return total, side


def save_model(model: MLBFullGameModel, path: Optional[Path] = None) -> Path:
    """Save model to disk"""
    model_path = path or (MODEL_DIR / "mlb_full_game_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    return model_path


def load_model(path: Optional[Path] = None) -> Optional[MLBFullGameModel]:
    """Load model from disk"""
    model_path = path or (MODEL_DIR / "mlb_full_game_model.pkl")
    if not model_path.exists():
        return None
    with open(model_path, "rb") as f:
        return pickle.load(f)


def build_model_and_save(force_retrain: bool = False) -> MLBFullGameModel:
    """Build and save the full game model"""
    existing = None if force_retrain else load_model()
    if existing is not None:
        return existing
    
    df = _safe_read_csv(FEAT_DIR / "games_full_features.csv")
    if df.empty:
        raise ValueError("games_full_features.csv is missing or empty")
    
    model = MLBFullGameModel()
    model.fit(df)
    save_model(model)
    return model


# =============================================================================
# MAIN PREDICTION FUNCTION
# =============================================================================

def predict_match(
    home_team: str,
    away_team: str,
    park_factor: float = 1.0,
    temperature: float = 75,
    wind_speed: float = 8,
    force_retrain: bool = False
) -> Dict[str, Any]:
    """
    Generate comprehensive predictions for an MLB matchup.
    
    Args:
        home_team: Home team name or abbreviation
        away_team: Away team name or abbreviation
        park_factor: Park factor for the venue
        temperature: Game temperature (°F)
        wind_speed: Wind speed (mph)
        force_retrain: Whether to force model retraining
        
    Returns:
        Dictionary with game projection, K props, HR props, and player props
    """
    home_team = _normalize_team_name(home_team)
    away_team = _normalize_team_name(away_team)
    
    # Load game data
    games = _safe_read_csv(FEAT_DIR / "games_full_features.csv")
    if games.empty:
        raise ValueError("games_full_features.csv is missing or empty. Run feature engineering first.")
    
    row = games[
        (games["home_team"] == home_team) &
        (games["away_team"] == away_team)
    ]
    
    if row.empty:
        raise ValueError(f"No MLB game found for {home_team} vs {away_team}")
    
    row = row.iloc[0]
    
    # Build/load model
    model = build_model_and_save(force_retrain=force_retrain)
    total_pred, side_pred = model.predict(row)
    
    # Load feature data for props
    pitchers = _safe_read_csv(FEAT_DIR / "pitcher_features.csv")
    hitters = _safe_read_csv(FEAT_DIR / "hitter_features.csv")
    umpires = _safe_read_csv(FEAT_DIR / "umpire_features.csv")
    
    # Get default stats (or filter by team in a real implementation)
    home_pitcher = pitchers.iloc[0].to_dict() if not pitchers.empty else {
        "k_rate": 0.22, "hr_per_9": 1.0, "handedness": "R", "innings_proj": 5.5
    }
    away_pitcher = pitchers.iloc[0].to_dict() if not pitchers.empty else {
        "k_rate": 0.22, "hr_per_9": 1.0, "handedness": "L", "innings_proj": 5.5
    }
    home_hitter = hitters.iloc[0].to_dict() if not hitters.empty else {
        "avg": 0.250, "slg": 0.400, "hr_rate": 0.03, "barrel_rate": 0.05, "hard_hit_rate": 0.35
    }
    away_hitter = hitters.iloc[0].to_dict() if not hitters.empty else {
        "avg": 0.250, "slg": 0.400, "hr_rate": 0.03, "barrel_rate": 0.05, "hard_hit_rate": 0.35
    }
    ump = umpires.iloc[0].to_dict() if not umpires.empty else None
    
    weather = {
        "temperature": temperature,
        "wind_speed": wind_speed,
        "wind_direction_factor": 0.5
    }
    
    # Generate prop projections
    result = {
        "game": {
            "home_team": home_team,
            "away_team": away_team,
            "projected_total_runs": round(total_pred, 2),
            "projected_run_diff_home_minus_away": round(side_pred, 2),
        },
        "k_props": {
            "home": project_k_prop(home_pitcher, away_hitter, ump, park_factor),
            "away": project_k_prop(away_pitcher, home_hitter, ump, park_factor),
        },
        "hr_props": {
            "home": project_hr_prop(home_hitter, away_pitcher, park_factor, weather),
            "away": project_hr_prop(away_hitter, home_pitcher, park_factor, weather),
        },
        "player_props": {
            "home": [
                project_total_bases({
                    "player_name": f"{home_team} Slugger",
                    "team": home_team,
                    "avg": 0.280,
                    "slg": 0.480,
                    "pa_proj": 4.0,
                    "prop_line": 1.5
                }),
                project_hits({
                    "player_name": f"{home_team} Hitter",
                    "team": home_team,
                    "avg": 0.280,
                    "pa_proj": 4.0,
                    "prop_line": 0.5
                })
            ],
            "away": [
                project_total_bases({
                    "player_name": f"{away_team} Slugger",
                    "team": away_team,
                    "avg": 0.260,
                    "slg": 0.430,
                    "pa_proj": 4.0,
                    "prop_line": 1.5
                }),
                project_hits({
                    "player_name": f"{away_team} Hitter",
                    "team": away_team,
                    "avg": 0.260,
                    "pa_proj": 4.0,
                    "prop_line": 0.5
                })
            ]
        }
    }
    
    # Save results
    out = OUT_DIR / f"{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
    _safe_write_json(out, result)
    print(f"Saved prediction to: {out}")
    
    return result