"""
Sport-Specific JSON Schema Definitions for MultiSportPredict
=============================================================
Provides standardized output schemas for all sports predictions.
Ensures consistent data structure across all modules.
"""

from datetime import datetime
from typing import Any, Dict, Optional


def schema_basketball() -> Dict[str, Any]:
    """
    Returns the standard schema for basketball predictions.
    
    Structure:
    - game_info: Basic game information
    - full_game: Spread predictions
    - totals: Over/under predictions
    - moneyline: Win probability predictions
    - player_props: Player-specific prop predictions
    - meta: Metadata including ref data and consensus
    """
    return {
        "game_info": {
            "home": "",
            "away": "",
            "timestamp": datetime.now().isoformat(),
            "league": "Basketball"
        },
        "full_game": {
            "model_spread": 0.0,
            "market_spread": 0.0,
            "edge": 0.0,
            "confidence": 0.0,
            "recommendation": "PASS"
        },
        "totals": {
            "model_total": 0.0,
            "market_total": 0.0,
            "edge": 0.0,
            "confidence": 0.0,
            "recommendation": "PASS"
        },
        "moneyline": {
            "model_prob": 0.5,
            "edge": 0.0,
            "confidence": 0.0,
            "recommendation": "PASS"
        },
        "player_props": [],
        "meta": {
            "ref_data": {},
            "consensus": {}
        }
    }


def schema_soccer() -> Dict[str, Any]:
    """
    Returns the standard schema for soccer predictions.
    
    Structure:
    - game_info: Basic game information
    - side: Match outcome predictions (1X2)
    - totals: Over/under goals predictions
    - btts: Both teams to score prediction
    - player_props: Player-specific prop predictions
    - meta: Metadata including ref data
    """
    return {
        "game_info": {
            "home": "",
            "away": "",
            "timestamp": datetime.now().isoformat(),
            "league": "Soccer"
        },
        "side": {
            "model_xg_diff": 0.0,
            "market_line": 0.0,
            "edge": 0.0,
            "confidence": 0.0,
            "recommendation": "PASS"
        },
        "totals": {
            "model_total_xg": 0.0,
            "market_total": 0.0,
            "edge": 0.0,
            "confidence": 0.0,
            "recommendation": "PASS"
        },
        "btts": {
            "probability": 0.0,
            "confidence": 0.0,
            "recommendation": "PASS"
        },
        "player_props": [],
        "meta": {
            "ref_data": {}
        }
    }


def schema_mlb() -> Dict[str, Any]:
    """
    Returns the standard schema for MLB predictions.
    
    Structure:
    - game_info: Basic game information
    - full_game: Total runs and run differential predictions
    - pitcher_props: Pitcher-specific prop predictions
    - hitter_props: Hitter-specific prop predictions
    - meta: Metadata including park factors and weather
    """
    return {
        "game_info": {
            "home": "",
            "away": "",
            "timestamp": datetime.now().isoformat(),
            "league": "MLB"
        },
        "full_game": {
            "model_total": 0.0,
            "market_total": 0.0,
            "edge": 0.0,
            "confidence": 0.0,
            "recommendation": "PASS",
            "run_diff": 0.0
        },
        "pitcher_props": [],
        "hitter_props": [],
        "meta": {
            "park_factor_run": 1.0,
            "park_factor_hr": 1.0,
            "weather": {}
        }
    }


def create_base_prediction(
    sport: str,
    home_team: str,
    away_team: str,
    league: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a base prediction dictionary with common fields.
    
    Args:
        sport: Sport type (basketball, soccer, mlb)
        home_team: Home team name
        away_team: Away team name
        league: Optional league name
        
    Returns:
        Base prediction dictionary
    """
    if league is None:
        league = sport.capitalize()
    
    return {
        "sport": sport,
        "league": league,
        "home_team": home_team,
        "away_team": away_team,
        "timestamp": datetime.now().isoformat(),
        "predictions": {},
        "meta": {}
    }


def add_confidence_to_prediction(
    prediction: Dict[str, Any],
    market_type: str,
    model_value: float,
    market_value: float,
    edge: float,
    confidence: float,
    recommendation: str
) -> Dict[str, Any]:
    """
    Add a confidence-scored prediction to a prediction dictionary.
    
    Args:
        prediction: Base prediction dictionary
        market_type: Type of market (spread, total, moneyline, etc.)
        model_value: Model's projected value
        market_value: Market line/value
        edge: Difference between model and market
        confidence: Confidence score (0-100)
        recommendation: Bet recommendation
        
    Returns:
        Updated prediction dictionary
    """
    prediction["predictions"][market_type] = {
        "model_value": round(model_value, 2),
        "market_value": market_value,
        "edge": round(edge, 2),
        "confidence": confidence,
        "recommendation": recommendation,
        "lean": "Over" if edge > 0 else "Under"
    }
    
    return prediction


def validate_prediction_schema(
    prediction: Dict[str, Any],
    sport: str
) -> bool:
    """
    Validate that a prediction dictionary matches the expected schema.
    
    Args:
        prediction: Prediction dictionary to validate
        sport: Expected sport type
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["sport", "home_team", "away_team", "timestamp"]
    
    for field in required_fields:
        if field not in prediction:
            return False
    
    if prediction["sport"] != sport:
        return False
    
    # Check sport-specific fields
    if sport == "basketball":
        required_sections = ["full_game", "totals"]
    elif sport == "soccer":
        required_sections = ["side", "totals"]
    elif sport == "mlb":
        required_sections = ["full_game"]
    else:
        return True  # Unknown sport, just check base fields
    
    if "predictions" not in prediction:
        return False
    
    for section in required_sections:
        if section not in prediction["predictions"]:
            return False
    
    return True


def format_prediction_for_output(
    prediction: Dict[str, Any],
    include_meta: bool = True
) -> Dict[str, Any]:
    """
    Format a prediction dictionary for JSON output.
    
    Args:
        prediction: Prediction dictionary
        include_meta: Whether to include metadata
        
    Returns:
        Formatted prediction dictionary
    """
    output = {
        "sport": prediction.get("sport"),
        "league": prediction.get("league"),
        "game": {
            "home_team": prediction.get("home_team"),
            "away_team": prediction.get("away_team"),
            "timestamp": prediction.get("timestamp")
        },
        "predictions": prediction.get("predictions", {})
    }
    
    if include_meta and "meta" in prediction:
        output["meta"] = prediction["meta"]
    
    return output