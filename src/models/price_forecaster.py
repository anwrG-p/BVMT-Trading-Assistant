"""XGBoost quantile regression models for price forecasting."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import xgboost as xgb
from tqdm import tqdm

from src.models.base import QuantileForecaster
from src.utils import logger


class XGBQuantileForecaster(QuantileForecaster):
    """XGBoost quantile regression for multi-horizon forecasting."""
    
    def __init__(
        self,
        horizon: int = 1,
        quantiles: List[float] = [0.025, 0.1, 0.5, 0.9, 0.975],
        **xgb_params
    ):
        """
        Initialize XGBoost quantile forecaster.
        
        Args:
            horizon: Forecast horizon in days
            quantiles: List of quantiles to predict
            **xgb_params: XGBoost parameters
        """
        super().__init__(f"xgb_h{horizon}", quantiles)
        self.horizon = horizon
        
        # Default XGBoost parameters
        self.xgb_params = {
            'objective': 'reg:quantileerror',
            'tree_method': 'hist',
            'max_depth': 6,
            'learning_rate': 0.05,
            'n_estimators': 500,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'n_jobs': -1
        }
        
        # Update with user-provided parameters
        self.xgb_params.update(xgb_params)
    
    def create_target(
        self,
        df: pd.DataFrame,
        target_column: str = 'log_return'
    ) -> pd.Series:
        """
        Create target variable for given horizon.
        
        Args:
            df: DataFrame with returns
            target_column: Column to use as target
            
        Returns:
            Target series shifted by horizon
        """
        # Shift returns by horizon (negative shift = future values)
        target = df.groupby('symbol')[target_column].shift(-self.horizon)
        
        return target
    
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        eval_set: Optional[List[tuple]] = None,
        early_stopping_rounds: int = 50,
        verbose: bool = False
    ) -> 'XGBQuantileForecaster':
        """
        Fit XGBoost models for all quantiles.
        
        Args:
            X: Feature matrix
            y: Target variable
            eval_set: Validation set for early stopping
            early_stopping_rounds: Early stopping rounds
            verbose: Verbose training
            
        Returns:
            self
        """
        logger.info(f"Training {self.model_name} for {len(self.quantiles)} quantiles...")
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Remove NaN targets (from shifting)
        valid_idx = ~y.isna()
        X_train = X[valid_idx]
        y_train = y[valid_idx]
        
        logger.info(f"Training samples: {len(X_train)} (removed {(~valid_idx).sum()} NaN targets)")
        
        # Train one model per quantile
        for quantile in tqdm(self.quantiles, desc="Training quantiles"):
            # Set quantile parameter
            params = self.xgb_params.copy()
            params['quantile_alpha'] = quantile
            
            # Create model
            model = xgb.XGBRegressor(**params)
            
            # Fit model
            if eval_set is not None:
                model.fit(
                    X_train,
                    y_train,
                    eval_set=eval_set,
                    early_stopping_rounds=early_stopping_rounds,
                    verbose=verbose
                )
            else:
                model.fit(X_train, y_train, verbose=verbose)
            
            self.models[quantile] = model
            
            logger.debug(f"Trained quantile {quantile:.3f}")
        
        self.is_fitted = True
        logger.info(f"✓ {self.model_name} training complete")
        
        return self
    
    def get_feature_importance(self, quantile: float = 0.5) -> pd.DataFrame:
        """
        Get feature importance for a specific quantile.
        
        Args:
            quantile: Quantile to get importance for (default: median)
            
        Returns:
            DataFrame with feature importance
        """
        if not self.is_fitted:
            logger.warning("Model not fitted yet")
            return None
        
        if quantile not in self.models:
            logger.warning(f"Quantile {quantile} not available")
            return None
        
        model = self.models[quantile]
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df


class MultiHorizonForecaster:
    """Multi-horizon forecaster combining multiple XGBoost models."""
    
    def __init__(
        self,
        horizons: List[int] = [1, 2, 3, 4, 5],
        quantiles: List[float] = [0.025, 0.1, 0.5, 0.9, 0.975],
        **xgb_params
    ):
        """
        Initialize multi-horizon forecaster.
        
        Args:
            horizons: List of forecast horizons
            quantiles: List of quantiles to predict
            **xgb_params: XGBoost parameters
        """
        self.horizons = horizons
        self.quantiles = quantiles
        self.xgb_params = xgb_params
        self.models = {}  # horizon -> XGBQuantileForecaster
    
    def fit(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_column: str = 'log_return',
        **fit_kwargs
    ) -> 'MultiHorizonForecaster':
        """
        Fit models for all horizons.
        
        Args:
            df: DataFrame with features and target
            feature_columns: List of feature column names
            target_column: Target column name
            **fit_kwargs: Additional fit arguments
            
        Returns:
            self
        """
        logger.info("=" * 60)
        logger.info(f"Training Multi-Horizon Forecaster")
        logger.info(f"Horizons: {self.horizons}")
        logger.info(f"Quantiles: {self.quantiles}")
        logger.info("=" * 60)
        
        X = df[feature_columns]
        
        for horizon in self.horizons:
            logger.info(f"\nTraining horizon {horizon}...")
            
            # Create forecaster for this horizon
            forecaster = XGBQuantileForecaster(
                horizon=horizon,
                quantiles=self.quantiles,
                **self.xgb_params
            )
            
            # Create target
            y = forecaster.create_target(df, target_column)
            
            # Fit
            forecaster.fit(X, y, **fit_kwargs)
            
            self.models[horizon] = forecaster
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Multi-Horizon Training Complete!")
        logger.info("=" * 60)
        
        return self
    
    def predict(
        self,
        X: pd.DataFrame,
        horizons: Optional[List[int]] = None
    ) -> Dict[int, Dict[float, np.ndarray]]:
        """
        Predict all horizons and quantiles.
        
        Args:
            X: Feature matrix
            horizons: Specific horizons to predict (default: all)
            
        Returns:
            Dictionary mapping horizon -> quantile -> predictions
        """
        if horizons is None:
            horizons = self.horizons
        
        predictions = {}
        
        for horizon in horizons:
            if horizon not in self.models:
                logger.warning(f"Horizon {horizon} not available")
                continue
            
            predictions[horizon] = self.models[horizon].predict(X)
        
        return predictions
    
    def predict_intervals(
        self,
        X: pd.DataFrame,
        confidence_levels: List[float] = [0.80, 0.95],
        horizons: Optional[List[int]] = None
    ) -> Dict[int, Dict[float, tuple]]:
        """
        Predict confidence intervals for all horizons.
        
        Args:
            X: Feature matrix
            confidence_levels: List of confidence levels
            horizons: Specific horizons to predict (default: all)
            
        Returns:
            Dictionary mapping horizon -> confidence level -> (lower, upper)
        """
        if horizons is None:
            horizons = self.horizons
        
        intervals = {}
        
        for horizon in horizons:
            if horizon not in self.models:
                logger.warning(f"Horizon {horizon} not available")
                continue
            
            intervals[horizon] = self.models[horizon].predict_intervals(
                X, confidence_levels
            )
        
        return intervals
    
    def save(self, output_dir: str) -> None:
        """
        Save all horizon models.
        
        Args:
            output_dir: Output directory
        """
        from pathlib import Path
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for horizon, model in self.models.items():
            model_path = output_dir / f"xgb_h{horizon}.pkl"
            model.save(model_path)
        
        logger.info(f"Saved {len(self.models)} models to {output_dir}")
    
    def load(self, input_dir: str) -> 'MultiHorizonForecaster':
        """
        Load all horizon models.
        
        Args:
            input_dir: Input directory
            
        Returns:
            self
        """
        from pathlib import Path
        
        input_dir = Path(input_dir)
        
        for horizon in self.horizons:
            model_path = input_dir / f"xgb_h{horizon}.pkl"
            
            if not model_path.exists():
                logger.warning(f"Model not found: {model_path}")
                continue
            
            forecaster = XGBQuantileForecaster(horizon=horizon, quantiles=self.quantiles)
            forecaster.load(model_path)
            
            self.models[horizon] = forecaster
        
        logger.info(f"Loaded {len(self.models)} models from {input_dir}")
        
        return self
