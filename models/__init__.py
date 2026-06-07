# MultiSportPredict Models Package
"""
Models package for MultiSportPredict.

This package contains sport-specific predictors:
- BasketballPredictor: FIBA/European basketball predictions
- SoccerPredictor: Soccer match predictions with xG
- BaseballPredictor: Unified MLB/KBO baseball predictions

Usage:
    from models import BasketballPredictor, SoccerPredictor, BaseballPredictor
    from models import get_predictor  # Factory function from base_predictor
"""

from models.basketball_predictor import BasketballPredictor
from models.soccer_predictor import SoccerPredictor
from models.baseball_predictor import BaseballPredictor, detect_league, KBOLineupScraper

__all__ = [
    'BasketballPredictor',
    'SoccerPredictor', 
    'BaseballPredictor',
    'detect_league',
    'KBOLineupScraper',
]

# Also expose the factory function from base_predictor
try:
    from base_predictor import get_predictor, quick_predict, SportPredictorBase
    __all__.extend(['get_predictor', 'quick_predict', 'SportPredictorBase'])
except ImportError:
    pass