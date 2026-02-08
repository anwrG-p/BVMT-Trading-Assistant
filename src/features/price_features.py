"""Price-based features for BVMT forecasting system."""

import pandas as pd
import numpy as np
from typing import List

from src.utils import logger


def calculate_sma(
    df: pd.DataFrame,
    periods: List[int] = [5, 10, 20, 50],
    price_column: str = 'adj_close'
) -> pd.DataFrame:
    """
    Calculate Simple Moving Averages.
    
    Args:
        df: DataFrame with price data
        periods: List of SMA periods
        price_column: Column to use for calculation
        
    Returns:
        DataFrame with SMA columns added
    """
    df = df.copy()
    
    for period in periods:
        col_name = f'sma_{period}'
        df[col_name] = df.groupby('symbol')[price_column].transform(
            lambda x: x.rolling(window=period, min_periods=period).mean()
        )
    
    logger.debug(f"Calculated SMA for periods: {periods}")
    
    return df


def calculate_ema(
    df: pd.DataFrame,
    periods: List[int] = [12, 26],
    price_column: str = 'adj_close'
) -> pd.DataFrame:
    """
    Calculate Exponential Moving Averages.
    
    Args:
        df: DataFrame with price data
        periods: List of EMA periods
        price_column: Column to use for calculation
        
    Returns:
        DataFrame with EMA columns added
    """
    df = df.copy()
    
    for period in periods:
        col_name = f'ema_{period}'
        df[col_name] = df.groupby('symbol')[price_column].transform(
            lambda x: x.ewm(span=period, adjust=False).mean()
        )
    
    logger.debug(f"Calculated EMA for periods: {periods}")
    
    return df


