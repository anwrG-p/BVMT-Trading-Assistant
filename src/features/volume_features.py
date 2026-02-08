"""Volume and liquidity features for BVMT forecasting system."""

import pandas as pd
import numpy as np
from typing import List, Tuple

from src.utils import logger


def calculate_volume_ma(
    df: pd.DataFrame,
    period: int = 20,
    volume_column: str = 'volume'
) -> pd.DataFrame:
    """
    Calculate volume moving average.
    
    Args:
        df: DataFrame with volume data
        period: Moving average period
        volume_column: Column to use for calculation
        
    Returns:
        DataFrame with volume MA column added
    """
    df = df.copy()
    
    df['volume_ma'] = df.groupby('symbol')[volume_column].transform(
        lambda x: x.rolling(window=period, min_periods=period).mean()
    )
    
    logger.debug(f"Calculated volume MA with period {period}")
    
    return df


def calculate_volume_ratio(
    df: pd.DataFrame,
    period: int = 20,
    volume_column: str = 'volume'
) -> pd.DataFrame:
    """
    Calculate volume ratio (current volume / average volume).
    
    Args:
        df: DataFrame with volume data
        period: Period for average calculation
        volume_column: Column to use for calculation
        
    Returns:
        DataFrame with volume ratio column added
    """
    df = df.copy()
    
    # Calculate volume MA first if not exists
    if 'volume_ma' not in df.columns:
        df = calculate_volume_ma(df, period=period, volume_column=volume_column)
    
    # Calculate ratio
    df['volume_ratio'] = df[volume_column] / df['volume_ma']
    
    # Handle division by zero
    df['volume_ratio'] = df['volume_ratio'].replace([np.inf, -np.inf], np.nan)
    
    logger.debug(f"Calculated volume ratio")
    
    return df


def calculate_liquidity_regime(
    df: pd.DataFrame,
    q_low: float = 0.20,
    q_high: float = 0.80,
    volume_column: str = 'volume'
) -> pd.DataFrame:
    """
    Classify liquidity regime using volume quantiles.
    
    Regimes:
    - Low: volume < Q20
    - Normal: Q20 <= volume <= Q80
    - High: volume > Q80
    
    Args:
        df: DataFrame with volume data
        q_low: Lower quantile threshold (default: 0.20)
        q_high: Upper quantile threshold (default: 0.80)
        volume_column: Column to use for calculation
        
    Returns:
        DataFrame with liquidity regime columns added
    """
    df = df.copy()
    
    def classify_regime(group):
        # Calculate quantiles for this symbol
        q20 = group[volume_column].quantile(q_low)
        q80 = group[volume_column].quantile(q_high)
        
        # Classify regime
        regime = pd.Series('Normal', index=group.index)
        regime[group[volume_column] < q20] = 'Low'
        regime[group[volume_column] > q80] = 'High'
        
        # Add quantile values
        return pd.DataFrame({
            'liquidity_regime': regime,
            'volume_q20': q20,
            'volume_q80': q80
        }, index=group.index)
    
    regime_df = df.groupby('symbol').apply(classify_regime).reset_index(level=0, drop=True)
    df = pd.concat([df, regime_df], axis=1)
    
    # One-hot encode regime
    df['liquidity_low'] = (df['liquidity_regime'] == 'Low').astype(int)
    df['liquidity_normal'] = (df['liquidity_regime'] == 'Normal').astype(int)
    df['liquidity_high'] = (df['liquidity_regime'] == 'High').astype(int)
    
    logger.debug(f"Calculated liquidity regimes (Q{int(q_low*100)}/Q{int(q_high*100)})")
    
    return df


def calculate_avg_trade_size(
    df: pd.DataFrame,
    volume_column: str = 'volume',
    num_trades_column: str = 'num_trades'
) -> pd.DataFrame:
    """
    Calculate average trade size.
    
    Args:
        df: DataFrame with volume and trade count data
        volume_column: Volume column name
        num_trades_column: Number of trades column name
        
    Returns:
        DataFrame with average trade size column added
    """
    df = df.copy()
    
    # Calculate average trade size
    df['avg_trade_size'] = df[volume_column] / df[num_trades_column]
    
    # Handle division by zero
    df['avg_trade_size'] = df['avg_trade_size'].replace([np.inf, -np.inf], np.nan)
    
    logger.debug(f"Calculated average trade size")
    
    return df


