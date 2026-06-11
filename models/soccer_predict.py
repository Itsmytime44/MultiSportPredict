# predict/soccer_predict.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import pandas as pd
from models.soccer_model import SoccerModel
from models.soccer_league_config import (
    LeagueDetector,
    get_league_config_for_match,
    add_league_detection_to_df,
)


def run_soccer_game(
    home_team: str,
    away_team: str,
    league: Optional[str] = None,
    features_path: str = "data/processed/soccer_features.csv"
):
    """
    Run soccer prediction with automatic league detection and tuning.
    
    Args:
        home_team: Home team name
        away_team: Away team name
        league: Optional league key (auto-detected if not provided)
        features_path: Path to features CSV
    """
    path = Path(features_path)
    if not path.exists():
        raise FileNotFoundError(f"Missing feature file: {path}")

    df = pd.read_csv(path)
    
    # Auto-detect league if not provided
    if not league:
        # Try to detect from existing data
        test_row = pd.Series({"home_team": home_team})
        detected = LeagueDetector.detect_from_row(test_row)
        league = detected if detected else "unknown"
    
    # Add league column for context
    if "league" not in df.columns:
        df = add_league_detection_to_df(df)
    
    # Find the match (case-insensitive)
    row = df[
        (df["home_team"].str.lower() == home_team.lower()) &
        (df["away_team"].str.lower() == away_team.lower())
    ]
    
    if row.empty:
        raise ValueError(f"No soccer game found for {home_team} vs {away_team}")

    row = row.iloc[0]
    
    # Create league-aware model
    model = SoccerModel(league=league)
    model.fit(df, target_col="total_goals")

    result = {
        "sport": "soccer",
        "home_team": home_team,
        "away_team": away_team,
        "league": league,
        "model": model.predict(row),
    }

    out = Path("output/soccer")
    out.mkdir(parents=True, exist_ok=True)
    file_path = out / f"{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(result)
    return result