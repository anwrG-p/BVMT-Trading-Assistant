"""Dividend adjustment engine for BVMT forecasting system."""

from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import numpy as np

from src.utils import logger, DataLoadError
from src.data import FileLoaderFactory


class DividendAdjuster:
    """Calculate dividend-adjusted close prices."""
    
    def __init__(self, dividends_dir: Path):
        """
        Initialize dividend adjuster.
        
        Args:
            dividends_dir: Directory containing dividend Excel files
        """
        self.dividends_dir = Path(dividends_dir)
        self.dividends_df: Optional[pd.DataFrame] = None
    
    def load_all_dividends(self) -> pd.DataFrame:
        """
        Load all dividend files and combine into single DataFrame.
        
        Returns:
            Combined dividend DataFrame
        """
        logger.info("Loading all dividend files...")
        
        all_dividends = []
        
        # Load all .xls and .xlsx files
        files = sorted(self.dividends_dir.glob('*.xls')) + sorted(self.dividends_dir.glob('*.xlsx'))
        
        for file_path in files:
            try:
                loader = FileLoaderFactory.create_loader(file_path)
                df = loader.load()
                
                # Extract year from filename
                year = file_path.stem
                df['year'] = year
                
                all_dividends.append(df)
                logger.debug(f"Loaded {len(df)} dividends from {file_path.name}")
                
            except Exception as e:
                logger.warning(f"Failed to load {file_path.name}: {str(e)}")
        
        if not all_dividends:
            raise DataLoadError("No dividend files could be loaded")
        
        # Combine all dividends
        self.dividends_df = pd.concat(all_dividends, ignore_index=True)
        
        logger.info(f"Loaded {len(self.dividends_df)} total dividend records from {len(files)} files")
        
        return self.dividends_df
    
    def standardize_dividend_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize dividend data columns.
        
        Args:
            df: Raw dividend DataFrame
            
        Returns:
            Standardized dividend DataFrame
        """
        # Common column name variations
        column_mappings = {
            # Symbol variations
            'CODE': 'symbol',
            'Code': 'symbol',
            'SYMBOLE': 'symbol',
            'Symbole': 'symbol',
            'VALEUR': 'symbol',
            
            # Company name variations
            'SOCIETE': 'company',
            'Société': 'company',
            'RAISON_SOCIALE': 'company',
            'NOM': 'company',
            
            # Ex-date variations
            'DATE_DETACHEMENT': 'ex_date',
            'Date Détachement': 'ex_date',
            'EX_DATE': 'ex_date',
            'DATE': 'ex_date',
            
            # Dividend amount variations
            'DIVIDENDE': 'dividend',
            'Dividende': 'dividend',
            'MONTANT': 'dividend',
            'Montant': 'dividend',
            'DIVIDEND': 'dividend',
        }
        
        # Rename columns
        df_std = df.copy()
        for old_col, new_col in column_mappings.items():
            if old_col in df_std.columns:
                df_std = df_std.rename(columns={old_col: new_col})
        
        # Ensure required columns exist
        required_cols = ['symbol', 'ex_date', 'dividend']
        missing_cols = [col for col in required_cols if col not in df_std.columns]
        
        if missing_cols:
            logger.warning(f"Missing columns in dividend data: {missing_cols}")
            logger.warning(f"Available columns: {df_std.columns.tolist()}")
            # Try to infer from available columns
            if 'ex_date' not in df_std.columns and 'year' in df_std.columns:
                # If we only have year, we'll need to handle this differently
                logger.warning("Only year information available, will need manual date mapping")
        
        # Parse ex_date if it exists
        if 'ex_date' in df_std.columns:
            df_std['ex_date'] = pd.to_datetime(df_std['ex_date'], errors='coerce')
        
        # Convert dividend to numeric
        if 'dividend' in df_std.columns:
            df_std['dividend'] = pd.to_numeric(df_std['dividend'], errors='coerce')
        
        # Remove rows with missing critical data
        df_std = df_std.dropna(subset=[col for col in required_cols if col in df_std.columns])
        
        return df_std
    
    def calculate_adjustment_factors(
        self,
        price_df: pd.DataFrame,
        dividends_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate cumulative adjustment factors for each stock.
        
        Formula:
            adj_factor[t] = adj_factor[t-1] * (1 - dividend[t] / close[t-1])
            adj_close[t] = close[t] * adj_factor[t]
        
        Args:
            price_df: DataFrame with price data (must have 'date', 'symbol', 'close')
            dividends_df: DataFrame with dividend data
            
        Returns:
            DataFrame with adjustment factors
        """
        logger.info("Calculating dividend adjustment factors...")
        
        # Ensure price_df is sorted
        price_df = price_df.sort_values(['symbol', 'date']).copy()
        
        # Initialize adjustment factor column
        price_df['adj_factor'] = 1.0
        price_df['adj_close'] = price_df['close']
        
        # Standardize dividend data
        div_std = self.standardize_dividend_data(dividends_df)
        
        if 'ex_date' not in div_std.columns:
            logger.warning("No ex_date column in dividend data, skipping adjustment")
            return price_df
        
        # Group by symbol
        for symbol in price_df['symbol'].unique():
            symbol_prices = price_df[price_df['symbol'] == symbol].copy()
            symbol_divs = div_std[div_std['symbol'] == symbol]
            
            if len(symbol_divs) == 0:
                continue
            
            # Sort dividends by ex-date (descending for backward adjustment)
            symbol_divs = symbol_divs.sort_values('ex_date', ascending=False)
            
            # Calculate adjustment factor for each dividend
            adj_factor = 1.0
            
            for _, div_row in symbol_divs.iterrows():
                ex_date = div_row['ex_date']
                dividend = div_row['dividend']
                
                # Find close price on day before ex-date
                prev_date = ex_date - pd.Timedelta(days=1)
                prev_price = symbol_prices[symbol_prices['date'] <= prev_date]['close'].iloc[-1] if len(symbol_prices[symbol_prices['date'] <= prev_date]) > 0 else None
                
                if prev_price is not None and prev_price > 0:
                    # Calculate adjustment multiplier
                    adj_multiplier = 1 - (dividend / prev_price)
                    
                    # Apply to all dates before ex-date
                    mask = (price_df['symbol'] == symbol) & (price_df['date'] < ex_date)
                    price_df.loc[mask, 'adj_factor'] *= adj_multiplier
        
        # Calculate adjusted close
        price_df['adj_close'] = price_df['close'] * price_df['adj_factor']
        
        logger.info("Dividend adjustment complete")
        
        return price_df
    
    def adjust_prices(
        self,
        price_df: pd.DataFrame,
        save_path: Optional[Path] = None
    ) -> pd.DataFrame:
        """
        Main method to adjust prices for dividends.
        
        Args:
            price_df: DataFrame with price data
            save_path: Optional path to save adjusted data
            
        Returns:
            DataFrame with adjusted prices
        """
        # Load dividends if not already loaded
        if self.dividends_df is None:
            self.load_all_dividends()
        
        # Calculate adjustments
        adjusted_df = self.calculate_adjustment_factors(price_df, self.dividends_df)
        
        # Save if path provided
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            if save_path.suffix == '.parquet':
                adjusted_df.to_parquet(save_path, index=False)
            elif save_path.suffix == '.csv':
                adjusted_df.to_csv(save_path, index=False)
            else:
                raise ValueError(f"Unsupported file format: {save_path.suffix}")
            
            logger.info(f"Saved adjusted prices to {save_path}")
        
        return adjusted_df
    
    def get_adjustment_summary(self, adjusted_df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for adjustments.
        
        Args:
            adjusted_df: DataFrame with adjusted prices
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_stocks': adjusted_df['symbol'].nunique(),
            'stocks_with_adjustments': (adjusted_df['adj_factor'] != 1.0).groupby(adjusted_df['symbol']).any().sum(),
            'total_adjustments': (adjusted_df['adj_factor'] != 1.0).sum(),
            'avg_adjustment_factor': adjusted_df[adjusted_df['adj_factor'] != 1.0]['adj_factor'].mean(),
            'min_adjustment_factor': adjusted_df['adj_factor'].min(),
            'max_adjustment_factor': adjusted_df['adj_factor'].max(),
        }
        
        return summary
