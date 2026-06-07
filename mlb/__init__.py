"""
MLB Module for MultiSportPredict
=================================
Comprehensive MLB prediction module with:
- Statcast data ingestion via pybaseball
- Feature engineering for pitchers, hitters, umpires, and game contexts
- Full game prediction model (totals + sides)
- Player prop projections (K, HR, TB, Hits, Walks, RBIs)
- Automatic daily ingestion pipeline
- Sportsbook lines, weather, and park factor integration
- Confidence scoring and bet recommendations
"""

# Core prediction functions (from mlb_module.py)
from mlb.mlb_module import (
    ingest_statcast,
    ingest_recent,
    engineer_pitcher_features,
    engineer_hitter_features,
    engineer_umpire_features,
    engineer_team_game_features,
    project_k_prop,
    project_hr_prop,
    project_total_bases,
    project_hits,
    project_walks,
    project_rbis,
    MLBFullGameModel,
    save_model,
    load_model,
    build_model_and_save,
    predict_match,
)

# Player ingestion and features
from mlb.mlb_ingest_players import (
    ingest_player_stats,
    ingest_recent_players,
    get_team_players,
)

from mlb.mlb_player_features import (
    build_hitter_features,
    build_pitcher_features,
    load_hitter_features,
    load_pitcher_features,
)

# External data ingestion
from mlb.mlb_sportsbook import (
    fetch_sportsbook_lines,
    load_sportsbook_lines,
    get_player_line,
)

from mlb.mlb_weather import (
    fetch_weather_for_games,
    load_weather_data,
    get_game_weather,
)

from mlb.mlb_park_factors import (
    load_static_park_factors,
    get_park_factor,
    get_stadium_info,
)

# Daily pipeline
from mlb.mlb_daily_pipeline import (
    run_daily_mlb_pipeline,
)

__all__ = [
    # Core prediction
    "ingest_statcast",
    "ingest_recent",
    "engineer_pitcher_features",
    "engineer_hitter_features",
    "engineer_umpire_features",
    "engineer_team_game_features",
    "project_k_prop",
    "project_hr_prop",
    "project_total_bases",
    "project_hits",
    "project_walks",
    "project_rbis",
    "MLBFullGameModel",
    "save_model",
    "load_model",
    "build_model_and_save",
    "predict_match",
    
    # Player ingestion
    "ingest_player_stats",
    "ingest_recent_players",
    "get_team_players",
    "build_hitter_features",
    "build_pitcher_features",
    "load_hitter_features",
    "load_pitcher_features",
    
    # External data
    "fetch_sportsbook_lines",
    "load_sportsbook_lines",
    "get_player_line",
    "fetch_weather_for_games",
    "load_weather_data",
    "get_game_weather",
    "load_static_park_factors",
    "get_park_factor",
    "get_stadium_info",
    
    # Pipeline
    "run_daily_mlb_pipeline",
]