def calculate_rsi(
    df: pd.DataFrame,
    period: int = 14,
    price_column: str = 'adj_close'
) -> pd.DataFrame:
    """
    Calculate Relative Strength Index (RSI).
    
    Formula:
        RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss
    
    Args:
        df: DataFrame with price data
        period: RSI period (default: 14)
        price_column: Column to use for calculation
        
    Returns:
        DataFrame with RSI column added
    """
    df = df.copy()
    
    def compute_rsi(prices):
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period, min_periods=period).mean()
        avg_losses = losses.rolling(window=period, min_periods=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    df['rsi'] = df.groupby('symbol')[price_column].transform(compute_rsi)
    
    logger.debug(f"Calculated RSI with period {period}")
    
    return df


def calculate_macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    price_column: str = 'adj_close'
) -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        df: DataFrame with price data
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line period
        price_column: Column to use for calculation
        
    Returns:
        DataFrame with MACD columns added
    """
    df = df.copy()
    
    def compute_macd(prices):
        # Calculate EMAs
        ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
        ema_slow = prices.ewm(span=slow_period, adjust=False).mean()
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # MACD histogram
        macd_hist = macd_line - signal_line
        
        return pd.DataFrame({
            'macd': macd_line,
            'macd_signal': signal_line,
            'macd_hist': macd_hist
        })
    
    macd_df = df.groupby('symbol')[price_column].apply(compute_macd).reset_index(level=0, drop=True)
    df = pd.concat([df, macd_df], axis=1)
    
    logger.debug(f"Calculated MACD ({fast_period}, {slow_period}, {signal_period})")
    
    return df


def calculate_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    num_std: float = 2.0,
    price_column: str = 'adj_close'
) -> pd.DataFrame:
    """
    Calculate Bollinger Bands.
    
    Args:
        df: DataFrame with price data
        period: Moving average period
        num_std: Number of standard deviations
        price_column: Column to use for calculation
        
    Returns:
        DataFrame with Bollinger Bands columns added
    """
    df = df.copy()
    
    def compute_bollinger(prices):
        # Middle band (SMA)
        middle = prices.rolling(window=period, min_periods=period).mean()
        
        # Standard deviation
        std = prices.rolling(window=period, min_periods=period).std()
        
        # Upper and lower bands
        upper = middle + (num_std * std)
        lower = middle - (num_std * std)
        
        # Bollinger Band Width
        bb_width = (upper - lower) / middle
        
        # %B (position within bands)
        percent_b = (prices - lower) / (upper - lower)
        
        return pd.DataFrame({
            'bb_middle': middle,
            'bb_upper': upper,
            'bb_lower': lower,
            'bb_width': bb_width,
            'bb_percent': percent_b
        })
    
    bb_df = df.groupby('symbol')[price_column].apply(compute_bollinger).reset_index(level=0, drop=True)
    df = pd.concat([df, bb_df], axis=1)
    
    logger.debug(f"Calculated Bollinger Bands (period={period}, std={num_std})")
    
    return df


def calculate_momentum(
    df: pd.DataFrame,
    periods: List[int] = [1, 5, 10, 20],
    price_column: str = 'adj_close'
) -> pd.DataFrame:
    """
    Calculate price momentum (percentage change over N periods).
    
    Args:
        df: DataFrame with price data
        periods: List of momentum periods
        price_column: Column to use for calculation
        
    Returns:
        DataFrame with momentum columns added
    """
    df = df.copy()
    
    for period in periods:
        col_name = f'momentum_{period}'
        df[col_name] = df.groupby('symbol')[price_column].transform(
            lambda x: x.pct_change(periods=period)
        )
    
    logger.debug(f"Calculated momentum for periods: {periods}")
    
    return df


def calculate_price_zscores(
    df: pd.DataFrame,
    window: int = 20,
    price_column: str = 'adj_close'
) -> pd.DataFrame:
    """
    Calculate rolling z-scores for prices.
    
    Formula: z = (price - rolling_mean) / rolling_std
    
    Args:
        df: DataFrame with price data
        window: Rolling window size
        price_column: Column to use for calculation
        
    Returns:
        DataFrame with z-score column added
    """
    df = df.copy()
    
    def compute_zscore(prices):
        rolling_mean = prices.rolling(window=window, min_periods=window).mean()
        rolling_std = prices.rolling(window=window, min_periods=window).std()
        
        zscore = (prices - rolling_mean) / rolling_std
        
        return zscore
    
    df['price_zscore'] = df.groupby('symbol')[price_column].transform(compute_zscore)
    
    logger.debug(f"Calculated price z-scores with window {window}")
    
    return df


def calculate_price_lags(
    df: pd.DataFrame,
    lags: List[int] = [1, 5, 10, 20],
    price_column: str = 'adj_close'
) -> pd.DataFrame:
    """
    Calculate lagged price values.
    
    Args:
        df: DataFrame with price data
        lags: List of lag periods
        price_column: Column to use for calculation
        
    Returns:
        DataFrame with lagged price columns added
    """
    df = df.copy()
    
    for lag in lags:
        col_name = f'{price_column}_lag_{lag}'
        df[col_name] = df.groupby('symbol')[price_column].shift(lag)
    
    logger.debug(f"Calculated price lags: {lags}")
    
    return df


def calculate_returns(
    df: pd.DataFrame,
    price_column: str = 'adj_close'
) -> pd.DataFrame:
    """
    Calculate simple and log returns.
    
    Args:
        df: DataFrame with price data
        price_column: Column to use for calculation
        
    Returns:
        DataFrame with return columns added
    """
    df = df.copy()
    
    # Calculate simple return
    df['simple_return'] = df.groupby('symbol')[price_column].pct_change()
    
    # Calculate log return
    df['log_return'] = df.groupby('symbol')[price_column].apply(
        lambda x: np.log(x / x.shift(1))
    ).reset_index(level=0, drop=True)
    
    # Fill NA with 0 for the first period
    df['simple_return'] = df['simple_return'].fillna(0)
    df['log_return'] = df['log_return'].fillna(0)
    
    logger.debug(f"Calculated returns (simple and log)")
    
    return df


def calculate_all_price_features(
    df: pd.DataFrame,
    config: dict = None
) -> pd.DataFrame:
    """
    Calculate all price-based features.
    
    Args:
        df: DataFrame with price data
        config: Configuration dictionary with feature parameters
        
    Returns:
        DataFrame with all price features added
    """
    logger.info("Calculating price-based features...")
    
    if config is None:
        config = {}
    
    # SMA
    sma_periods = config.get('sma_periods', [5, 10, 20, 50])
    df = calculate_sma(df, periods=sma_periods)
    
    # EMA
    ema_periods = config.get('ema_periods', [12, 26])
    df = calculate_ema(df, periods=ema_periods)
    
    # RSI
    rsi_period = config.get('rsi_period', 14)
    df = calculate_rsi(df, period=rsi_period)
    
    # MACD
    df = calculate_macd(
        df,
        fast_period=config.get('macd_fast', 12),
        slow_period=config.get('macd_slow', 26),
        signal_period=config.get('macd_signal', 9)
    )
    
    # Bollinger Bands
    df = calculate_bollinger_bands(
        df,
        period=config.get('bollinger_period', 20),
        num_std=config.get('bollinger_std', 2.0)
    )
    
    # Momentum
    momentum_periods = config.get('price_lags', [1, 5, 10, 20])
    df = calculate_momentum(df, periods=momentum_periods)
    
    # Returns (Log and Simple)
    df = calculate_returns(df)
    
    # Z-scores
    df = calculate_price_zscores(df, window=20)
    
    # Price lags
    df = calculate_price_lags(df, lags=momentum_periods)
    
    logger.info(f"✓ Price features complete: {len([c for c in df.columns if c not in ['date', 'symbol', 'name']])} total features")
    
    return df
