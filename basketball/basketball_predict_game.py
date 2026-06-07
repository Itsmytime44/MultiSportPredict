"""
Basketball prediction module for MultiSportPredict
"""

def run_basketball_game(home_team: str, away_team: str):
    """Run basketball prediction for a matchup"""
    from pathlib import Path
    import json
    
    print(f"\n=== BASKETBALL: {home_team} vs {away_team} ===\n")
    
    # Use the existing MultiSportModel
    from MultiSportModel import (
        GameContext,
        TeamMetrics,
        eu_build_full_game,
        project_basketball_q1,
    )
    
    # Default team metrics
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
    q1_proj = project_basketball_q1(home_data, away_data)
    
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