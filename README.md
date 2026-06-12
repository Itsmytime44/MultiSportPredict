# MultiSportPredict

A comprehensive machine learning platform for predicting outcomes across multiple sports.

## Overview

MultiSportPredict provides:
- **Basketball**: Game predictions (spread, totals)
- **Soccer**: Match outcome, goals predictions
- **KBO**: Game predictions (totals)

## Quick Start

### Installation

```bash
pip install -r MultiSportPredict/requirements.txt
```

### Unified CLI

Predict any sport with a single command:

```bash
# Basketball
python predict_match.py basketball "UCAM Murcia" "FC Barcelona"

# Soccer
python predict_match.py soccer "Liverpool" "Aston Villa"

# Baseball/MLB
python predict_match.py baseball "Yankees" "Red Sox"
python predict_match.py mlb "LAD" "SF"
```

## Project Structure

```
MultiSportPredict/
├── basketball/              # Basketball prediction module
│   ├── __init__.py
│   └── basketball_predict_game.py
├── soccer/                  # Soccer prediction module
│   ├── __init__.py
│   └── soccer_predict_game.py
├── mlb/                     # MLB prediction module (NEW!)
│   ├── __init__.py
│   ├── mlb_module.py        # Core MLB functionality
│   └── README.md
├── data/
│   ├── mlb/
│   │   ├── raw/             # Raw Statcast data
│   │   ├── features/        # Engineered features
│   │   └── models/          # Trained models
│   └── (other sports data)
├── output/                  # Prediction results
├── MultiSportModel.py       # Core modeling engine
├── predict_match.py         # Unified CLI
├── requirements.txt
└── README.md
```

## MLB Module

The MLB module provides comprehensive baseball predictions using Statcast data.

### Features

- **Data Ingestion**: Automatic Statcast data pulling via pybaseball
- **Feature Engineering**: Pitcher, hitter, umpire, and game-level features
- **Full Game Model**: Random Forest for total runs and run differential
- **Prop Projections**: K props, HR props, total bases, hits, walks, RBIs

### MLB Workflow

```python
from mlb import (
    ingest_recent,
    engineer_pitcher_features,
    engineer_hitter_features,
    engineer_umpire_features,
    engineer_team_game_features,
    predict_match,
)

# Step 1: Ingest recent data
df = ingest_recent(days_back=3)

# Step 2: Build features
engineer_pitcher_features(df)
engineer_hitter_features(df)
engineer_umpire_features(df)
engineer_team_game_features(df)

# Step 3: Predict a matchup
result = predict_match("NYY", "BOS")
print(result)
```

### MLB Prop Projections

The module supports various player prop projections:

- **Strikeout Props**: Based on pitcher K rate, opponent K rate, umpire tendencies, park factor
- **Home Run Props**: Based on barrel rate, hard hit%, pitcher HR/9, weather, park factor
- **Total Bases**: SLG × projected PA
- **Hits**: AVG × projected PA
- **Walks**: (Hitter BB rate + Pitcher BB rate) / 2 × projected PA
- **RBIs**: Based on HR rate, AVG, and lineup context

See `mlb/README.md` for detailed documentation.

## Historical Storage & Analysis

All predictions are automatically stored in a SQLite database (`multisport_history.db`) for tracking and analysis.

### Querying Historical Predictions

```python
from core import get_predictions, get_prediction_summary, export_predictions_to_json

# Get all basketball predictions
bball_preds = get_predictions(sport="basketball")

# Get predictions for a specific team
team_preds = get_predictions(home_team="FC Barcelona")

# Get predictions by date range
recent_preds = get_predictions(
    start_date="2026-06-01",
    end_date="2026-06-30"
)

# Get summary statistics
summary = get_prediction_summary()
print(f"Total predictions: {summary['total_predictions']}")
print(f"Average confidence: {summary['avg_confidence']}%")

# Export to JSON
export_predictions_to_json("output/all_predictions.json")
```

### Database Schema

The predictions table includes:
- `id`: Unique identifier
- `sport`: Sport type (basketball, soccer, mlb)
- `home_team`, `away_team`: Team names
- `market_type`: Type of market (spread, total, moneyline, props)
- `model_value`: Model's projected value
- `market_value`: Market line/value
- `edge`: Difference between model and market
- `confidence`: Confidence score (0-100)
- `recommendation`: Bet recommendation (STRONG BET, BET, PASS)
- `timestamp`: When the prediction was made
- `raw_json`: Full prediction result
- `result_outcome`: Actual outcome (win, loss, push)
- `profit_loss`: P&L tracking

## Basketball Module

Provides EuroLeague/NBA predictions with:
- Full game spread and totals
- First quarter (Q1) projections
- First half (1H) projections
- Moneyline probabilities
- Player prop projections

### Enhanced Features
- **Referee Data Integration**: Crew foul rates, home bias, pace adjustments
- **Consensus Signals**: Public betting percentages, sharp money alignment
- **Confidence Scoring**: Sport-specific volatility with market alignment

## Soccer Module

Provides soccer predictions with:
- Match outcome (1X2)
- Goals over/under
- Both teams to score (BTTS)
- Corner totals
- Expected goals (xG) modeling

### Enhanced Features
- **Referee Data Integration**: Card tendencies, penalty rates, strictness ratings
- **Penalty Adjustments**: Expected goals adjusted for referee penalty tendencies
- **Confidence Scoring**: Sport-specific volatility for soccer markets

## Requirements

- Python 3.8+
- pandas
- numpy
- scikit-learn
- requests
- matplotlib
- pybaseball (for MLB)

## 2026 Season Notes

### MLB
The 2026 MLB season features the new Automated Ball-Strike (ABS) Challenge System, resulting in:
- Tighter strike zone (53.5% at top, 27% at bottom)
- Average of 9.4 runs per game
- Specific umpire tendencies affecting Over/Under trends

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License