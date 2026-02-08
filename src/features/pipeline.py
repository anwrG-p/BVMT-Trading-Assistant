"""Feature engineering pipeline orchestrator."""

import pandas as pd
from pathlib import Path
from typing import Optional
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.features.price_features import calculate_all_price_features
from src.features.volume_features import calculate_all_volume_features
from src.features.market_features import calculate_all_market_features
from src.features.calendar_features import calculate_all_calendar_features
from src.utils import logger, config


class FeaturePipeline:
    """Orchestrate all feature engineering steps."""
    
    def __init__(self, config_dict: Optional[dict] = None):
        """
        Initialize feature pipeline.
        
        Args:
            config_dict: Configuration dictionary (default: load from config)
        """
        if config_dict is None:
            config_dict = config.get('features', {})
        
        self.config = config_dict
        self.processed_dir = Path(config.get('data.processed_dir'))
    
    def load_processed_data(self) -> tuple:
        """
        Load processed stock and index data.
        
        Returns:
            (stock_df, index_df)
        """
        logger.info("Loading processed data...")
        
        stock_path = self.processed_dir / 'stock_data.parquet'
        index_path = self.processed_dir / 'tunindex_data.parquet'
        
        if not stock_path.exists():
            raise FileNotFoundError(f"Stock data not found: {stock_path}")
        
        stock_df = pd.read_parquet(stock_path)
        logger.info(f"Loaded stock data: {len(stock_df)} rows, {stock_df['symbol'].nunique()} symbols")
        
        index_df = None
        if index_path.exists():
            index_df = pd.read_parquet(index_path)
            logger.info(f"Loaded index data: {len(index_df)} rows")
        else:
            logger.warning(f"Index data not found: {index_path}")
        
        return stock_df, index_df
    
    def generate_features(
        self,
        stock_df: pd.DataFrame,
        index_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Generate all features.
        
        Args:
            stock_df: Stock DataFrame
            index_df: Index DataFrame (optional)
            
        Returns:
            DataFrame with all features
        """
        logger.info("=" * 60)
        logger.info("Starting Feature Engineering")
        logger.info("=" * 60)
        
        # Price features
        stock_df = calculate_all_price_features(stock_df, self.config)
        
        # Volume features
        stock_df = calculate_all_volume_features(stock_df, self.config)
        
        # Market features
        stock_df = calculate_all_market_features(stock_df, index_df, self.config)
        
        # Calendar features
        stock_df = calculate_all_calendar_features(stock_df, self.config)
        
        # Sanitize features (replace inf with nan globally)
        stock_df = stock_df.replace([float('inf'), float('-inf')], float('nan'))
        
        logger.info("=" * 60)
        logger.info(f"Feature Engineering Complete!")
        logger.info(f"Total features: {len(stock_df.columns)}")
        logger.info("=" * 60)
        
        return stock_df
    
    def drop_insufficient_history(
        self,
        df: pd.DataFrame,
        lookback_window: int = None
    ) -> pd.DataFrame:
        """
        Drop rows with insufficient history for features.
        
        Args:
            df: DataFrame with features
            lookback_window: Minimum lookback window (default: from config)
            
        Returns:
            DataFrame with insufficient history dropped
        """
        if lookback_window is None:
            lookback_window = self.config.get('lookback_window', 60)
        
        before_count = len(df)
        
        # Drop first N rows per symbol
        df = df.groupby('symbol').apply(
            lambda x: x.iloc[lookback_window:]
        ).reset_index(drop=True)
        
        after_count = len(df)
        dropped = before_count - after_count
        
        logger.info(f"Dropped {dropped} rows with insufficient history (lookback={lookback_window})")
        
        return df
    
    def save_features(
        self,
        df: pd.DataFrame,
        output_path: Optional[Path] = None
    ) -> None:
        """
        Save feature matrix to file.
        
        Args:
            df: DataFrame with features
            output_path: Output file path (default: processed_dir/features.parquet)
        """
        if output_path is None:
            output_path = self.processed_dir / 'features.parquet'
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to parquet
        df.to_parquet(output_path, index=False)
        
        logger.info(f"✓ Saved features to {output_path}")
        logger.info(f"  - Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        logger.info(f"  - Rows: {len(df)}")
        logger.info(f"  - Columns: {len(df.columns)}")
        
        # Save feature list
        feature_list_path = output_path.parent / 'feature_list.txt'
        with open(feature_list_path, 'w') as f:
            for col in sorted(df.columns):
                f.write(f"{col}\n")
        
        logger.info(f"✓ Saved feature list to {feature_list_path}")
    
    def run(self) -> pd.DataFrame:
        """
        Run complete feature engineering pipeline.
        
        Returns:
            DataFrame with all features
        """
        # Load data
        stock_df, index_df = self.load_processed_data()
        
        # Generate features
        features_df = self.generate_features(stock_df, index_df)
        
        # Drop insufficient history
        features_df = self.drop_insufficient_history(features_df)
        
        # Save features
        self.save_features(features_df)
        
        return features_df


if __name__ == '__main__':
    pipeline = FeaturePipeline()
    features_df = pipeline.run()
    
    print("\n" + "=" * 60)
    print("Feature Engineering Summary")
    print("=" * 60)
    print(f"Total rows: {len(features_df)}")
    print(f"Total symbols: {features_df['symbol'].nunique()}")
    print(f"Total features: {len(features_df.columns)}")
    print(f"Date range: {features_df['date'].min()} to {features_df['date'].max()}")
    print("=" * 60)
