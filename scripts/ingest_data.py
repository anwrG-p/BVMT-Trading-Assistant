"""Comprehensive data ingestion pipeline for BVMT forecasting system."""

from pathlib import Path
import pandas as pd
from typing import Optional
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data import FileLoaderFactory, DataQualityValidator
from src.data.schema import apply_schema, STOCK_SCHEMA, INDEX_SCHEMA
from src.data.dividends import DividendAdjuster
from src.data.adjustments import calculate_log_returns, handle_zero_prices, validate_price_data
from src.utils import logger, config
from tqdm import tqdm


class DataIngestionPipeline:
    """Complete data ingestion pipeline."""
    
    def __init__(self):
        """Initialize pipeline."""
        self.stock_dir = Path(config.get('data.stock_quotation_dir'))
        self.dividends_dir = Path(config.get('data.dividends_dir'))
        self.index_dir = Path(config.get('data.index_dir'))
        self.processed_dir = Path(config.get('data.processed_dir'))
        
        # Create processed directory
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_all_stock_data(self) -> pd.DataFrame:
        """
        Load all stock quotation files and combine.
        
        Returns:
            Combined stock DataFrame
        """
        logger.info("=" * 60)
        logger.info("Loading Stock Quotation Data")
        logger.info("=" * 60)
        
        files = []
        for ext in ['*.txt', '*.csv', '*.xlsx', '*.xls']:
            files.extend(sorted(self.stock_dir.rglob(ext)))
            
        # Filter out system files or temp files
        files = [f for f in files if not f.name.startswith('.')]
        
        all_data = []
        
        for file_path in tqdm(files, desc="Loading stock files"):
            try:
                loader = FileLoaderFactory.create_loader(file_path)
                df = loader.load()
                df = apply_schema(df, STOCK_SCHEMA)
                all_data.append(df)
                logger.info(f"✓ {file_path.name}: {len(df)} rows")
            except Exception as e:
                logger.error(f"✗ {file_path.name}: {str(e)}")
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Sort by symbol and date
        combined_df = combined_df.sort_values(['symbol', 'date'])
        
        # Remove duplicates
        before_dedup = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['date', 'symbol'], keep='last')
        after_dedup = len(combined_df)
        
        if before_dedup > after_dedup:
            logger.warning(f"Removed {before_dedup - after_dedup} duplicate rows")
        
        logger.info(f"Total stock data: {len(combined_df)} rows, {combined_df['symbol'].nunique()} symbols")
        logger.info(f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
        
        return combined_df
    
    def load_all_index_data(self) -> pd.DataFrame:
        """
        Load all TUNINDEX data and combine.
        
        Returns:
            Combined index DataFrame
        """
        logger.info("\n" + "=" * 60)
        logger.info("Loading TUNINDEX Data")
        logger.info("=" * 60)
        
        files = []
        for ext in ['*.txt', '*.csv', '*.xlsx', '*.xls']:
            files.extend(sorted(self.index_dir.rglob(ext)))
            
        # Filter out system files
        files = [f for f in files if not f.name.startswith('.')]
        
        all_data = []
        
        for file_path in tqdm(files, desc="Loading index files"):
            try:
                loader = FileLoaderFactory.create_loader(file_path)
                df = loader.load()
                
                # Handle case where Index file has Stock header format (CODE instead of CODE_INDICE)
                if 'symbol' in df.columns and 'index_code' not in df.columns:
                    df = df.rename(columns={'symbol': 'index_code'})
                    
                # Handle case where Index file has Stock header format (CLOTURE -> close instead of INDICE_JOUR -> value)
                if 'close' in df.columns and 'value' not in df.columns:
                    df = df.rename(columns={'close': 'value'})
                
                df = apply_schema(df, INDEX_SCHEMA)
                
                # Filter for TUNINDEX only (code 905001)
                if 'index_code' in df.columns:
                    # Convert to string to ensure matching
                    df = df[df['index_code'].astype(str) == '905001']
                
                all_data.append(df)
                logger.info(f"✓ {file_path.name}: {len(df)} rows")
            except Exception as e:
                logger.error(f"✗ {file_path.name}: {str(e)}")
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Sort by date
        combined_df = combined_df.sort_values('date')
        
        # Remove duplicates
        combined_df = combined_df.drop_duplicates(subset=['date'], keep='last')
        
        logger.info(f"Total TUNINDEX data: {len(combined_df)} rows")
        logger.info(f"Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
        
        return combined_df
    
    def apply_dividend_adjustments(self, stock_df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply dividend adjustments to stock data.
        
        Args:
            stock_df: Stock DataFrame
            
        Returns:
            DataFrame with adjusted prices
        """
        logger.info("\n" + "=" * 60)
        logger.info("Applying Dividend Adjustments")
        logger.info("=" * 60)
        
        adjuster = DividendAdjuster(self.dividends_dir)
        adjusted_df = adjuster.adjust_prices(stock_df)
        
        # Get summary
        summary = adjuster.get_adjustment_summary(adjusted_df)
        logger.info(f"Adjustment Summary:")
        logger.info(f"  - Total stocks: {summary['total_stocks']}")
        logger.info(f"  - Stocks with adjustments: {summary['stocks_with_adjustments']}")
        logger.info(f"  - Total adjustments: {summary['total_adjustments']}")
        logger.info(f"  - Avg adjustment factor: {summary['avg_adjustment_factor']:.4f}")
        
        return adjusted_df
    
    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate log and simple returns.
        
        Args:
            df: DataFrame with adjusted prices
            
        Returns:
            DataFrame with returns
        """
        logger.info("\n" + "=" * 60)
        logger.info("Calculating Returns")
        logger.info("=" * 60)
        
        df = calculate_log_returns(df, price_column='adj_close', output_column='log_return')
        df = calculate_log_returns(df, price_column='close', output_column='log_return_raw')
        
        logger.info(f"✓ Calculated log returns")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate data.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("\n" + "=" * 60)
        logger.info("Cleaning Data")
        logger.info("=" * 60)
        
        # Handle zero prices
        df = handle_zero_prices(df)
        
        # Validate price data
        df = validate_price_data(df)
        
        # Filter out stocks with insufficient data
        min_days = config.get('data.min_trading_days', 252)
        symbol_counts = df.groupby('symbol').size()
        valid_symbols = symbol_counts[symbol_counts >= min_days].index
        
        before_filter = df['symbol'].nunique()
        df = df[df['symbol'].isin(valid_symbols)]
        after_filter = df['symbol'].nunique()
        
        logger.info(f"Filtered stocks: {before_filter} → {after_filter} (removed {before_filter - after_filter} with <{min_days} days)")
        
        return df
    
    def save_processed_data(
        self,
        stock_df: pd.DataFrame,
        index_df: pd.DataFrame
    ) -> None:
        """
        Save processed data to parquet files.
        
        Args:
            stock_df: Processed stock DataFrame
            index_df: Processed index DataFrame
        """
        logger.info("\n" + "=" * 60)
        logger.info("Saving Processed Data")
        logger.info("=" * 60)
        
        # Save stock data
        stock_path = self.processed_dir / 'stock_data.parquet'
        stock_df.to_parquet(stock_path, index=False)
        logger.info(f"✓ Saved stock data to {stock_path}")
        logger.info(f"  - Size: {stock_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Save index data
        index_path = self.processed_dir / 'tunindex_data.parquet'
        index_df.to_parquet(index_path, index=False)
        logger.info(f"✓ Saved TUNINDEX data to {index_path}")
        logger.info(f"  - Size: {index_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Save metadata
        metadata = {
            'stock_data': {
                'rows': len(stock_df),
                'symbols': stock_df['symbol'].nunique(),
                'date_range': {
                    'start': str(stock_df['date'].min()),
                    'end': str(stock_df['date'].max())
                },
                'columns': stock_df.columns.tolist()
            },
            'index_data': {
                'rows': len(index_df),
                'date_range': {
                    'start': str(index_df['date'].min()),
                    'end': str(index_df['date'].max())
                },
                'columns': index_df.columns.tolist()
            }
        }
        
        import json
        metadata_path = self.processed_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✓ Saved metadata to {metadata_path}")
    
    def run(self) -> None:
        """Run complete ingestion pipeline."""
        logger.info("Starting Data Ingestion Pipeline")
        logger.info("=" * 60)
        
        # Load all data
        stock_df = self.load_all_stock_data()
        index_df = self.load_all_index_data()
        
        # Apply dividend adjustments
        stock_df = self.apply_dividend_adjustments(stock_df)
        
        # Calculate returns
        stock_df = self.calculate_returns(stock_df)
        
        # Clean data
        stock_df = self.clean_data(stock_df)
        
        # Save processed data
        self.save_processed_data(stock_df, index_df)
        
        logger.info("\n" + "=" * 60)
        logger.info("Data Ingestion Pipeline Complete!")
        logger.info("=" * 60)


if __name__ == '__main__':
    pipeline = DataIngestionPipeline()
    pipeline.run()
