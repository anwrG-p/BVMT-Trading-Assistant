"""Training orchestrator for BVMT forecasting models."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.price_forecaster import MultiHorizonForecaster
from src.models.volume_forecaster import MultiHorizonVolumeForecaster
from src.utils import logger, config


class ModelTrainer:
    """Orchestrate model training for price and volume forecasting."""
    
    def __init__(self, config_dict: Optional[dict] = None):
        """
        Initialize model trainer.
        
        Args:
            config_dict: Configuration dictionary (default: load from config)
        """
        if config_dict is None:
            config_dict = config.get('models', {})
        
        self.config = config_dict
        self.processed_dir = Path(config.get('data.processed_dir'))
        self.models_dir = Path(config.get('models.save_dir', 'models'))
        
        # Create models directory
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Models
        self.price_forecaster = None
        self.volume_forecaster = None
    
    def load_features(self) -> pd.DataFrame:
        """
        Load feature matrix.
        
        Returns:
            DataFrame with features
        """
        logger.info("Loading features...")
        
        features_path = self.processed_dir / 'features.parquet'
        
        if not features_path.exists():
            raise FileNotFoundError(f"Features not found: {features_path}")
        
        df = pd.read_parquet(features_path)
        
        logger.info(f"Loaded features: {len(df)} rows, {len(df.columns)} columns")
        logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
        logger.info(f"Symbols: {df['symbol'].nunique()}")
        
        return df
    
    def create_train_test_split(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create time-based train/test split.
        
        Args:
            df: DataFrame with features
            test_size: Proportion of data for testing
            
        Returns:
            (train_df, test_df)
        """
        # Sort by date
        df = df.sort_values('date')
        
        # Calculate split point
        split_idx = int(len(df) * (1 - test_size))
        split_date = df.iloc[split_idx]['date']
        
        # Split
        train_df = df[df['date'] < split_date].copy()
        test_df = df[df['date'] >= split_date].copy()
        
        logger.info(f"Train/Test Split:")
        logger.info(f"  Train: {len(train_df)} rows ({train_df['date'].min()} to {train_df['date'].max()})")
        logger.info(f"  Test:  {len(test_df)} rows ({test_df['date'].min()} to {test_df['date'].max()})")
        
        return train_df, test_df
    
    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of feature columns (exclude metadata).
        
        Args:
            df: DataFrame with features
            
        Returns:
            List of feature column names
        """
        # Exclude metadata columns
        exclude_cols = [
            'date', 'symbol', 'name', 'group',
            'open', 'high', 'low', 'close',
            'volume', 'num_trades', 'turnover',
            'adj_close', 'adj_open', 'adj_high', 'adj_low',
            'log_return', 'log_return_raw',
            'liquidity_regime', 'volatility_regime'
        ]
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Filter for numeric columns only to avoid XGBoost errors with object/string columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        feature_cols = [col for col in feature_cols if col in numeric_cols]
        
        logger.info(f"Feature columns: {len(feature_cols)}")
        
        return feature_cols
    
    def train_price_models(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        feature_columns: List[str]
    ) -> None:
        """
        Train price forecasting models.
        
        Args:
            train_df: Training data
            test_df: Test data
            feature_columns: List of feature columns
        """
        logger.info("\n" + "=" * 60)
        logger.info("Training Price Forecasting Models")
        logger.info("=" * 60)
        
        # Get hyperparameters from config
        horizons = self.config.get('horizons', [1, 2, 3, 4, 5])
        quantiles = self.config.get('quantiles', [0.025, 0.1, 0.5, 0.9, 0.975])
        
        xgb_params = {
            'max_depth': self.config.get('xgb_max_depth', 6),
            'learning_rate': self.config.get('xgb_learning_rate', 0.05),
            'n_estimators': self.config.get('xgb_n_estimators', 500),
            'subsample': self.config.get('xgb_subsample', 0.8),
            'colsample_bytree': self.config.get('xgb_colsample_bytree', 0.8)
        }
        
        # Create forecaster
        self.price_forecaster = MultiHorizonForecaster(
            horizons=horizons,
            quantiles=quantiles,
            **xgb_params
        )
        
        # Fit
        self.price_forecaster.fit(
            train_df,
            feature_columns=feature_columns,
            target_column='log_return'
        )
        
        # Save
        price_models_dir = self.models_dir / 'price'
        self.price_forecaster.save(price_models_dir)
        
        logger.info(f"✓ Price models saved to {price_models_dir}")
    
    def train_volume_models(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        feature_columns: List[str]
    ) -> None:
        """
        Train volume forecasting models.
        
        Args:
            train_df: Training data
            test_df: Test data
            feature_columns: List of feature columns
        """
        logger.info("\n" + "=" * 60)
        logger.info("Training Volume Forecasting Models")
        logger.info("=" * 60)
        
        # Get hyperparameters from config
        horizons = self.config.get('horizons', [1, 2, 3, 4, 5])
        
        xgb_params = {
            'max_depth': self.config.get('volume_xgb_max_depth', 5),
            'learning_rate': self.config.get('volume_xgb_learning_rate', 0.05),
            'n_estimators': self.config.get('volume_xgb_n_estimators', 300),
            'subsample': self.config.get('volume_xgb_subsample', 0.8),
            'colsample_bytree': self.config.get('volume_xgb_colsample_bytree', 0.8)
        }
        
        # Create forecaster
        self.volume_forecaster = MultiHorizonVolumeForecaster(
            horizons=horizons,
            **xgb_params
        )
        
        # Fit
        self.volume_forecaster.fit(
            train_df,
            feature_columns=feature_columns,
            volume_column='volume'
        )
        
        # Save
        volume_models_dir = self.models_dir / 'volume'
        self.volume_forecaster.save(volume_models_dir)
        
        logger.info(f"✓ Volume models saved to {volume_models_dir}")
    
    def run(self) -> None:
        """Run complete training pipeline."""
        logger.info("=" * 60)
        logger.info("Starting Model Training Pipeline")
        logger.info("=" * 60)
        
        # Load features
        df = self.load_features()
        
        # Sanitize features (replace inf with nan)
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Create train/test split
        train_df, test_df = self.create_train_test_split(df)
        
        # Get feature columns
        feature_columns = self.get_feature_columns(df)
        
        # Train price models
        self.train_price_models(train_df, test_df, feature_columns)
        
        # Train volume models
        self.train_volume_models(train_df, test_df, feature_columns)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Model Training Pipeline Complete!")
        logger.info("=" * 60)


if __name__ == '__main__':
    trainer = ModelTrainer()
    trainer.run()
