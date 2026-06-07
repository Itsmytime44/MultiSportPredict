"""
Soccer prediction module for MultiSportPredict
Enhanced with referee data hooks and historical storage.
Maintains all sophisticated existing prediction logic.
"""

from typing import Any, Dict, Optional


def fetch_soccer_ref_data(home: str, away: str) -> Dict[str, Any]:
    """
    Fetch referee data for a soccer match.
    
    This is a placeholder that should be integrated with real data sources
    like Transfermarkt, PlayerStats, Flashscore, or official league data.
    
    Returns:
        Dictionary with referee statistics
    """
    # TODO: Integrate with real referee data API
    # Real implementation would call:
    # - Transfermarkt for referee assignment and history
    # - Official league data for card tendencies
    # - Flashscore for real-time referee stats
    
    return {
        "yellow_cards_per_game": 4.2,     # Average yellow cards per game
        "red_cards_per_game": 0.25,       # Average red cards per game
        "penalties_per_game": 0.18,       # Average penalties awarded per game
        "home_card_diff": -0.3,           # Home vs away card differential
        "fouls_per_game": 22.5,           # Average fouls per game
        "strictness_rating": 0.65,        # Referee strictness (0-1)
    }


def run_soccer_game(
    home_team: str, 
    away_team: str,
    market_line: float = 0.25,
    market_total: float = 2.5,
    store_to_db: bool = True,
):
    """
    Run soccer prediction for a matchup with enhanced features.
    
    Args:
        home_team: Home team name
        away_team: Away team name
        market_line: Current market Asian handicap line
        market_total: Current market total goals line
        store_to_db: Whether to store prediction to database
        
    Returns:
        Dictionary with comprehensive prediction results
    """
    from pathlib import Path
    import json
    from core import (
        confidence_score,
        bet_recommendation,
        store_prediction,
        schema_soccer,
    )
    
    print(f"\n=== SOCCER: {home_team} vs {away_team} ===\n")
    
    # Use the existing MultiSportModel for sophisticated predictions
    from MultiSportModel import (
        estimate_team_goals,
        estimate_btts_prob,
        poisson_over_prob,
    )
    
    # Fetch external data (referee)
    ref_data = fetch_soccer_ref_data(home_team, away_team)
    
    # Default team data (in production, these would come from your data pipeline)
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
    
    # Calculate expected goals using sophisticated model
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
    
    # Adjust total based on referee penalty tendency
    penalty_adjustment = ref_data["penalties_per_game"] * 0.4  # Each penalty ~0.4 expected goals
    adjusted_total = total_lam + penalty_adjustment
    
    # BTTS probability
    btts_prob = estimate_btts_prob(home_data['xg_for'], away_data['xg_for'], 0, 0)
    
    # Goal probabilities with adjusted total
    p_over_15 = poisson_over_prob(adjusted_total, 1.5)
    p_over_25 = poisson_over_prob(adjusted_total, 2.5)
    p_over_35 = poisson_over_prob(adjusted_total, 3.5)
    
    # Match outcome probabilities
    home_win_prob = home_lam / (home_lam + away_lam) * 0.85 + 0.10
    away_win_prob = away_lam / (home_lam + away_lam) * 0.05 + 0.05
    draw_prob = 1 - home_win_prob - away_win_prob
    
    # Calculate confidence scores for betting markets
    side_edge = (home_lam - away_lam) - market_line
    total_edge = adjusted_total - market_total
    btts_edge = btts_prob - 0.5
    
    # Use confidence engine with sport-specific volatilities
    side_confidence = confidence_score(
        side_edge, 
        volatility=0.50,  # Soccer sides volatility
        market_alignment=0.0
    )
    total_confidence = confidence_score(
        total_edge, 
        volatility=0.55,  # Soccer totals volatility
        market_alignment=0.0
    )
    btts_confidence = confidence_score(
        btts_edge * 100,  # Scale probability edge
        volatility=0.48,  # BTTS volatility
        market_alignment=0.0
    )
    
    side_rec = bet_recommendation(side_confidence)
    total_rec = bet_recommendation(total_confidence)
    btts_rec = bet_recommendation(btts_confidence)
    
    # Build comprehensive output
    output = {
        "sport": "soccer",
        "game": {
            "home_team": home_team,
            "away_team": away_team,
            "projected_home_goals": round(home_lam, 2),
            "projected_away_goals": round(away_lam, 2),
            "projected_total_goals": round(adjusted_total, 2),
            "home_win_prob": round(home_win_prob, 3),
            "draw_prob": round(draw_prob, 3),
            "away_win_prob": round(away_win_prob, 3),
        },
        "predictions": {
            "side": {
                "model_xg_diff": round(home_lam - away_lam, 3),
                "market_line": market_line,
                "edge": round(side_edge, 3),
                "confidence": side_confidence,
                "recommendation": side_rec,
            },
            "total": {
                "model_total_xg": round(adjusted_total, 3),
                "market_total": market_total,
                "edge": round(total_edge, 3),
                "confidence": total_confidence,
                "recommendation": total_rec,
            },
            "btts": {
                "probability": round(btts_prob, 3),
                "confidence": btts_confidence,
                "recommendation": btts_rec,
            },
        },
        "goals_analysis": {
            "over_15_prob": round(p_over_15, 3),
            "over_25_prob": round(p_over_25, 3),
            "over_35_prob": round(p_over_35, 3),
        },
        "btts_probability": round(btts_prob, 3),
        "meta": {
            "ref_data": ref_data,
        }
    }
    
    # Store to database if enabled
    if store_to_db:
        try:
            # Store side prediction
            store_prediction(
                sport="soccer",
                home_team=home_team,
                away_team=away_team,
                market_type="side",
                model_value=home_lam - away_lam,
                market_value=market_line,
                edge=side_edge,
                confidence=side_confidence,
                recommendation=side_rec,
                raw_json=output
            )
            
            # Store total prediction
            store_prediction(
                sport="soccer",
                home_team=home_team,
                away_team=away_team,
                market_type="total",
                model_value=adjusted_total,
                market_value=market_total,
                edge=total_edge,
                confidence=total_confidence,
                recommendation=total_rec,
                raw_json=output
            )
            
            # Store BTTS prediction
            store_prediction(
                sport="soccer",
                home_team=home_team,
                away_team=away_team,
                market_type="btts",
                model_value=btts_prob,
                market_value=0.5,
                edge=btts_edge,
                confidence=btts_confidence,
                recommendation=btts_rec,
                raw_json=output
            )
        except Exception as e:
            print(f"Warning: Could not store to database: {e}")
    
    # Save to output file
    out_dir = Path("output/soccer")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{home_team.replace(' ', '_')}_vs_{away_team.replace(' ', '_')}.json"
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Print summary
    print(f"Projected Score: {home_team} {home_lam:.1f} - {away_team} {away_lam:.1f}")
    print(f"Projected Total Goals: {adjusted_total:.2f}")
    print(f"\nGoal Probabilities:")
    print(f"  Over 1.5: {p_over_15:.1%}")
    print(f"  Over 2.5: {p_over_25:.1%}")
    print(f"  Over 3.5: {p_over_35:.1%}")
    print(f"\nBTTS Probability: {btts_prob:.1%}")
    print(f"\nMatch Outcome:")
    print(f"  {home_team} Win: {home_win_prob:.1%}")
    print(f"  Draw: {draw_prob:.1%}")
    print(f"  {away_team} Win: {away_win_prob:.1%}")
    print(f"\nBetting Predictions:")
    print(f"  Side: {side_rec} (Confidence: {side_confidence:.1f}%)")
    print(f"  Total: {total_rec} (Confidence: {total_confidence:.1f}%)")
    print(f"  BTTS: {btts_rec} (Confidence: {btts_confidence:.1f}%)")
    print(f"\nResults saved to: {out_path}")
    
    return output
