"""Market context features for BVMT forecasting system."""

import pandas as pd
import numpy as np
from typing import Optional

from src.utils import logger


def merge_market_index(
    stock_df: pd.DataFrame,
    index_df: pd.DataFrame,
    index_column: str = 'value'
) -> pd.DataFrame:
    """
    Merge market index data with stock data.
    
    Args:
        stock_df: Stock DataFrame
        index_df: Index DataFrame (TUNINDEX)
        index_column: Index value column name
        
    Returns:
        DataFrame with index data merged
    """
    # Ensure both have date column
    if 'date' not in stock_df.columns or 'date' not in index_df.columns:
        raise ValueError("Both DataFrames must have 'date' column")
    
    # Select relevant index columns
    index_cols = ['date', index_column]
    if 'change_pct' in index_df.columns:
        index_cols.append('change_pct')
    
    index_subset = index_df[index_cols].copy()
    index_subset = index_subset.rename(columns={
        index_column: 'market_index',
        'change_pct': 'market_return'
    })
    
    # Merge on date
    merged_df = stock_df.merge(index_subset, on='date', how='left')
    
    logger.debug(f"Merged market index data")
    
    return merged_df


def calculate_market_return(
    df: pd.DataFrame,
    index_column: str = 'market_index'
) -> pd.DataFrame:
    """
    Calculate market returns if not already present.
    
    Args:
        df: DataFrame with market index
        index_column: Index value column name
        
    Returns:
        DataFrame with market return column added
    """
    df = df.copy()
    
    if 'market_return' not in df.columns:
        # Ensure index is numeric
        market_idx = pd.to_numeric(df[index_column], errors='coerce')
        df['market_return'] = market_idx.pct_change()
    
    return df


def calculate_relative_strength(
    df: pd.DataFrame,
    stock_return_column: str = 'log_return',
    market_return_column: str = 'market_return'
) -> pd.DataFrame:
    """
    Calculate relative strength (stock return - market return).
    
    Args:
        df: DataFrame with stock and market returns
        stock_return_column: Stock return column name
        market_return_column: Market return column name
        
    Returns:
        DataFrame with relative strength column added
    """
    df = df.copy()
    
    # Ensure returns are numeric
    stock_ret = pd.to_numeric(df[stock_return_column], errors='coerce')
    market_ret = pd.to_numeric(df[market_return_column], errors='coerce')
    
    df['relative_strength'] = stock_ret - market_ret
    
    logger.debug(f"Calculated relative strength")
    
    return df


def calculate_market_correlation(
    df: pd.DataFrame,
    window: int = 60,
    stock_return_column: str = 'log_return',
    market_return_column: str = 'market_return'
) -> pd.DataFrame:
    """
    Calculate rolling correlation with market index.
    
    Args:
        df: DataFrame with stock and market returns
        window: Rolling window size
        stock_return_column: Stock return column name
        market_return_column: Market return column name
        
    Returns:
        DataFrame with market correlation column added
    """
    df = df.copy()
    
    def compute_correlation(group):
        # Calculate rolling correlation
        corr = group[stock_return_column].rolling(window=window, min_periods=window).corr(
            group[market_return_column]
        )
        return corr
    
    df['market_correlation'] = df.groupby('symbol').apply(compute_correlation).reset_index(level=0, drop=True)
    
    logger.debug(f"Calculated market correlation with window {window}")
    
    return df


def calculate_beta(
    df: pd.DataFrame,
    window: int = 60,
    stock_return_column: str = 'log_return',
    market_return_column: str = 'market_return'
) -> pd.DataFrame:
    """
    Calculate rolling beta (stock volatility relative to market).
    
    Beta = Cov(stock_return, market_return) / Var(market_return)
    
    Args:
        df: DataFrame with stock and market returns
        window: Rolling window size
        stock_return_column: Stock return column name
        market_return_column: Market return column name
        
    Returns:
        DataFrame with beta column added
    """
    df = df.copy()
    
    def compute_beta(group):
        # Calculate rolling covariance and variance
        stock_returns = group[stock_return_column]
        market_returns = group[market_return_column]
        
        # Rolling covariance
        cov = stock_returns.rolling(window=window, min_periods=window).cov(market_returns)
        
        # Rolling variance of market
        market_var = market_returns.rolling(window=window, min_periods=window).var()
        
        # Beta
        beta = cov / market_var
        
        return beta
    
    df['beta'] = df.groupby('symbol').apply(compute_beta).reset_index(level=0, drop=True)
    
    # Handle division by zero
    df['beta'] = df['beta'].replace([np.inf, -np.inf], np.nan)
    
    logger.debug(f"Calculated beta with window {window}")
    
    return df


def calculate_market_cap_proxy(
    df: pd.DataFrame,
    price_column: str = 'close',
    volume_column: str = 'volume'
) -> pd.DataFrame:
    """
    Calculate market cap proxy (price * volume as a relative measure).
    
    Args:
        df: DataFrame with price and volume data
        price_column: Price column name
        volume_column: Volume column name
        
    Returns:
        DataFrame with market cap proxy column added
    """
    df = df.copy()
    
    df['market_cap_proxy'] = df[price_column] * df[volume_column]
    
    logger.debug(f"Calculated market cap proxy")
    
    return df


def calculate_all_market_features(
    stock_df: pd.DataFrame,
    index_df: Optional[pd.DataFrame] = None,
    config: dict = None
) -> pd.DataFrame:
    """
    Calculate all market context features.
    
    Args:
        stock_df: Stock DataFrame
        index_df: Index DataFrame (TUNINDEX)
        config: Configuration dictionary with feature parameters
        
    Returns:
        DataFrame with all market features added
    """
    logger.info("Calculating market context features...")
    
    if config is None:
        config = {}
    
    # Merge index data if provided
    if index_df is not None:
        stock_df = merge_market_index(stock_df, index_df)
        
        # Enforce numeric types for market index and returns
        if 'market_index' in stock_df.columns:
            stock_df['market_index'] = pd.to_numeric(stock_df['market_index'], errors='coerce')
            
        stock_df = calculate_market_return(stock_df)
        
        # Enforce numeric types for returns
        if 'market_return' in stock_df.columns:
            stock_df['market_return'] = pd.to_numeric(stock_df['market_return'], errors='coerce')
            
        if 'log_return' in stock_df.columns:
            stock_df['log_return'] = pd.to_numeric(stock_df['log_return'], errors='coerce')
        
        # Relative strength
        stock_df = calculate_relative_strength(stock_df)
        
        # Market correlation
        corr_window = config.get('market_corr_window', 60)
        stock_df = calculate_market_correlation(stock_df, window=corr_window)
        
        # Beta
        stock_df = calculate_beta(stock_df, window=corr_window)
    else:
        logger.warning("No index data provided, skipping market features")
    
    # Market cap proxy
    # Ensure inputs are numeric
    if 'close' in stock_df.columns:
        stock_df['close'] = pd.to_numeric(stock_df['close'], errors='coerce')
    if 'volume' in stock_df.columns:
        stock_df['volume'] = pd.to_numeric(stock_df['volume'], errors='coerce')
        
    stock_df = calculate_market_cap_proxy(stock_df)
    
    logger.info(f"✓ Market features complete")
    
    return stock_df
