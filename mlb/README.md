# MLB Module

This folder contains the MLB module for MultiSportPredict.

## What It Does

- **Data Ingestion**: Pulls Statcast data using the `pybaseball` library
- **Feature Engineering**: Builds pitcher, hitter, umpire, and game-level feature files
- **Full Game Model**: Trains a Random Forest model to predict total runs and run differential
- **Prop Projections**: Generates projections for K props, HR props, total bases, hits, walks, and RBIs
- **Matchup Predictions**: Produces comprehensive game projections and prop outputs

## Main Files

- `mlb_module.py` - Core module with all functions and the model class
- `__init__.py` - Package exports for easy importing

## Installation

Make sure you have the required packages:

```bash
pip install pybaseball pandas numpy scikit-learn
```

## Example Workflow

### Step 1: Ingest Data

```python
from mlb import ingest_recent

# Pull data from the last 3 days
df = ingest_recent(days_back=3)
```

Or specify exact dates:

```python
from mlb import ingest_statcast

df = ingest_statcast("2026-06-04", "2026-06-06")
```

### Step 2: Build Features

```python
from mlb import (
    engineer_pitcher_features,
    engineer_hitter_features,
    engineer_umpire_features,
    engineer_team_game_features,
)

# Engineer all feature sets from the raw Statcast data
engineer_pitcher_features(df)
engineer_hitter_features(df)
engineer_umpire_features(df)
engineer_team_game_features(df)
```

### Step 3: Predict a Matchup

```python
from mlb import predict_match

# Predict Yankees vs Red Sox
result = predict_match("NYY", "BOS")
print(result)
```

### Step 4: Use the Unified CLI

From the repo root:

```bash
python predict_match.py baseball "Yankees" "Red Sox"
```

## Directory Structure

```
mlb/
├── __init__.py          # Package exports
├── mlb_module.py        # Core module
└── README.md            # This file

data/mlb/
├── raw/                 # Raw Statcast CSV files
├── features/            # Engineered feature files
│   ├── pitcher_features.csv
│   ├── hitter_features.csv
│   ├── umpire_features.csv
│   └── games_full_features.csv
└── models/              # Trained model files
    └── mlb_full_game_model.pkl

output/mlb/              # Prediction output files
```

## Feature Descriptions

### Pitcher Features
- `pitches`, `strikeouts`, `walks`, `home_runs`, `hits`
- `k_rate`, `bb_rate`, `hr_per_100_pitches`, `hard_hit_rate`
- `avg_velo`, `avg_launch_speed`

### Hitter Features
- `pa`, `hits`, `walks`, `strikeouts`, `home_runs`
- `obp_proxy`, `hr_rate`, `k_rate`
- `avg_exit_velo`, `barrel_rate`, `hard_hit_rate`

### Umpire Features
- `pitches`, `strikeouts`, `walks`, `runs`
- `k_rate`, `bb_rate`, `avg_release_speed`

### Game Features
- `home_runs`, `away_runs`, `hits`, `walks`, `strikeouts`
- `total_runs`

## Prop Projection Methods

### Strikeout Props (`project_k_prop`)
Projects pitcher strikeouts based on:
- Pitcher K rate × Opponent K rate
- Umpire adjustment (some umps have tighter zones)
- Park factor
- Innings projection

### Home Run Props (`project_hr_prop`)
Projects HR probability based on:
- Hitter HR rate vs pitcher handedness
- Barrel rate and hard hit rate
- Pitcher HR/9 allowed
- Park factor and weather (wind, temperature)

### Player Props
- **Total Bases**: SLG × projected PA
- **Hits**: AVG × projected PA
- **Walks**: (Hitter BB rate + Pitcher BB rate) / 2 × projected PA
- **RBIs**: (HR rate × 1.4 + AVG × runners on base rate × 0.6) × projected PA

## 2026 Season Notes

The 2026 MLB season features the new Automated Ball-Strike (ABS) Challenge System, which has resulted in a tighter strike zone (53.5% at top, 27% at bottom of zone). This affects:
- Umpire tendencies (some umps call more strikes)
- Overall run environment (9.4 runs/game average)
- Strikeout and walk rates

## Team Abbreviations

The module supports both full team names and abbreviations:

| Full Name | Abbreviation |
|-----------|--------------|
| New York Yankees | NYY |
| Boston Red Sox | BOS |
| Los Angeles Dodgers | LAD |
| ... | ... |

See `TEAM_ALIASES` in `mlb_module.py` for the complete list.