"""Price adjustment utilities."""

import pandas as pd
import numpy as np
from typing import Optional

from src.utils import logger


def calculate_log_returns(
    df: pd.DataFrame,
    price_column: str = 'adj_close',
    output_column: str = 'log_return'
) -> pd.DataFrame:
    """
    Calculate log returns for each stock.
    
    Formula: log(price[t] / price[t-1])
    
    Args:
        df: DataFrame with price data
        price_column: Column to use for calculation
        output_column: Name of output column
        
    Returns:
        DataFrame with log returns added
    """
    df = df.copy()
    
    # Sort by symbol and date
    df = df.sort_values(['symbol', 'date'])
    
    # Calculate log returns per symbol
    df[output_column] = df.groupby('symbol')[price_column].transform(
        lambda x: np.log(x / x.shift(1))
    )
    
    # Handle inf and -inf (from zero/negative prices)
    df[output_column] = df[output_column].replace([np.inf, -np.inf], np.nan)
    
    logger.debug(f"Calculated log returns: {df[output_column].notna().sum()} valid values")
    
    return df


def calculate_simple_returns(
    df: pd.DataFrame,
    price_column: str = 'adj_close',
    output_column: str = 'return'
) -> pd.DataFrame:
    """
    Calculate simple returns for each stock.
    
    Formula: (price[t] - price[t-1]) / price[t-1]
    
    Args:
        df: DataFrame with price data
        price_column: Column to use for calculation
        output_column: Name of output column
        
    Returns:
        DataFrame with returns added
    """
    df = df.copy()
    
    # Sort by symbol and date
    df = df.sort_values(['symbol', 'date'])
    
    # Calculate returns per symbol
    df[output_column] = df.groupby('symbol')[price_column].pct_change()
    
    logger.debug(f"Calculated simple returns: {df[output_column].notna().sum()} valid values")
    
    return df


def handle_zero_prices(
    df: pd.DataFrame,
    price_columns: list = ['open', 'high', 'low', 'close', 'adj_close']
) -> pd.DataFrame:
    """
    Handle zero or negative prices by forward-filling or interpolation.
    
    Args:
        df: DataFrame with price data
        price_columns: Columns to check for zero/negative prices
        
    Returns:
        DataFrame with zero prices handled
    """
    df = df.copy()
    
    for col in price_columns:
        if col not in df.columns:
            continue
        
        # Count zero/negative prices
        zero_count = (df[col] <= 0).sum()
        
        if zero_count > 0:
            logger.warning(f"Found {zero_count} zero/negative prices in {col}")
            
            # Replace with NaN
            df.loc[df[col] <= 0, col] = np.nan
            
            # Forward fill within each symbol
            df[col] = df.groupby('symbol')[col].ffill()
            
            # Backward fill if still NaN
            df[col] = df.groupby('symbol')[col].bfill()
    
    return df


def validate_price_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate price data integrity.
    
    Checks:
    - High >= Low
    - High >= Open, Close
    - Low <= Open, Close
    
    Args:
        df: DataFrame with OHLC data
        
    Returns:
        DataFrame with validation flags
    """
    df = df.copy()
    
    # Check high >= low
    invalid_hl = df['high'] < df['low']
    if invalid_hl.any():
        logger.warning(f"Found {invalid_hl.sum()} rows where high < low")
        df.loc[invalid_hl, 'data_quality_flag'] = 'invalid_high_low'
    
    # Check high >= open, close
    invalid_h_open = df['high'] < df['open']
    invalid_h_close = df['high'] < df['close']
    
    if invalid_h_open.any() or invalid_h_close.any():
        total_invalid = (invalid_h_open | invalid_h_close).sum()
        logger.warning(f"Found {total_invalid} rows where high < open/close")
    
    # Check low <= open, close
    invalid_l_open = df['low'] > df['open']
    invalid_l_close = df['low'] > df['close']
    
    if invalid_l_open.any() or invalid_l_close.any():
        total_invalid = (invalid_l_open | invalid_l_close).sum()
        logger.warning(f"Found {total_invalid} rows where low > open/close")
    
    return df