def calculate_turnover_ratio(
    df: pd.DataFrame,
    window: int = 20,
    turnover_column: str = 'turnover'
) -> pd.DataFrame:
    """
    Calculate turnover ratio (current / rolling average).
    
    Args:
        df: DataFrame with turnover data
        window: Rolling window size
        turnover_column: Turnover column name
        
    Returns:
        DataFrame with turnover ratio column added
    """
    df = df.copy()
    
    # Calculate rolling average turnover
    df['turnover_ma'] = df.groupby('symbol')[turnover_column].transform(
        lambda x: x.rolling(window=window, min_periods=window).mean()
    )
    
    # Calculate ratio
    df['turnover_ratio'] = df[turnover_column] / df['turnover_ma']
    
    # Handle division by zero
    df['turnover_ratio'] = df['turnover_ratio'].replace([np.inf, -np.inf], np.nan)
    
    logger.debug(f"Calculated turnover ratio")
    
    return df


def calculate_volume_momentum(
    df: pd.DataFrame,
    periods: List[int] = [1, 5, 10],
    volume_column: str = 'volume'
) -> pd.DataFrame:
    """
    Calculate volume momentum (percentage change).
    
    Args:
        df: DataFrame with volume data
        periods: List of momentum periods
        volume_column: Volume column name
        
    Returns:
        DataFrame with volume momentum columns added
    """
    df = df.copy()
    
    for period in periods:
        col_name = f'volume_momentum_{period}'
        df[col_name] = df.groupby('symbol')[volume_column].transform(
            lambda x: x.pct_change(periods=period)
        )
    
    logger.debug(f"Calculated volume momentum for periods: {periods}")
    
    return df


def calculate_bid_ask_spread_proxy(
    df: pd.DataFrame,
    high_column: str = 'high',
    low_column: str = 'low',
    close_column: str = 'close'
) -> pd.DataFrame:
    """
    Calculate bid-ask spread proxy using (high - low) / close.
    
    Args:
        df: DataFrame with OHLC data
        high_column: High price column
        low_column: Low price column
        close_column: Close price column
        
    Returns:
        DataFrame with spread proxy column added
    """
    df = df.copy()
    
    # Calculate spread proxy
    df['spread_proxy'] = (df[high_column] - df[low_column]) / df[close_column]
    
    # Handle division by zero
    df['spread_proxy'] = df['spread_proxy'].replace([np.inf, -np.inf], np.nan)
    
    logger.debug(f"Calculated bid-ask spread proxy")
    
    return df


def calculate_volume_price_trend(
    df: pd.DataFrame,
    period: int = 20,
    volume_column: str = 'volume',
    close_column: str = 'close'
) -> pd.DataFrame:
    """
    Calculate Volume Price Trend (VPT) indicator.
    
    VPT = VPT_prev + volume * (close - close_prev) / close_prev
    
    Args:
        df: DataFrame with volume and price data
        period: Period for calculation
        volume_column: Volume column name
        close_column: Close price column name
        
    Returns:
        DataFrame with VPT column added
    """
    df = df.copy()
    
    # Calculate price change percentage per symbol
    price_change_pct = df.groupby('symbol')[close_column].pct_change().fillna(0)
    
    # Calculate VPT increment
    vpt_inc = df[volume_column] * price_change_pct
    
    # Calculate Cumulative VPT
    df['vpt'] = vpt_inc.groupby(df['symbol']).cumsum()
    
    logger.debug(f"Calculated Volume Price Trend")
    
    return df


def calculate_all_volume_features(
    df: pd.DataFrame,
    config: dict = None
) -> pd.DataFrame:
    """
    Calculate all volume and liquidity features.
    
    Args:
        df: DataFrame with volume data
        config: Configuration dictionary with feature parameters
        
    Returns:
        DataFrame with all volume features added
    """
    logger.info("Calculating volume and liquidity features...")
    
    if config is None:
        config = {}
    
    # Volume MA and ratio
    volume_ma_period = config.get('volume_ma_period', 20)
    df = calculate_volume_ma(df, period=volume_ma_period)
    df = calculate_volume_ratio(df, period=volume_ma_period)
    
    # Liquidity regime
    df = calculate_liquidity_regime(
        df,
        q_low=config.get('liquidity_q_low', 0.20),
        q_high=config.get('liquidity_q_high', 0.80)
    )
    
    # Average trade size
    if 'num_trades' in df.columns:
        df = calculate_avg_trade_size(df)
    
    # Turnover ratio
    if 'turnover' in df.columns:
        df = calculate_turnover_ratio(df)
    
    # Volume momentum
    volume_lags = config.get('volume_lags', [1, 5, 10])
    df = calculate_volume_momentum(df, periods=volume_lags)
    
    # Bid-ask spread proxy
    df = calculate_bid_ask_spread_proxy(df)
    
    # Volume Price Trend
    df = calculate_volume_price_trend(df)
    
    logger.info(f"✓ Volume features complete")
    
    return df
