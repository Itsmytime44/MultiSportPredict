"""Core module for MultiSportPredict"""

from core.confidence_engine import (
    confidence_score,
    bet_recommendation,
    get_volatility,
    get_thresholds,
    analyze_bet,
)
from core.historical_storage import (
    init_db,
    store_prediction,
    get_predictions,
    get_prediction_summary,
    update_prediction_outcome,
    export_predictions_to_json,
    get_recent_predictions,
)
from core.schemas import (
    schema_basketball,
    schema_soccer,
    schema_mlb,
    create_base_prediction,
    add_confidence_to_prediction,
)

__all__ = [
    # Confidence engine
    "confidence_score",
    "bet_recommendation",
    "get_volatility",
    "get_thresholds",
    "analyze_bet",
    # Historical storage
    "init_db",
    "store_prediction",
    "get_predictions",
    "get_prediction_summary",
    "update_prediction_outcome",
    "export_predictions_to_json",
    "get_recent_predictions",
    # Schemas
    "schema_basketball",
    "schema_soccer",
    "schema_mlb",
    "create_base_prediction",
    "add_confidence_to_prediction",
]
