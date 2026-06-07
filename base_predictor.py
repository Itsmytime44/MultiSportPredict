#!/usr/bin/env python
"""
Base Predictor Module for MultiSportPredict
============================================
Abstract base class defining the interface for all sport-specific predictors.

This module implements the Factory Pattern for sport prediction models,
ensuring clean separation between sport-specific logic while maintaining
a consistent interface across all predictors.

Usage:
    from base_predictor import SportPredictorBase
    
    class MySportPredictor(SportPredictorBase):
        def load_data(self, *args, **kwargs):
            pass
        def feature_engineering(self, data, *args, **kwargs):
            pass
        def train_model(self, features, *args, **kwargs):
            pass
        def predict(self, features, model, *args, **kwargs):
            pass
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime


class SportPredictorBase(ABC):
    """
    Abstract base class for all sport prediction models.
    
    This class defines the standard interface that all sport-specific
    predictors must implement. It provides a consistent API for:
    - Data loading and preprocessing
    - Feature engineering
    - Model training
    - Prediction generation
    
    Subclasses must implement all abstract methods.
    """
    
    def __init__(self, name: str = None):
        """
        Initialize the predictor.
        
        Args:
            name: Optional name for this predictor instance
        """
        self.name = name or self.__class__.__name__
        self._model = None
        self._last_trained = None
    
    @abstractmethod
    def load_data(self, *args, **kwargs) -> Any:
        """
        Load and preprocess data for the specific sport.
        
        This method should handle:
        - Data source connection (files, APIs, databases)
        - Initial data cleaning and validation
        - Data normalization and formatting
        
        Returns:
            Raw or lightly processed data suitable for feature engineering
        """
        pass
    
    @abstractmethod
    def feature_engineering(self, data: Any, *args, **kwargs) -> Any:
        """
        Perform feature engineering for the specific sport.
        
        This method should:
        - Create predictive features from raw data
        - Handle missing values and outliers
        - Apply sport-specific transformations
        - Generate derived metrics and statistics
        
        Args:
            data: Raw data from load_data()
            
        Returns:
            Processed features suitable for model training/prediction
        """
        pass
    
    @abstractmethod
    def train_model(self, features: Any, *args, **kwargs) -> Any:
        """
        Train the prediction model for the specific sport.
        
        This method should:
        - Split data into training/validation sets
        - Train machine learning or statistical models
        - Evaluate model performance
        - Save trained model if needed
        
        Args:
            features: Processed features from feature_engineering()
            
        Returns:
            Trained model object or None if using pre-trained model
        """
        pass
    
    @abstractmethod
    def predict(self, features: Any, model: Any, *args, **kwargs) -> Dict[str, Any]:
        """
        Make predictions for the specific sport.
        
        This method should:
        - Use the trained model to generate predictions
        - Calculate confidence scores
        - Format output according to sport-specific schema
        - Include metadata and diagnostic information
        
        Args:
            features: Processed features for the specific matchup
            model: Trained model from train_model() or None for pre-trained
            
        Returns:
            Dictionary containing predictions, confidence scores, and metadata
        """
        pass
    
    def run_pipeline(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Run the complete prediction pipeline.
        
        This method orchestrates the full workflow:
        1. Load data
        2. Engineer features
        3. Train model (if needed)
        4. Generate predictions
        
        Returns:
            Complete prediction results dictionary
        """
        print(f"[{self.name}] Running prediction pipeline...")
        
        # Step 1: Load data
        data = self.load_data(*args, **kwargs)
        
        # Step 2: Engineer features
        features = self.feature_engineering(data, *args, **kwargs)
        
        # Step 3: Train or load model
        model = self.train_model(features, *args, **kwargs)
        if model is not None:
            self._model = model
            self._last_trained = datetime.now()
        else:
            model = self._model
        
        # Step 4: Generate predictions
        predictions = self.predict(features, model, *args, **kwargs)
        
        # Add metadata
        predictions['metadata'] = {
            'predictor': self.name,
            'timestamp': datetime.now().isoformat(),
            'pipeline_version': '1.0'
        }
        
        return predictions
    
    def save_model(self, path: Path, model: Any = None) -> None:
        """
        Save trained model to disk.
        
        Args:
            path: Path to save model file
            model: Model to save (uses self._model if None)
        """
        import pickle
        
        model = model or self._model
        if model is None:
            raise ValueError("No model to save")
        
        path = Path(path) if isinstance(path, str) else path
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"[{self.name}] Model saved to {path}")
    
    def load_model(self, path: Path) -> Any:
        """
        Load pre-trained model from disk.
        
        Args:
            path: Path to model file
            
        Returns:
            Loaded model object
        """
        import pickle
        
        path = Path(path) if isinstance(path, str) else path
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        with open(path, 'rb') as f:
            model = pickle.load(f)
        
        self._model = model
        print(f"[{self.name}] Model loaded from {path}")
        return model
    
    def validate_prediction_schema(self, prediction: Dict[str, Any]) -> bool:
        """
        Validate that prediction output matches expected schema.
        
        Args:
            prediction: Prediction dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['sport', 'home_team', 'away_team', 'timestamp']
        
        for field in required_fields:
            if field not in prediction:
                print(f"[{self.name}] Validation failed: Missing field '{field}'")
                return False
        
        return True
    
    def export_prediction(self, prediction: Dict[str, Any], output_path: Path) -> None:
        """
        Export prediction to JSON file.
        
        Args:
            prediction: Prediction dictionary to export
            output_path: Path for output JSON file
        """
        output_path = Path(output_path) if isinstance(output_path, str) else output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(prediction, f, indent=2, default=str)
        
        print(f"[{self.name}] Prediction exported to {output_path}")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get predictor configuration.
        
        Returns:
            Dictionary with predictor configuration parameters
        """
        return {
            'name': self.name,
            'class': self.__class__.__name__,
            'has_model': self._model is not None,
            'last_trained': self._last_trained.isoformat() if self._last_trained else None
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', has_model={self._model is not None})"


# Factory function to get predictor by sport type
def get_predictor(sport: str, **kwargs) -> SportPredictorBase:
    """
    Factory function to create predictor instances by sport type.
    
    Args:
        sport: Sport type ('basketball', 'soccer', 'baseball', 'mlb', 'kbo')
        **kwargs: Additional arguments passed to predictor constructor
        
    Returns:
        SportPredictorBase instance for the specified sport
        
    Raises:
        ValueError: If sport type is not supported
        ImportError: If required dependencies are not installed
    """
    sport = sport.lower().strip()
    
    # Map sport names to predictor classes
    if sport in ['basketball', 'bball', 'hoops']:
        from models.basketball_predictor import BasketballPredictor
        return BasketballPredictor(**kwargs)
    
    elif sport in ['soccer', 'football', 'futbol']:
        from models.soccer_predictor import SoccerPredictor
        return SoccerPredictor(**kwargs)
    
    elif sport in ['baseball', 'mlb', 'kbo']:
        from models.baseball_predictor import BaseballPredictor
        return BaseballPredictor(**kwargs)
    
    else:
        raise ValueError(
            f"Unsupported sport: '{sport}'. "
            "Supported sports: basketball, soccer, baseball/mlb/kbo"
        )


# Convenience function for quick predictions
def quick_predict(
    sport: str,
    home_team: str,
    away_team: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Quick prediction function for common use cases.
    
    Args:
        sport: Sport type
        home_team: Home team name
        away_team: Away team name
        **kwargs: Additional arguments for the predictor
        
    Returns:
        Prediction results dictionary
    """
    predictor = get_predictor(sport, **kwargs)
    return predictor.run_pipeline(
        home_team=home_team,
        away_team=away_team,
        **kwargs
    )


if __name__ == "__main__":
    # Test the factory function
    print("Testing SportPredictorBase factory...")
    
    try:
        # Test basketball predictor
        bball_predictor = get_predictor("basketball")
        print(f"✓ Basketball predictor: {bball_predictor}")
    except Exception as e:
        print(f"✗ Basketball predictor failed: {e}")
    
    try:
        # Test soccer predictor
        soccer_predictor = get_predictor("soccer")
        print(f"✓ Soccer predictor: {soccer_predictor}")
    except Exception as e:
        print(f"✗ Soccer predictor failed: {e}")
    
    try:
        # Test baseball predictor
        baseball_predictor = get_predictor("baseball")
        print(f"✓ Baseball predictor: {baseball_predictor}")
    except Exception as e:
        print(f"✗ Baseball predictor failed: {e}")
    
    print("\nFactory test complete!")