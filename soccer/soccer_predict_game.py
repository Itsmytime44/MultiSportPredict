"""
Soccer prediction module for MultiSportPredict
"""

def run_soccer_game(home_team: str, away_team: str):
    """Run soccer prediction for a matchup"""
    from pathlib import Path
    import json
    
    print(f"\n=== SOCCER: {home_team} vs {away_team} ===\n")
    
    # Use the existing MultiSportModel
    from MultiSportModel import (
        estimate_team_goals,
        estimate_btts_prob,
        poisson_over_prob,
    )
    
    # Default team data
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