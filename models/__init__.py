# MultiSportPredict Models Package
"""
Models package for MultiSportPredict.

This package contains sport-specific predictors and props generation:
- BasketballPredictor: FIBA/European basketball predictions
- SoccerPredictor: Soccer match predictions with xG
- BaseballPredictor: Unified MLB/KBO baseball predictions
- PropsEngine: Automatic player prop generation for all sports

Usage:
    from models import BasketballPredictor, SoccerPredictor, BaseballPredictor
    from models import get_predictor, generate_player_props
"""

from models.basketball_predictor import BasketballPredictor
from models.soccer_predictor import SoccerPredictor
from models.baseball_predictor import BaseballPredictor, detect_league, KBOLineupScraper

# Props engine for automatic player prop generation
try:
    from models.props_engine import PropsEngine, generate_player_props, PropRecommendation
except ImportError:
    PropsEngine = None
    generate_player_props = None
    PropRecommendation = None

__all__ = [
    'BasketballPredictor',
    'SoccerPredictor', 
    'BaseballPredictor',
    'detect_league',
    'KBOLineupScraper',
    'PropsEngine',
    'generate_player_props',
    'PropRecommendation',
]

# Also expose the factory function from base_predictor
try:
    from base_predictor import get_predictor, quick_predict, SportPredictorBase
    __all__.extend(['get_predictor', 'quick_predict', 'SportPredictorBase'])
except ImportError:
    pass
