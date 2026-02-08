"""Data schema definitions for BVMT forecasting system."""

from typing import Dict, Any
import pandas as pd


# French to English column mapping
FRENCH_TO_ENGLISH_MAPPING = {
    # Stock quotation columns
    'SEANCE': 'date',
    'GROUPE': 'group',
    'CODE': 'symbol',
    'VALEUR': 'name',
    'OUVERTURE': 'open',
    'CLOTURE': 'close',
    'PLUS_BAS': 'low',
    'PLUS_HAUT': 'high',
    'QUANTITE_NEGOCIEE': 'volume',
    'NB_TRANSACTION': 'num_trades',
    'CAPITAUX': 'turnover',
    'IND_RES': 'reserved_ind', # Indicator of reservation
    
    # Index columns
    'CODE_INDICE': 'index_code',
    'LIB_INDICE': 'index_name',
    'INDICE_JOUR': 'value',
    'INDICE_VEILLE': 'prev_value',
    'VARIATION_VEILLE': 'change_pct',
    'INDICE_PLUS_HAUT': 'high',
    'INDICE_PLUS_BAS': 'low',
    'INDICE_OUV': 'open'
}


# Standard schema for stock quotation data
STOCK_SCHEMA = {
    'date': 'datetime64[ns]',
    'symbol': 'str',
    'name': 'str',
    'group': 'int',
    'open': 'float64',
    'high': 'float64',
    'low': 'float64',
    'close': 'float64',
    'volume': 'int64',
    'num_trades': 'int64',
    'turnover': 'float64'
}


# Standard schema for index data
INDEX_SCHEMA = {
    'date': 'datetime64[ns]',
    'index_code': 'str',
    'index_name': 'str',
    'value': 'float64',
    'prev_value': 'float64',
    'change_pct': 'float64',
    'high': 'float64',
    'low': 'float64'
}


def standardize_columns(df: pd.DataFrame, mapping: Dict[str, str] = None) -> pd.DataFrame:
    """
    Standardize column names from French to English.
    
    Args:
        df: DataFrame with French column names
        mapping: Custom column mapping (default: FRENCH_TO_ENGLISH_MAPPING)
        
    Returns:
        DataFrame with standardized English column names
    """
    if mapping is None:
        mapping = FRENCH_TO_ENGLISH_MAPPING
    
    # Create valid mapping (handling potential case/whitespace differences)
    # The keys in mapping are uppercase
    
    rename_dict = {}
    for col in df.columns:
        clean_col = str(col).strip().upper()
        if clean_col in mapping:
            rename_dict[col] = mapping[clean_col]
        elif col in mapping: # fallback to exact match just in case
            rename_dict[col] = mapping[col]
            
    df = df.rename(columns=rename_dict)
    
    return df


def parse_french_date(date_str: str) -> pd.Timestamp:
    """
    Parse French date format (DD/MM/YYYY or DD/MM/YY).
    
    Args:
        date_str: Date string in French format
        
    Returns:
        Pandas Timestamp
    """
    if pd.isna(date_str):
        return pd.NaT
        
    date_str = str(date_str).strip()
    
    # Try different formats
    for fmt in ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            continue
            
    # Fallback to general parser
    return pd.to_datetime(date_str, errors='coerce')


def apply_schema(df: pd.DataFrame, schema: Dict[str, str], drop_extra: bool = True) -> pd.DataFrame:
    """
    Apply data types according to schema and handle extra columns.
    
    Args:
        df: DataFrame to apply schema to
        schema: Dictionary mapping column names to data types
        drop_extra: Whether to drop columns not in schema (default: True)
        
    Returns:
        DataFrame with correct data types and columns
    """
    # Create copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Drop extra columns if requested
    if drop_extra:
        extra_cols = [c for c in df.columns if c not in schema]
        if extra_cols:
            df = df.drop(columns=extra_cols)
    
    for col, dtype in schema.items():
        if col in df.columns:
            if dtype == 'datetime64[ns]':
                if df[col].dtype != 'datetime64[ns]':
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            elif dtype == 'str':
                df[col] = df[col].astype(str)
            elif dtype == 'int64':
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')
            elif dtype == 'float64':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            # Add missing columns with default values if strictly adhering to schema?
            # For now, we just skip, but strictly we might want them present
            pass
    
    return df
