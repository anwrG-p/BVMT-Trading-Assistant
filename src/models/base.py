"""Base forecaster interface for BVMT models."""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import joblib

from src.utils import logger


class BaseForecaster(ABC):
    """Abstract base class for all forecasting models."""
    
    def __init__(self, model_name: str):
        """
        Initialize forecaster.
        
        Args:
            model_name: Name of the model
        """
        self.model_name = model_name
        self.model = None
        self.feature_names = None
        self.is_fitted = False
    
    @abstractmethod
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        **kwargs
    ) -> 'BaseForecaster':
        """
        Fit the model.
        
        Args:
            X: Feature matrix
            y: Target variable
            **kwargs: Additional arguments
            
        Returns:
            self
        """
        pass
    
    @abstractmethod
    def predict(
        self,
        X: pd.DataFrame,
        **kwargs
    ) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Feature matrix
            **kwargs: Additional arguments
            
        Returns:
            Predictions array
        """
        pass
    
    def save(self, path: Path) -> None:
        """
        Save model to disk.
        
        Args:
            path: Path to save model
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'model_name': self.model_name,
            'is_fitted': self.is_fitted
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Saved model to {path}")
    
    def load(self, path: Path) -> 'BaseForecaster':
        """
        Load model from disk.
        
        Args:
            path: Path to load model from
            
        Returns:
            self
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")
        
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.model_name = model_data['model_name']
        self.is_fitted = model_data['is_fitted']
        
        logger.info(f"Loaded model from {path}")
        
        return self
    
    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Get feature importance if available.
        
        Returns:
            DataFrame with feature importance or None
        """
        if not self.is_fitted:
            logger.warning("Model not fitted yet")
            return None
        
        if not hasattr(self.model, 'feature_importances_'):
            logger.warning(f"Model {self.model_name} does not support feature importance")
            return None
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df


class QuantileForecaster(BaseForecaster):
    """Quantile regression forecaster for confidence intervals."""
    
    def __init__(
        self,
        model_name: str,
        quantiles: List[float] = [0.025, 0.1, 0.5, 0.9, 0.975]
    ):
        """
        Initialize quantile forecaster.
        
        Args:
            model_name: Name of the model
            quantiles: List of quantiles to predict
        """
        super().__init__(model_name)
        self.quantiles = quantiles
        self.models = {}  # One model per quantile
    
    @abstractmethod
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        **kwargs
    ) -> 'QuantileForecaster':
        """Fit models for all quantiles."""
        pass
    
    def predict(
        self,
        X: pd.DataFrame,
        return_quantiles: bool = True
    ) -> Dict[float, np.ndarray]:
        """
        Predict all quantiles.
        
        Args:
            X: Feature matrix
            return_quantiles: If True, return dict of quantiles
            
        Returns:
            Dictionary mapping quantile -> predictions
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted yet")
        
        predictions = {}
        
        for quantile, model in self.models.items():
            predictions[quantile] = model.predict(X)
        
        return predictions
    
    def predict_intervals(
        self,
        X: pd.DataFrame,
        confidence_levels: List[float] = [0.80, 0.95]
    ) -> Dict[float, Tuple[np.ndarray, np.ndarray]]:
        """
        Predict confidence intervals.
        
        Args:
            X: Feature matrix
            confidence_levels: List of confidence levels (e.g., [0.80, 0.95])
            
        Returns:
            Dictionary mapping confidence level -> (lower, upper) bounds
        """
        predictions = self.predict(X)
        intervals = {}
        
        for conf_level in confidence_levels:
            alpha = 1 - conf_level
            lower_q = alpha / 2
            upper_q = 1 - (alpha / 2)
            
            # Find closest available quantile
            def find_closest_quantile(target_q, available_qs):
                if not available_qs:
                    return None
                closest = min(available_qs, key=lambda x: abs(x - target_q))
                if abs(closest - target_q) < 1e-6:
                    return closest
                return None

            available_quantiles = list(predictions.keys())
            
            actual_lower_q = find_closest_quantile(lower_q, available_quantiles)
            actual_upper_q = find_closest_quantile(upper_q, available_quantiles)
            
            if actual_lower_q is None or actual_upper_q is None:
                logger.warning(f"Quantiles {lower_q:.3f}, {upper_q:.3f} not found for {conf_level} CI. Available: {available_quantiles}")
                continue
            
            intervals[conf_level] = (
                predictions[actual_lower_q],
                predictions[actual_upper_q]
            )
        
        return intervals
    
    def save(self, path: Path) -> None:
        """Save all quantile models."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'models': self.models,
            'feature_names': self.feature_names,
            'model_name': self.model_name,
            'quantiles': self.quantiles,
            'is_fitted': self.is_fitted
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Saved quantile models to {path}")
    
    def load(self, path: Path) -> 'QuantileForecaster':
        """Load all quantile models."""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")
        
        model_data = joblib.load(path)
        
        self.models = model_data['models']
        self.feature_names = model_data['feature_names']
        self.model_name = model_data['model_name']
        self.quantiles = model_data['quantiles']
        self.is_fitted = model_data['is_fitted']
        
        logger.info(f"Loaded quantile models from {path}")
        
        return self
