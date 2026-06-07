"""
MLB Player Feature Engineering Module
======================================
Converts raw Statcast data into prop-ready metrics for hitters and pitchers.

Features Created:
Hitters: AVG, SLG, HR rate, BB rate, barrel rate, hard hit rate, PA projection
Pitchers: K rate, BB rate allowed, HR/9, hard hit allowed, innings projection
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Directory configuration
DATA_DIR = Path("data/mlb")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def build_hitter_features(
    input_path: Path = None,
    output_path: Path = None
) -> pd.DataFrame:
    """
    Build hitter features from raw Statcast data.
    
    Features created:
    - player_name, team, player_id
    - avg_exit_velo, hard_hit_rate, barrel_rate
    - avg (batting average proxy), slg (ISO proxy)
    - hr_rate, bb_rate
    - pa (plate appearances), pa_proj (projected PA)
    
    Args:
        input_path: Path to raw hitters CSV
        output_path: Path to save features CSV
        
    Returns:
        DataFrame with hitter features
    """
    input_path = input_path or (DATA_DIR / "hitters_raw.csv")
    output_path = output_path or (DATA_DIR / "hitter_features.csv")
    
    if not input_path.exists():
        print(f"Warning: {input_path} not found. Cannot build hitter features.")
        return pd.DataFrame()
    
    df = pd.read_csv(input_path)
    
    if df.empty:
        print("Warning: Hitters raw data is empty.")
        return pd.DataFrame()
    
    # Required columns check
    required = {"player_id"}
    if not required.issubset(df.columns):
        print(f"Warning: Required columns {required} not found in data")
        return pd.DataFrame()
    
    # Group by player and aggregate features
    grouped = df.groupby("player_id").agg(
        player_name=("player_name", "first"),
        team=("team", "first"),
        
        # Exit velocity metrics
        avg_exit_velo=("launch_speed", "mean"),
        hard_hit_rate=("launch_speed", lambda x: (x >= 95).mean() if x.notna().any() else 0.0),
        
        # Quality of contact
        barrel_rate=("barrel", "mean") if "barrel" in df.columns else ("launch_speed", lambda x: (x >= 98).mean()),
        
        # Rate stats
        avg=("events", lambda x: (x.isin(["single", "double", "triple", "home_run"])).sum() / len(x) if len(x) > 0 else 0.0),
        
        # Power metrics
        slg=("estimated_woba_using_speedangle", "mean") if "estimated_woba_using_speedangle" in df.columns else ("launch_speed", "mean"),
        hr_rate=("events", lambda x: (x == "home_run").mean() if len(x) > 0 else 0.0),
        
        # Plate discipline
        bb_rate=("events", lambda x: (x == "walk").mean() if len(x) > 0 else 0.0),
        
        # Volume
        pa=("events", "count"),
    ).reset_index()
    
    # Calculate projected PA (rough estimate based on recent performance)
    grouped["pa_proj"] = grouped["pa"] / 10.0  # Rough daily projection
    grouped["pa_proj"] = grouped["pa_proj"].clip(lower=2.0, upper=6.0)
    
    # Fill NaN values
    numeric_cols = grouped.select_dtypes(include=[np.number]).columns
    grouped[numeric_cols] = grouped[numeric_cols].fillna(0.0)
    
    # Save to CSV
    grouped.to_csv(output_path, index=False)
    print(f"Built hitter features: {len(grouped)} players saved to {output_path}")
    
    return grouped


def build_pitcher_features(
    input_path: Path = None,
    output_path: Path = None
) -> pd.DataFrame:
    """
    Build pitcher features from raw Statcast data.
    
    Features created:
    - player_name, team, player_id
    - k_rate, bb_rate_allowed, hr_per_9
    - hard_hit_allowed, innings_proj
    
    Args:
        input_path: Path to raw pitchers CSV
        output_path: Path to save features CSV
        
    Returns:
        DataFrame with pitcher features
    """
    input_path = input_path or (DATA_DIR / "pitchers_raw.csv")
    output_path = output_path or (DATA_DIR / "pitcher_features.csv")
    
    if not input_path.exists():
        print(f"Warning: {input_path} not found. Cannot build pitcher features.")
        return pd.DataFrame()
    
    df = pd.read_csv(input_path)
    
    if df.empty:
        print("Warning: Pitchers raw data is empty.")
        return pd.DataFrame()
    
    # Required columns check
    required = {"player_id"}
    if not required.issubset(df.columns):
        print(f"Warning: Required columns {required} not found in data")
        return pd.DataFrame()
    
    # Group by player and aggregate features
    grouped = df.groupby("player_id").agg(
        player_name=("player_name", "first"),
        team=("team", "first"),
        
        # Rate stats
        k_rate=("events", lambda x: (x == "strikeout").mean() if len(x) > 0 else 0.0),
        bb_rate_allowed=("events", lambda x: (x == "walk").mean() if len(x) > 0 else 0.0),
        
        # Home run rate (per 9 innings equivalent)
        hr_per_9=("events", lambda x: (x == "home_run").sum() * 9 / len(x) if len(x) > 0 else 0.0),
        
        # Contact quality allowed
        hard_hit_allowed=("launch_speed", lambda x: (x >= 95).mean() if x.notna().any() else 0.0),
        
        # Volume
        total_batters_faced=("events", "count"),
    ).reset_index()
    
    # Calculate projected innings (rough estimate)
    # Assume ~3 batters per inning, cap between 4 and 7
    grouped["innings_proj"] = grouped["total_batters_faced"] / 3.0
    grouped["innings_proj"] = grouped["innings_proj"].clip(lower=4.0, upper=7.0)
    
    # Fill NaN values
    numeric_cols = grouped.select_dtypes(include=[np.number]).columns
    grouped[numeric_cols] = grouped[numeric_cols].fillna(0.0)
    
    # Save to CSV
    grouped.to_csv(output_path, index=False)
    print(f"Built pitcher features: {len(grouped)} players saved to {output_path}")
    
    return grouped


def load_hitter_features(team_filter: str = None) -> pd.DataFrame:
    """Load hitter features, optionally filtered by team."""
    path = DATA_DIR / "hitter_features.csv"
    if not path.exists():
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    if team_filter:
        df = df[df["team"] == team_filter]
    return df


def load_pitcher_features(team_filter: str = None) -> pd.DataFrame:
    """Load pitcher features, optionally filtered by team."""
    path = DATA_DIR / "pitcher_features.csv"
    if not path.exists():
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    if team_filter:
        df = df[df["team"] == team_filter]
    return df