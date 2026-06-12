# predict/basketball_predict.py
# This file is moved from ingest/ to predict/
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from models.basketball_model import BasketballModel

def run_basketball_game(home_team: str, away_team: str):
    path = Path("data/processed/basketball_features.csv")
    if not path.exists():
        raise FileNotFoundError(f"Missing feature file: {path}")

    df = pd.read_csv(path)
    row = df[(df["home_team"] == home_team) & (df["away_team"] == away_team)]
    if row.empty:
        raise ValueError(f"No basketball game found for {home_team} vs {away_team}")

    row = row.iloc[0]
    model = BasketballModel()
    model.fit(df, target_col="total_points")

    result = {
        "sport": "basketball",
        "home_team": home_team,
        "away_team": away_team,
        "model": model.predict(row),
    }

    out = Path("output/basketball")
    out.mkdir(parents=True, exist_ok=True)
    file_path = out / f"{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(result)
    return result