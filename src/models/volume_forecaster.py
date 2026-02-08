"""Volume forecasting model with liquidity classification."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import xgboost as xgb

from src.models.base import BaseForecaster
from src.utils import logger


class VolumeForecaster(BaseForecaster):
    """Volume forecaster with liquidity regime classification."""
    
    def __init__(
        self,
        horizon: int = 1,
        **xgb_params
    ):
        """
        Initialize volume forecaster.
        
        Args:
            horizon: Forecast horizon in days
            **xgb_params: XGBoost parameters
        """
        super().__init__(f"volume_h{horizon}")
        self.horizon = horizon
        
        # Default XGBoost parameters for volume
        self.xgb_params = {
            'objective': 'reg:squarederror',
            'tree_method': 'hist',
            'max_depth': 5,
            'learning_rate': 0.05,
            'n_estimators': 300,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 5,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'n_jobs': -1
        }
        
        # Update with user-provided parameters
        self.xgb_params.update(xgb_params)
        
        # Liquidity thresholds (will be set during training)
        self.q20_threshold = None
        self.q80_threshold = None
    
    def create_target(
        self,
        df: pd.DataFrame,
        target_column: str = 'volume'
    ) -> pd.Series:
        """
        Create target variable for given horizon.
        
        Uses log(volume) for better distribution.
        
        Args:
            df: DataFrame with volume
            target_column: Column to use as target
            
        Returns:
            Target series shifted by horizon
        """
        # Use log volume for better distribution
        log_volume = np.log1p(df[target_column])
        
        # Shift by horizon
        target = df.groupby('symbol')[target_column].shift(-self.horizon)
        
        # Convert to log
        target = np.log1p(target)
        
        return target
    
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        volume_data: pd.Series,
        eval_set: Optional[List[tuple]] = None,
        early_stopping_rounds: int = 50,
        verbose: bool = False
    ) -> 'VolumeForecaster':
        """
        Fit volume forecasting model.
        
        Args:
            X: Feature matrix
            y: Target variable (log volume)
            volume_data: Original volume data for threshold calculation
            eval_set: Validation set for early stopping
            early_stopping_rounds: Early stopping rounds
            verbose: Verbose training
            
        Returns:
            self
        """
        logger.info(f"Training {self.model_name}...")
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Remove NaN targets
        valid_idx = ~y.isna()
        X_train = X[valid_idx]
        y_train = y[valid_idx]
        
        logger.info(f"Training samples: {len(X_train)}")
        
        # Calculate liquidity thresholds from training data
        self.q20_threshold = volume_data[valid_idx].quantile(0.20)
        self.q80_threshold = volume_data[valid_idx].quantile(0.80)
        
        logger.info(f"Liquidity thresholds: Q20={self.q20_threshold:.0f}, Q80={self.q80_threshold:.0f}")
        
        # Create model
        self.model = xgb.XGBRegressor(**self.xgb_params)
        
        # Fit model
        if eval_set is not None:
            self.model.fit(
                X_train,
                y_train,
                eval_set=eval_set,
                early_stopping_rounds=early_stopping_rounds,
                verbose=verbose
            )
        else:
            self.model.fit(X_train, y_train, verbose=verbose)
        
        self.is_fitted = True
        logger.info(f"✓ {self.model_name} training complete")
        
        return self
    
    def predict(
        self,
        X: pd.DataFrame,
        return_log: bool = False
    ) -> np.ndarray:
        """
        Predict volume.
        
        Args:
            X: Feature matrix
            return_log: If True, return log(volume), else return volume
            
        Returns:
            Volume predictions
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted yet")
        
        # Predict log volume
        log_volume_pred = self.model.predict(X)
        
        if return_log:
            return log_volume_pred
        else:
            # Convert back to volume
            return np.expm1(log_volume_pred)
    
    def predict_liquidity_regime(
        self,
        X: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict volume and classify liquidity regime.
        
        Args:
            X: Feature matrix
            
        Returns:
            (volume_predictions, regime_labels)
            regime_labels: 0=Low, 1=Normal, 2=High
        """
        # Predict volume
        volume_pred = self.predict(X, return_log=False)
        
        # Classify regime
        # Classify regime
        regime = np.ones(len(volume_pred), dtype=int)  # Default: Normal
        
        if self.q20_threshold is not None and self.q80_threshold is not None:
            regime[volume_pred < self.q20_threshold] = 0  # Low
            regime[volume_pred > self.q80_threshold] = 2  # High
        else:
            # Only warn once per prediction batch to avoid spam
            pass
        
        return volume_pred, regime
    
    def get_regime_name(self, regime_code: int) -> str:
        """
        Get regime name from code.
        
        Args:
            regime_code: 0, 1, or 2
            
        Returns:
            Regime name
        """
    def save(self, path: "Path") -> None:
        """Save model and thresholds."""
        from pathlib import Path
        import joblib
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'model_name': self.model_name,
            'is_fitted': self.is_fitted,
            'q20_threshold': self.q20_threshold,
            'q80_threshold': self.q80_threshold,
            'horizon': self.horizon,
            'xgb_params': self.xgb_params
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Saved model to {path}")

    def load(self, path: "Path") -> "VolumeForecaster":
        """Load model and thresholds."""
        from pathlib import Path
        import joblib
        
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {path}")
        
        model_data = joblib.load(path)
        
        # Handle both base class save format and new format
        if 'q20_threshold' in model_data:
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.model_name = model_data['model_name']
            self.is_fitted = model_data['is_fitted']
            self.q20_threshold = model_data['q20_threshold']
            self.q80_threshold = model_data['q80_threshold']
            self.horizon = model_data.get('horizon', self.horizon)
            self.xgb_params = model_data.get('xgb_params', self.xgb_params)
            logger.info(f"Loaded model from {path} (with thresholds)")
        else:
            # Fallback for old models
            super().load(path)
            logger.warning(f"Loaded model from {path} (missing thresholds)")
            
        return self


class MultiHorizonVolumeForecaster:
    """Multi-horizon volume forecaster."""
    
    def __init__(
        self,
        horizons: List[int] = [1, 2, 3, 4, 5],
        **xgb_params
    ):
        """
        Initialize multi-horizon volume forecaster.
        
        Args:
            horizons: List of forecast horizons
            **xgb_params: XGBoost parameters
        """
        self.horizons = horizons
        self.xgb_params = xgb_params
        self.models = {}  # horizon -> VolumeForecaster
    
    def fit(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        volume_column: str = 'volume',
        **fit_kwargs
    ) -> 'MultiHorizonVolumeForecaster':
        """
        Fit models for all horizons.
        
        Args:
            df: DataFrame with features and volume
            feature_columns: List of feature column names
            volume_column: Volume column name
            **fit_kwargs: Additional fit arguments
            
        Returns:
            self
        """
        logger.info("=" * 60)
        logger.info(f"Training Multi-Horizon Volume Forecaster")
        logger.info(f"Horizons: {self.horizons}")
        logger.info("=" * 60)
        
        X = df[feature_columns]
        volume_data = df[volume_column]
        
        for horizon in self.horizons:
            logger.info(f"\nTraining horizon {horizon}...")
            
            # Create forecaster for this horizon
            forecaster = VolumeForecaster(
                horizon=horizon,
                **self.xgb_params
            )
            
            # Create target
            y = forecaster.create_target(df, volume_column)
            
            # Fit
            forecaster.fit(X, y, volume_data, **fit_kwargs)
            
            self.models[horizon] = forecaster
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Multi-Horizon Volume Training Complete!")
        logger.info("=" * 60)
        
        return self
    
    def predict(
        self,
        X: pd.DataFrame,
        horizons: Optional[List[int]] = None
    ) -> Dict[int, np.ndarray]:
        """
        Predict volume for all horizons.
        
        Args:
            X: Feature matrix
            horizons: Specific horizons to predict (default: all)
            
        Returns:
            Dictionary mapping horizon -> volume predictions
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
    
    def predict_liquidity_regime(
        self,
        X: pd.DataFrame,
        horizons: Optional[List[int]] = None
    ) -> Dict[int, Tuple[np.ndarray, np.ndarray]]:
        """
        Predict volume and liquidity regime for all horizons.
        
        Args:
            X: Feature matrix
            horizons: Specific horizons to predict (default: all)
            
        Returns:
            Dictionary mapping horizon -> (volume, regime)
        """
        if horizons is None:
            horizons = self.horizons
        
        predictions = {}
        
        for horizon in horizons:
            if horizon not in self.models:
                logger.warning(f"Horizon {horizon} not available")
                continue
            
            predictions[horizon] = self.models[horizon].predict_liquidity_regime(X)
        
        return predictions
    
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
            model_path = output_dir / f"volume_h{horizon}.pkl"
            model.save(model_path)
        
        logger.info(f"Saved {len(self.models)} volume models to {output_dir}")
    
    def load(self, input_dir: str) -> 'MultiHorizonVolumeForecaster':
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
            model_path = input_dir / f"volume_h{horizon}.pkl"
            
            if not model_path.exists():
                logger.warning(f"Model not found: {model_path}")
                continue
            
            forecaster = VolumeForecaster(horizon=horizon)
            forecaster.load(model_path)
            
            self.models[horizon] = forecaster
        
        logger.info(f"Loaded {len(self.models)} volume models from {input_dir}")
        
        return self
