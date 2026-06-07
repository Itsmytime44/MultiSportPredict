#!/usr/bin/env python
"""
Unified CLI for MultiSportPredict
==================================
Predict matches across multiple sports with a single command.

Usage:
    python predict_match.py <sport> <home_team> <away_team>

Supported Sports:
    - basketball
    - soccer
    - baseball / mlb

Examples:
    python predict_match.py basketball "UCAM Murcia" "FC Barcelona"
    python predict_match.py soccer "Liverpool" "Aston Villa"
    python predict_match.py baseball "Yankees" "Red Sox"
    python predict_match.py mlb "LAD" "SF"
"""

import sys
import json
from pathlib import Path


def run_basketball_game(home_team: str, away_team: str) -> dict:
    """Run basketball prediction using the existing MultiSportModel"""
    print(f"\n{'='*60}")
    print(f"BASKETBALL MATCHUP: {home_team} vs {away_team}")
    print('='*60 + '\n')
    
    try:
        from MultiSportModel import (
            GameContext,
            TeamMetrics,
            eu_build_full_game,
            project_basketball_q1,
        )
        
        # Default team metrics (in a real implementation, these would be loaded from data)
        home_data = {
            'ortg': 110.0,
            'drtg': 105.0,
            'baseline_net': 5.0,
            'recent_net': 4.0,
            'pace': 95.0,
            'rest_days': 2,
            'travel_km': 0,
            'back_to_back': False,
            'three_in_six': False,
            'split_edge': 3.0,
            'rotation_depth': 9,
            'injury_status': 'green',
            'coach_stability': 'green',
            'motivation': 'green',
        }
        
        away_data = {
            'ortg': 108.0,
            'drtg': 107.0,
            'baseline_net': 1.0,
            'recent_net': 2.0,
            'pace': 93.0,
            'rest_days': 2,
            'travel_km': 500,
            'back_to_back': False,
            'three_in_six': False,
            'split_edge': 1.0,
            'rotation_depth': 8,
            'injury_status': 'yellow',
            'coach_stability': 'green',
            'motivation': 'green',
        }
        
        market_data = {
            'open_line': -2.0,
            'current_line': -2.5,
            'spread': -2.5,
            'total': 165.0,
        }
        
        ctx = GameContext(
            game_id=f"{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}",
            date="2026-06-06",
            league="Basketball",
            record_type="full_game",
            home_team=home_team,
            away_team=away_team,
            market_line=market_data['spread'],
            current_line=market_data['current_line'],
            open_line=market_data['open_line'],
        )
        
        home_tm = TeamMetrics(
            ortg=home_data['ortg'],
            drtg=home_data['drtg'],
            baseline_net=home_data['baseline_net'],
            recent_net=home_data['recent_net'],
            pace=home_data['pace'],
            rest_days=home_data['rest_days'],
            travel_km=home_data['travel_km'],
            back_to_back=home_data['back_to_back'],
            three_in_six=home_data['three_in_six'],
            split_edge=home_data['split_edge'],
            rotation_depth=home_data['rotation_depth'],
            injury_status=home_data['injury_status'],
            coach_stability=home_data['coach_stability'],
            motivation=home_data['motivation'],
            open_line=market_data['open_line'],
            current_line=market_data['current_line'],
        )
        
        away_tm = TeamMetrics(
            ortg=away_data['ortg'],
            drtg=away_data['drtg'],
            baseline_net=away_data['baseline_net'],
            recent_net=away_data['recent_net'],
            pace=away_data['pace'],
            rest_days=away_data['rest_days'],
            travel_km=away_data['travel_km'],
            back_to_back=away_data['back_to_back'],
            three_in_six=away_data['three_in_six'],
            split_edge=away_data['split_edge'],
            rotation_depth=away_data['rotation_depth'],
            injury_status=away_data['injury_status'],
            coach_stability=away_data['coach_stability'],
            motivation=away_data['motivation'],
            open_line=-market_data['open_line'],
            current_line=-market_data['current_line'],
        )
        
        result = eu_build_full_game(home_tm, away_tm, ctx)
        
        # Q1 projection
        q1_proj = project_basketball_q1(
            {k: v for k, v in home_data.items()},
            {k: v for k, v in away_data.items()}
        )
        
        output = {
            "sport": "basketball",
            "game": {
                "home_team": home_team,
                "away_team": away_team,
                "projected_home_score": result['projected_home_score'],
                "projected_away_score": result['projected_away_score'],
                "projected_total": result['projected_total'],
                "win_probability": result['probability'],
                "model_edge": result['model_edge'],
                "lean": result['lean'],
            },
            "q1_projection": q1_proj,
        }
        
        # Save output
        out_dir = Path("output/basketball")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
        with open(out_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Projected Score: {home_team} {result['projected_home_score']:.1f} - {away_team} {result['projected_away_score']:.1f}")
        print(f"Projected Total: {result['projected_total']:.1f}")
        print(f"Win Probability: {home_team} {result['probability']:.1%}")
        print(f"Model Edge: {result['model_edge']:+.2f}")
        print(f"Lean: {result['lean']}")
        print(f"\nResults saved to: {out_path}")
        
        return output
        
    except ImportError as e:
        print(f"Error: Basketball module not available. {e}")
        return {}


def run_soccer_game(home_team: str, away_team: str) -> dict:
    """Run soccer prediction using the existing MultiSportModel"""
    print(f"\n{'='*60}")
    print(f"SOCCER MATCHUP: {home_team} vs {away_team}")
    print('='*60 + '\n')
    
    try:
        from MultiSportModel import (
            SoccerHandicapper,
            estimate_team_goals,
            estimate_btts_prob,
            poisson_over_prob,
        )
        
        # Default team data (in a real implementation, these would be loaded from data)
        home_data = {
            'xg_for': 1.65,
            'xg_against': 1.20,
            'shots': 13.0,
            'sot': 4.5,
            'goals_for': 1.7,
            'goals_against': 1.1,
            'clean_sheets': 4,
            'missing_attacker': 0,
            'missing_creator': 0,
            'missing_cb': 0,
            'missing_gk': 0,
            'tempo': 0.3,
            'width_crossing': 0.55,
            'final_third_pressure': 0.55,
        }
        
        away_data = {
            'xg_for': 1.45,
            'xg_against': 1.35,
            'shots': 11.5,
            'sot': 4.0,
            'goals_for': 1.4,
            'goals_against': 1.3,
            'clean_sheets': 3,
            'missing_attacker': 0,
            'missing_creator': 0,
            'missing_cb': 0,
            'missing_gk': 0,
            'tempo': 0.1,
            'width_crossing': 0.50,
            'final_third_pressure': 0.45,
        }
        
        # Calculate expected goals
        home_lam = estimate_team_goals(
            home_data['xg_for'], home_data['sot'], home_data['tempo'], 1,
            home_data['missing_attacker'], home_data['missing_creator'],
            away_data['xg_against'], away_data['missing_cb'], away_data['missing_gk']
        )
        away_lam = estimate_team_goals(
            away_data['xg_for'], away_data['sot'], away_data['tempo'], 0,
            away_data['missing_attacker'], away_data['missing_creator'],
            home_data['xg_against'], home_data['missing_cb'], home_data['missing_gk']
        )
        total_lam = home_lam + away_lam
        
        # BTTS probability
        btts_prob = estimate_btts_prob(home_data['xg_for'], away_data['xg_for'], 0, 0)
        
        # Goal probabilities
        p_over_15 = poisson_over_prob(total_lam, 1.5)
        p_over_25 = poisson_over_prob(total_lam, 2.5)
        p_over_35 = poisson_over_prob(total_lam, 3.5)
        
        # Match outcome probabilities
        home_win_prob = home_lam / (home_lam + away_lam) * 0.85 + 0.10
        away_win_prob = away_lam / (home_lam + away_lam) * 0.85 + 0.05
        draw_prob = 1 - home_win_prob - away_win_prob
        
        output = {
            "sport": "soccer",
            "game": {
                "home_team": home_team,
                "away_team": away_team,
                "projected_home_goals": round(home_lam, 2),
                "projected_away_goals": round(away_lam, 2),
                "projected_total_goals": round(total_lam, 2),
                "home_win_prob": round(home_win_prob, 3),
                "draw_prob": round(draw_prob, 3),
                "away_win_prob": round(away_win_prob, 3),
            },
            "goals_analysis": {
                "over_15_prob": round(p_over_15, 3),
                "over_25_prob": round(p_over_25, 3),
                "over_35_prob": round(p_over_35, 3),
            },
            "btts_probability": round(btts_prob, 3),
        }
        
        # Save output
        out_dir = Path("output/soccer")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
        with open(out_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Projected Score: {home_team} {home_lam:.1f} - {away_team} {away_lam:.1f}")
        print(f"Projected Total Goals: {total_lam:.2f}")
        print(f"\nGoal Probabilities:")
        print(f"  Over 1.5: {p_over_15:.1%}")
        print(f"  Over 2.5: {p_over_25:.1%}")
        print(f"  Over 3.5: {p_over_35:.1%}")
        print(f"\nBTTS Probability: {btts_prob:.1%}")
        print(f"\nMatch Outcome:")
        print(f"  {home_team} Win: {home_win_prob:.1%}")
        print(f"  Draw: {draw_prob:.1%}")
        print(f"  {away_team} Win: {away_win_prob:.1%}")
        print(f"\nResults saved to: {out_path}")
        
        return output
        
    except ImportError as e:
        print(f"Error: Soccer module not available. {e}")
        return {}


def run_mlb_game(home_team: str, away_team: str) -> dict:
    """Run MLB prediction using the new MLB module"""
    print(f"\n{'='*60}")
    print(f"MLB MATCHUP: {home_team} vs {away_team}")
    print('='*60 + '\n')
    
    try:
        from mlb import predict_match as mlb_predict
        
        result = mlb_predict(home_team, away_team)
        
        print(f"Projected Total Runs: {result['game']['projected_total_runs']:.1f}")
        print(f"Projected Run Differential: {result['game']['projected_run_diff_home_minus_away']:+.1f}")
        
        print(f"\nK Props:")
        for team, props in result['k_props'].items():
            print(f"  {team}: {props['projection']:.1f} Ks (Line: {props['line']}) -> {props['lean']}")
        
        print(f"\nHR Props:")
        for team, props in result['hr_props'].items():
            print(f"  {team}: {props['hr_probability']:.1%} HR probability -> {props['lean']}")
        
        print(f"\nPlayer Props:")
        for team, props in result['player_props'].items():
            for prop in props:
                print(f"  {prop['player_name']} ({prop['prop_type']}): {prop['projection']:.1f} (Line: {prop['line']}) -> {prop['lean']}")
        
        print(f"\nResults saved to: output/mlb/{result['game']['home_team']}_vs_{result['game']['away_team']}.json")
        
        return result
        
    except ImportError as e:
        print(f"Error: MLB module not available. Make sure pybaseball is installed. {e}")
        return {}
    except ValueError as e:
        print(f"Error: {e}")
        return {}


def main():
    """Main entry point for the unified CLI"""
    if len(sys.argv) < 4:
        print(__doc__)
        print(f"\nError: Not enough arguments provided.")
        print(f"Usage: python predict_match.py <sport> <home_team> <away_team>")
        sys.exit(1)
    
    sport = sys.argv[1].lower()
    home_team = sys.argv[2]
    away_team = sys.argv[3]
    
    if sport == "basketball":
        run_basketball_game(home_team, away_team)
    elif sport == "soccer":
        run_soccer_game(home_team, away_team)
    elif sport in ("baseball", "mlb"):
        run_mlb_game(home_team, away_team)
    else:
        print(f"\nError: Unknown sport '{sport}'")
        print("Supported sports: basketball, soccer, baseball/mlb")
        sys.exit(1)


if __name__ == "__main__":
    main()