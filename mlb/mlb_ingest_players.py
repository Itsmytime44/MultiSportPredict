"""
MLB Player Stats Ingestion Module
==================================
Automatic ingestion of player statistics from Statcast via pybaseball.

Features:
- Fetch hitter stats from Statcast
- Fetch pitcher stats from Statcast
- Save raw data for feature engineering
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

try:
    from pybaseball import statcast_batter, statcast_pitcher
except ImportError:
    statcast_batter = None
    statcast_pitcher = None

# Directory configuration
DATA_DIR = Path("data/mlb")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def ingest_player_stats(
    player_ids: List[str],
    start_date: str,
    end_date: str,
    save: bool = True
) -> tuple:
    """
    Ingest player statistics from Statcast for a date range.
    
    Args:
        player_ids: List of player IDs to fetch
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        save: Whether to save raw data to CSV
        
    Returns:
        Tuple of (hitters_df, pitchers_df)
    """
    if statcast_batter is None or statcast_pitcher is None:
        raise ImportError("pybaseball is not installed. Run: pip install pybaseball")
    
    hitters = []
    pitchers = []
    
    print(f"Ingesting player stats from {start_date} to {end_date}...")
    
    for pid in player_ids:
        try:
            # Fetch hitter stats
            h = statcast_batter(start_date, end_date, pid)
            if h is not None and not h.empty:
                h['player_id'] = pid
                hitters.append(h)
        except Exception as e:
            print(f"  Warning: Could not fetch hitter stats for {pid}: {e}")
        
        try:
            # Fetch pitcher stats
            p = statcast_pitcher(start_date, end_date, pid)
            if p is not None and not p.empty:
                p['player_id'] = pid
                pitchers.append(p)
        except Exception as e:
            print(f"  Warning: Could not fetch pitcher stats for {pid}: {e}")
    
    # Combine DataFrames
    hitters_df = pd.concat(hitters, ignore_index=True) if hitters else pd.DataFrame()
    pitchers_df = pd.concat(pitchers, ignore_index=True) if pitchers else pd.DataFrame()
    
    if save:
        if not hitters_df.empty:
            hitters_df.to_csv(DATA_DIR / "hitters_raw.csv", index=False)
            print(f"  Saved {len(hitters_df)} hitter rows")
        if not pitchers_df.empty:
            pitchers_df.to_csv(DATA_DIR / "pitchers_raw.csv", index=False)
            print(f"  Saved {len(pitchers_df)} pitcher rows")
    
    return hitters_df, pitchers_df


def ingest_recent_players(
    days_back: int = 7,
    save: bool = True
) -> tuple:
    """
    Ingest player statistics for the last N days.
    
    Args:
        days_back: Number of days to look back
        save: Whether to save raw data to CSV
        
    Returns:
        Tuple of (hitters_df, pitchers_df)
    """
    end = datetime.now()
    start = end - timedelta(days=days_back)
    return ingest_player_stats(
        player_ids=[],  # Would need player IDs
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end.strftime("%Y-%m-%d"),
        save=save
    )


def get_team_players(team_abbreviation: str) -> List[str]:
    """
    Get list of player IDs for a team.
    This is a placeholder - in production, you'd fetch from a roster API.
    
    Args:
        team_abbreviation: Team abbreviation (e.g., "NYY", "LAD")
        
    Returns:
        List of player IDs
    """
    # Placeholder - would need to be populated with real roster data
    # Could use pybaseball.lahman or Fangraphs API
    team_rosters = {
        "NYY": [],  # Yankees
        "BOS": [],  # Red Sox
        "LAD": [],  # Dodgers
        "SD": [],   # Padres
        "NYM": [],  # Mets
        # Add more teams...
    }
    return team_rosters.get(team_abbreviation, [])