"""
MLB Park Factors Module
========================
Manages park factor data for MLB stadiums.

Park factors adjust player projections based on stadium characteristics:
- Run factor: How the park affects overall scoring
- HR factor: How the park affects home run rates
- Dimensions and altitude considerations
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict

# Directory configuration
DATA_DIR = Path("data/mlb")
DATA_DIR.mkdir(parents=True, exist_ok=True)


# Static park factors (would ideally be updated seasonally)
# Source: FanGraphs / Baseball Savant park factors (scaled where 100 = average)
PARK_FACTORS = [
    {"stadium": "PETCO Park", "team": "SD", "run_factor": 0.95, "hr_factor": 0.90, "dimensions": "Large"},
    {"stadium": "Citi Field", "team": "NYM", "run_factor": 0.98, "hr_factor": 0.92, "dimensions": "Large"},
    {"stadium": "T-Mobile Park", "team": "SEA", "run_factor": 0.97, "hr_factor": 0.95, "dimensions": "Large"},
    {"stadium": "Oracle Park", "team": "SF", "run_factor": 0.96, "hr_factor": 0.88, "dimensions": "Large"},
    {"stadium": "Dodger Stadium", "team": "LAD", "run_factor": 0.99, "hr_factor": 0.95, "dimensions": "Neutral"},
    {"stadium": "Yankee Stadium", "team": "NYY", "run_factor": 1.02, "hr_factor": 1.15, "dimensions": "Small RF"},
    {"stadium": "Fenway Park", "team": "BOS", "run_factor": 1.03, "hr_factor": 1.08, "dimensions": "Unique"},
    {"stadium": "Coors Field", "team": "COL", "run_factor": 1.18, "hr_factor": 1.05, "dimensions": "High Altitude"},
    {"stadium": "Great American Ball Park", "team": "CIN", "run_factor": 1.05, "hr_factor": 1.12, "dimensions": "Small"},
    {"stadium": "Busch Stadium", "team": "STL", "run_factor": 1.00, "hr_factor": 0.98, "dimensions": "Neutral"},
    {"stadium": "Wrigley Field", "team": "CHC", "run_factor": 1.01, "hr_factor": 1.03, "dimensions": "Neutral"},
    {"stadium": "Guaranteed Rate Field", "team": "CWS", "run_factor": 1.02, "hr_factor": 1.06, "dimensions": "Neutral"},
    {"stadium": "Progressive Field", "team": "CLE", "run_factor": 0.98, "hr_factor": 0.95, "dimensions": "Neutral"},
    {"stadium": "Comerica Park", "team": "DET", "run_factor": 0.97, "hr_factor": 0.93, "dimensions": "Large"},
    {"stadium": "Kauffman Stadium", "team": "KC", "run_factor": 1.00, "hr_factor": 1.02, "dimensions": "Neutral"},
    {"stadium": "Target Field", "team": "MIN", "run_factor": 0.99, "hr_factor": 0.97, "dimensions": "Neutral"},
    {"stadium": "Globe Life Field", "team": "TEX", "run_factor": 1.01, "hr_factor": 1.04, "dimensions": "Neutral"},
    {"stadium": "Minute Maid Park", "team": "HOU", "run_factor": 1.02, "hr_factor": 1.08, "dimensions": "Neutral"},
    {"stadium": "Angel Stadium", "team": "LAA", "run_factor": 1.00, "hr_factor": 0.98, "dimensions": "Neutral"},
    {"stadium": "Oakland Coliseum", "team": "OAK", "run_factor": 0.96, "hr_factor": 0.90, "dimensions": "Large"},
    {"stadium": "Tropicana Field", "team": "TB", "run_factor": 0.97, "hr_factor": 0.94, "dimensions": "Dome"},
    {"stadium": "Rogers Centre", "team": "TOR", "run_factor": 1.01, "hr_factor": 1.05, "dimensions": "Dome"},
    {"stadium": "Oriole Park at Camden Yards", "team": "BAL", "run_factor": 1.02, "hr_factor": 1.08, "dimensions": "Neutral"},
    {"stadium": "Nationals Park", "team": "WSH", "run_factor": 1.00, "hr_factor": 0.98, "dimensions": "Neutral"},
    {"stadium": "Truist Park", "team": "ATL", "run_factor": 1.01, "hr_factor": 1.03, "dimensions": "Neutral"},
    {"stadium": "loanDepot park", "team": "MIA", "run_factor": 0.98, "hr_factor": 0.95, "dimensions": "Dome"},
    {"stadium": "Citizens Bank Park", "team": "PHI", "run_factor": 1.04, "hr_factor": 1.10, "dimensions": "Small"},
    {"stadium": "PNC Park", "team": "PIT", "run_factor": 0.97, "hr_factor": 0.92, "dimensions": "Large"},
    {"stadium": "American Family Field", "team": "MIL", "run_factor": 1.00, "hr_factor": 1.02, "dimensions": "Neutral"},
    {"stadium": "Chase Field", "team": "ARI", "run_factor": 1.03, "hr_factor": 1.06, "dimensions": "Dome"},
]


def load_static_park_factors(save: bool = True) -> pd.DataFrame:
    """
    Load and optionally save static park factors.
    
    Args:
        save: Whether to save to CSV
        
    Returns:
        DataFrame with park factors
    """
    df = pd.DataFrame(PARK_FACTORS)
    
    if save:
        out_path = DATA_DIR / "park_factors.csv"
        df.to_csv(out_path, index=False)
        print(f"Saved park factors for {len(df)} stadiums to {out_path}")
    
    return df


def get_park_factor(
    team: str,
    factor_type: str = "run_factor"
) -> float:
    """
    Get park factor for a team.
    
    Args:
        team: Team abbreviation
        factor_type: Type of factor ("run_factor" or "hr_factor")
        
    Returns:
        Park factor value (1.0 = average, >1.0 = hitter friendly, <1.0 = pitcher friendly)
    """
    path = DATA_DIR / "park_factors.csv"
    if path.exists():
        df = pd.read_csv(path)
    else:
        df = pd.DataFrame(PARK_FACTORS)
    
    matching = df[df["team"] == team]
    if matching.empty:
        return 1.0  # Default to neutral
    
    return float(matching.iloc[0][factor_type])


def get_stadium_info(
    team: str
) -> Optional[Dict]:
    """
    Get full stadium information for a team.
    
    Args:
        team: Team abbreviation
        
    Returns:
        Dictionary with stadium info or None
    """
    path = DATA_DIR / "park_factors.csv"
    if path.exists():
        df = pd.read_csv(path)
    else:
        df = pd.DataFrame(PARK_FACTORS)
    
    matching = df[df["team"] == team]
    if matching.empty:
        return None
    
    row = matching.iloc[0]
    return {
        "stadium": row["stadium"],
        "team": row["team"],
        "run_factor": float(row["run_factor"]),
        "hr_factor": float(row["hr_factor"]),
        "dimensions": row.get("dimensions", "Neutral")
    }