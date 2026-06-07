"""
MLB Daily Ingestion Pipeline
=============================
Automated daily pipeline for MLB data ingestion.

Runs all ingestion steps in sequence:
1. Statcast game data
2. Player stats ingestion
3. Feature engineering
4. Sportsbook lines
5. Weather data
6. Park factors

Usage:
    python -m mlb.mlb_daily_pipeline
    OR
    from mlb.mlb_daily_pipeline import run_daily_mlb_pipeline
    run_daily_mlb_pipeline()
"""

from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Import all pipeline components
from mlb.mlb_module import ingest_recent, engineer_pitcher_features, engineer_hitter_features, engineer_team_game_features
from mlb.mlb_ingest_players import ingest_player_stats
from mlb.mlb_player_features import build_hitter_features, build_pitcher_features
from mlb.mlb_sportsbook import fetch_sportsbook_lines
from mlb.mlb_weather import fetch_weather_for_games
from mlb.mlb_park_factors import load_static_park_factors


def run_daily_mlb_pipeline(
    days_back: int = 1,
    player_ids: list = None,
    include_sportsbook: bool = True,
    include_weather: bool = True,
    include_park_factors: bool = True
):
    """
    Run the complete daily MLB ingestion pipeline.
    
    Args:
        days_back: Number of days to look back for Statcast data
        player_ids: List of player IDs to ingest (if None, skips player ingestion)
        include_sportsbook: Whether to fetch sportsbook lines
        include_weather: Whether to fetch weather data
        include_park_factors: Whether to load park factors
    """
    print(f"\n{'='*60}")
    print(f"MLB Daily Pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print('='*60 + '\n')
    
    # Step 1: Ingest Statcast game data
    print("Step 1: Ingesting Statcast game data...")
    try:
        df = ingest_recent(days_back=days_back)
        if not df.empty:
            print(f"  ✓ Ingested {len(df)} Statcast rows")
        else:
            print("  ⚠ No Statcast data available for this date range")
    except Exception as e:
        print(f"  ✗ Error ingesting Statcast: {e}")
    
    # Step 2: Build game-level features
    print("\nStep 2: Building game-level features...")
    try:
        games = engineer_team_game_features(df if 'df' in locals() else pd.DataFrame())
        if games is not None and not games.empty:
            print(f"  ✓ Built features for {len(games)} games")
    except Exception as e:
        print(f"  ✗ Error building game features: {e}")
    
    # Step 3: Ingest player stats (if player IDs provided)
    if player_ids:
        print("\nStep 3: Ingesting player statistics...")
        try:
            end = datetime.now()
            start = end - timedelta(days=days_back * 7)  # Look back further for player stats
            hitters, pitchers = ingest_player_stats(
                player_ids,
                start.strftime("%Y-%m-%d"),
                end.strftime("%Y-%m-%d")
            )
            if not hitters.empty:
                print(f"  ✓ Ingested {len(hitters)} hitter rows")
            if not pitchers.empty:
                print(f"  ✓ Ingested {len(pitchers)} pitcher rows")
        except Exception as e:
            print(f"  ✗ Error ingesting player stats: {e}")
    
    # Step 4: Build player features
    print("\nStep 4: Building player features...")
    try:
        hitter_feats = build_hitter_features()
        if hitter_feats is not None and not hitter_feats.empty:
            print(f"  ✓ Built features for {len(hitter_feats)} hitters")
        
        pitcher_feats = build_pitcher_features()
        if pitcher_feats is not None and not pitcher_feats.empty:
            print(f"  ✓ Built features for {len(pitcher_feats)} pitchers")
    except Exception as e:
        print(f"  ✗ Error building player features: {e}")
    
    # Step 5: Fetch sportsbook lines
    if include_sportsbook:
        print("\nStep 5: Fetching sportsbook lines...")
        try:
            lines = fetch_sportsbook_lines()
            if lines is not None and not lines.empty:
                print(f"  ✓ Fetched {len(lines)} prop lines")
            else:
                print("  ⚠ No sportsbook lines available (configure API endpoint)")
        except Exception as e:
            print(f"  ✗ Error fetching sportsbook lines: {e}")
    
    # Step 6: Fetch weather data
    if include_weather:
        print("\nStep 6: Fetching weather data...")
        try:
            games_df = pd.read_csv("data/mlb/games_full_features.csv") if Path("data/mlb/games_full_features.csv").exists() else pd.DataFrame()
            if not games_df.empty:
                weather = fetch_weather_for_games(games_df)
                if weather is not None and not weather.empty:
                    print(f"  ✓ Fetched weather for {len(weather)} games")
            else:
                print("  ⚠ No games found for weather fetch")
        except Exception as e:
            print(f"  ✗ Error fetching weather: {e}")
    
    # Step 7: Load park factors
    if include_park_factors:
        print("\nStep 7: Loading park factors...")
        try:
            parks = load_static_park_factors()
            if parks is not None and not parks.empty:
                print(f"  ✓ Loaded park factors for {len(parks)} stadiums")
        except Exception as e:
            print(f"  ✗ Error loading park factors: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Daily MLB pipeline completed!")
    print('='*60)


if __name__ == "__main__":
    import sys
    
    # Default player IDs (would need real IDs in production)
    DEFAULT_PLAYER_IDS = []
    
    # Parse command line arguments
    days = 1
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print(f"Usage: python -m mlb.mlb_daily_pipeline [days_back]")
            sys.exit(1)
    
    run_daily_mlb_pipeline(days_back=days, player_ids=DEFAULT_PLAYER_IDS)