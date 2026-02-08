"""Calendar and seasonal features for BVMT forecasting system."""

import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime

from src.utils import logger


def add_day_of_week(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Add day of week feature (0=Monday, 4=Friday).
    
    Args:
        df: DataFrame with date column
        date_column: Date column name
        
    Returns:
        DataFrame with day of week columns added
    """
    df = df.copy()
    
    df['day_of_week'] = pd.to_datetime(df[date_column]).dt.dayofweek
    
    # One-hot encode
    for i in range(5):  # Monday to Friday
        df[f'is_day_{i}'] = (df['day_of_week'] == i).astype(int)
    
    logger.debug(f"Added day of week features")
    
    return df


def add_month(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Add month feature (1-12).
    
    Args:
        df: DataFrame with date column
        date_column: Date column name
        
    Returns:
        DataFrame with month columns added
    """
    df = df.copy()
    
    df['month'] = pd.to_datetime(df[date_column]).dt.month
    
    # One-hot encode
    for i in range(1, 13):
        df[f'is_month_{i}'] = (df['month'] == i).astype(int)
    
    logger.debug(f"Added month features")
    
    return df


def add_quarter(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Add quarter feature (1-4).
    
    Args:
        df: DataFrame with date column
        date_column: Date column name
        
    Returns:
        DataFrame with quarter columns added
    """
    df = df.copy()
    
    df['quarter'] = pd.to_datetime(df[date_column]).dt.quarter
    
    # One-hot encode
    for i in range(1, 5):
        df[f'is_q{i}'] = (df['quarter'] == i).astype(int)
    
    logger.debug(f"Added quarter features")
    
    return df


def add_month_end(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Add month-end indicator (last trading day of month).
    
    Args:
        df: DataFrame with date column
        date_column: Date column name
        
    Returns:
        DataFrame with month-end indicator added
    """
    df = df.copy()
    
    df['is_month_end'] = pd.to_datetime(df[date_column]).dt.is_month_end.astype(int)
    
    logger.debug(f"Added month-end indicator")
    
    return df


def add_ramadan_indicator(
    df: pd.DataFrame,
    date_column: str = 'date'
) -> pd.DataFrame:
    """
    Add Ramadan indicator using hijri-converter.
    
    Args:
        df: DataFrame with date column
        date_column: Date column name
        
    Returns:
        DataFrame with Ramadan indicator added
    """
    df = df.copy()
    
    try:
        from hijri_converter import Hijri, Gregorian
        
        def is_ramadan(date):
            """Check if date falls in Ramadan."""
            try:
                # Convert to Hijri calendar
                hijri_date = Gregorian(date.year, date.month, date.day).to_hijri()
                
                # Ramadan is the 9th month in Hijri calendar
                return 1 if hijri_date.month == 9 else 0
            except:
                return 0
        
        df['is_ramadan'] = pd.to_datetime(df[date_column]).apply(is_ramadan)
        
        ramadan_count = df['is_ramadan'].sum()
        logger.debug(f"Added Ramadan indicator ({ramadan_count} Ramadan trading days)")
        
    except ImportError:
        logger.warning("hijri-converter not installed, skipping Ramadan indicator")
        df['is_ramadan'] = 0
    
    return df


def calculate_volatility_regime(
    df: pd.DataFrame,
    window: int = 20,
    return_column: str = 'log_return',
    threshold_low: float = 0.33,
    threshold_high: float = 0.67
) -> pd.DataFrame:
    """
    Classify volatility regime based on rolling standard deviation.
    
    Regimes:
    - Low: volatility < 33rd percentile
    - Normal: 33rd <= volatility <= 67th percentile
    - High: volatility > 67th percentile
    
    Args:
        df: DataFrame with returns
        window: Rolling window for volatility calculation
        return_column: Return column name
        threshold_low: Lower percentile threshold
        threshold_high: Upper percentile threshold
        
    Returns:
        DataFrame with volatility regime columns added
    """
    df = df.copy()
    
    def classify_vol_regime(group):
        if len(group) == 0:
            return pd.DataFrame({
                'volatility': [0.0] * len(group),
                'volatility_regime': ['Normal'] * len(group)
            }, index=group.index)
            
        # Calculate rolling volatility
        rolling_vol = group[return_column].rolling(window=window, min_periods=min(5, window)).std()
        
        # Fill NaNs with 0 to allow quantile calculation if needed, or handle explicitly
        rolling_vol = rolling_vol.fillna(0)
        
        # Calculate percentiles for this symbol
        # Handle case where volatility is all 0/NaN
        if rolling_vol.max() == 0:
            p33 = 0
            p67 = 0
        else:
            p33 = rolling_vol.quantile(threshold_low)
            p67 = rolling_vol.quantile(threshold_high)
        
        # Classify regime
        regime = pd.Series('Normal', index=group.index)
        if p33 < p67: # Standard case
            regime[rolling_vol < p33] = 'Low'
            regime[rolling_vol > p67] = 'High'
        
        return pd.DataFrame({
            'volatility': rolling_vol,
            'volatility_regime': regime
        }, index=group.index)
    
    vol_df = df.groupby('symbol').apply(classify_vol_regime).reset_index(level=0, drop=True)
    df = pd.concat([df, vol_df], axis=1)
    
    # One-hot encode regime
    df['vol_low'] = (df['volatility_regime'] == 'Low').astype(int)
    df['vol_normal'] = (df['volatility_regime'] == 'Normal').astype(int)
    df['vol_high'] = (df['volatility_regime'] == 'High').astype(int)
    
    logger.debug(f"Calculated volatility regimes")
    
    return df


def add_year(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
    """
    Add year feature.
    
    Args:
        df: DataFrame with date column
        date_column: Date column name
        
    Returns:
        DataFrame with year column added
    """
    df = df.copy()
    
    df['year'] = pd.to_datetime(df[date_column]).dt.year
    
    logger.debug(f"Added year feature")
    
    return df


def add_summer_indicator(
    df: pd.DataFrame,
    date_column: str = 'date',
    summer_months: List[int] = [7, 8]
) -> pd.DataFrame:
    """
    Add summer indicator (typically low trading activity).
    
    Args:
        df: DataFrame with date column
        date_column: Date column name
        summer_months: Months considered as summer (default: July, August)
        
    Returns:
        DataFrame with summer indicator added
    """
    df = df.copy()
    
    month = pd.to_datetime(df[date_column]).dt.month
    df['is_summer'] = month.isin(summer_months).astype(int)
    
    logger.debug(f"Added summer indicator (months: {summer_months})")
    
    return df


def calculate_all_calendar_features(
    df: pd.DataFrame,
    config: dict = None
) -> pd.DataFrame:
    """
    Calculate all calendar and seasonal features.
    
    Args:
        df: DataFrame with date column
        config: Configuration dictionary with feature parameters
        
    Returns:
        DataFrame with all calendar features added
    """
    logger.info("Calculating calendar and seasonal features...")
    
    if config is None:
        config = {}
    
    # Day of week
    df = add_day_of_week(df)
    
    # Month
    df = add_month(df)
    
    # Quarter
    df = add_quarter(df)
    
    # Month-end
    df = add_month_end(df)
    
    # Year
    df = add_year(df)
    
    # Ramadan
    if config.get('ramadan_impact', True):
        df = add_ramadan_indicator(df)
    
    # Summer
    df = add_summer_indicator(df)
    
    # Volatility regime
    df = calculate_volatility_regime(df, window=20)
    
    logger.info(f"✓ Calendar features complete")
    
    return df
