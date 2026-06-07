#!/usr/bin/env python
"""
Unified CLI for MultiSportPredict
==================================
Predict matches across multiple sports with a single command.

Supported Sports:
    - basketball (FIBA/European rules)
    - soccer (xG-based predictions)
    - baseball/mlb (MLB predictions)
    - kbo (Korean Baseball Organization)

Usage:
    python predict_match.py <sport> <home_team> <away_team> [league]

Examples:
    python predict_match.py basketball "Real Madrid" "FC Barcelona"
    python predict_match.py soccer "Liverpool" "Aston Villa"
    python predict_match.py baseball "Yankees" "Red Sox"
    python predict_match.py mlb "LAD" "SF"
    python predict_match.py kbo "Doosan Bears" "LG Twins"
    python predict_match.py basketball "Olympiacos" "Panathinaikos" EuroLeague
    python predict_match.py soccer "Bayern Munich" "Dortmund" Bundesliga
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any


def run_basketball_game(home_team: str, away_team: str, league: str = "EuroLeague",
                        market_line: float = 0.0, current_line: float = 0.0, 
                        open_line: float = 0.0) -> Dict[str, Any]:
    """
    Run basketball prediction using the FIBA/European module.
    
    Args:
        home_team: Home team name
        away_team: Away team name
        league: League type (default: EuroLeague)
        market_line: Current market spread
        current_line: Current line (for market filter)
        open_line: Opening line (for market filter)
        
    Returns:
        Dictionary with prediction results
    """
    print(f"\n{'='*60}")
    print(f"BASKETBALL ({league}) MATCHUP: {home_team} vs {away_team}")
    print('='*60 + '\n')
    
    try:
        from models.basketball_predictor import BasketballPredictor
        
        predictor = BasketballPredictor(league=league)
        result = predictor.predict(
            features=None,
            model=None,
            home_team=home_team,
            away_team=away_team,
            market_line=market_line,
            current_line=current_line or market_line,
            open_line=open_line or market_line,
        )
        
        # Display results
        full_game = result.get('full_game', {})
        print(f"Projected Score: {home_team} {full_game.get('projected_home_score', 0):.1f} - {away_team} {full_game.get('projected_away_score', 0):.1f}")
        print(f"Projected Total: {full_game.get('projected_total', 0):.1f}")
        print(f"Win Probability: {home_team} {full_game.get('probability', 0):.1%}")
        print(f"Model Edge: {full_game.get('model_edge', 0):+.2f}")
        print(f"Lean: {full_game.get('lean', 'N/A')}")
        
        # Save to output file
        out_dir = Path("output/basketball")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
        with open(out_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nResults saved to: {out_path}")
        
        return result
        
    except ImportError as e:
        print(f"Error: Basketball module not available. {e}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}


def run_soccer_game(home_team: str, away_team: str, league: str = "Premier League",
                    market_line: float = 0.0, market_total: float = 2.5) -> Dict[str, Any]:
    """
    Run soccer prediction using the xG-based module.
    
    Args:
        home_team: Home team name
        away_team: Away team name
        league: League type (default: Premier League)
        market_line: Asian handicap line
        market_total: Over/under goals line
        
    Returns:
        Dictionary with prediction results
    """
    print(f"\n{'='*60}")
    print(f"SOCCER ({league}) MATCHUP: {home_team} vs {away_team}")
    print('='*60 + '\n')
    
    try:
        from models.soccer_predictor import SoccerPredictor
        
        predictor = SoccerPredictor(league=league)
        result = predictor.predict(
            features=None,
            model=None,
            home_team=home_team,
            away_team=away_team,
            market_line=market_line,
            market_total=market_total,
        )
        
        # Display results
        game = result.get('game', {})
        print(f"Projected Score: {home_team} {game.get('projected_home_goals', 0):.2f} - {away_team} {game.get('projected_away_goals', 0):.2f}")
        print(f"Projected Total Goals: {game.get('projected_total_goals', 0):.2f}")
        
        print(f"\nMatch Outcome:")
        print(f"  {home_team} Win: {game.get('home_win_prob', 0):.1%}")
        print(f"  Draw: {game.get('draw_prob', 0):.1%}")
        print(f"  {away_team} Win: {game.get('away_win_prob', 0):.1%}")
        
        predictions = result.get('predictions', {})
        if 'side' in predictions:
            side = predictions['side']
            print(f"\nSide: {side.get('recommendation', 'N/A')} (Confidence: {side.get('confidence', 0):.1f}%)")
        if 'total' in predictions:
            total = predictions['total']
            print(f"Total: {total.get('recommendation', 'N/A')} (Confidence: {total.get('confidence', 0):.1f}%)")
        if 'btts' in predictions:
            btts = predictions['btts']
            print(f"BTTS: {btts.get('recommendation', 'N/A')} (Confidence: {btts.get('confidence', 0):.1f}%)")
        
        # Save to output file
        out_dir = Path("output/soccer")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
        with open(out_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nResults saved to: {out_path}")
        
        return result
        
    except ImportError as e:
        print(f"Error: Soccer module not available. {e}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}


def run_baseball_game(home_team: str, away_team: str, league: str = "MLB") -> Dict[str, Any]:
    """
    Run baseball prediction using the unified MLB/KBO module.
    
    Args:
        home_team: Home team name
        away_team: Away team name
        league: League type (MLB or KBO)
        
    Returns:
        Dictionary with prediction results
    """
    print(f"\n{'='*60}")
    print(f"BASEBALL ({league.upper()}) MATCHUP: {home_team} vs {away_team}")
    print('='*60 + '\n')
    
    try:
        from models.baseball_predictor import BaseballPredictor
        
        predictor = BaseballPredictor()
        
        # Load data and engineer features
        data = predictor.load_data(league=league, home_team=home_team, away_team=away_team)
        features = predictor.feature_engineering(data)
        result = predictor.predict(features, None, home_team, away_team, league=league)
        
        # Display results
        game = result.get('game', {})
        print(f"Projected Total Runs: {game.get('projected_total_runs', 0):.2f}")
        print(f"Projected Run Differential: {game.get('projected_run_differential', 0):+.2f}")
        print(f"Win Probability: {home_team} {game.get('home_win_probability', 0):.1%}")
        
        confidence = game.get('confidence', {})
        if 'total' in confidence:
            total = confidence['total']
            print(f"\nTotal: {total.get('recommendation', 'N/A')} (Confidence: {total.get('score', 0):.1f}%)")
        if 'side' in confidence:
            side = confidence['side']
            print(f"Side: {side.get('recommendation', 'N/A')} (Confidence: {side.get('score', 0):.1f}%)")
        
        # Save to output file
        out_dir = Path("output/baseball")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
        with open(out_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nResults saved to: {out_path}")
        
        return result
        
    except ImportError as e:
        print(f"Error: Baseball module not available. {e}")
        return {}
    except Exception as e:
        print(f"Error: {e}")
        return {}


def main():
    """Main entry point for the unified CLI"""
    if len(sys.argv) < 4:
        print(__doc__)
        print(f"\nError: Not enough arguments provided.")
        print(f"Usage: python predict_match.py <sport> <home_team> <away_team> [league]")
        sys.exit(1)
    
    sport = sys.argv[1].lower()
    home_team = sys.argv[2]
    away_team = sys.argv[3]
    
    # Optional league parameter
    league = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Initialize database for historical storage
    try:
        from core import init_db
        init_db()
        print("Database initialized: multisport_history.db\n")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}\n")
    
    if sport == "basketball":
        run_basketball_game(home_team, away_team, league=league or "EuroLeague")
    elif sport == "soccer":
        run_soccer_game(home_team, away_team, league=league or "Premier League")
    elif sport in ("baseball", "mlb"):
        run_baseball_game(home_team, away_team, league="MLB")
    elif sport == "kbo":
        run_baseball_game(home_team, away_team, league="KBO")
    else:
        print(f"\nError: Unknown sport '{sport}'")
        print("Supported sports: basketball, soccer, baseball/mlb, kbo")
        sys.exit(1)


if __name__ == "__main__":
    main()