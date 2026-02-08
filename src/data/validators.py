"""Data quality validation for BVMT forecasting system."""

from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from pathlib import Path
import json

from src.utils import logger, ValidationError


class DataQualityValidator:
    """Validator for data quality checks."""
    
    def __init__(self, df: pd.DataFrame, name: str = "dataset"):
        """
        Initialize validator.
        
        Args:
            df: DataFrame to validate
            name: Name of dataset for reporting
        """
        self.df = df
        self.name = name
        self.issues: List[Dict] = []
    
    def check_duplicates(self) -> Tuple[bool, int]:
        """
        Check for duplicate (date, symbol) pairs.
        
        Returns:
            (has_duplicates, num_duplicates)
        """
        if 'date' in self.df.columns and 'symbol' in self.df.columns:
            duplicates = self.df.duplicated(subset=['date', 'symbol'], keep=False)
            num_duplicates = duplicates.sum()
            
            if num_duplicates > 0:
                self.issues.append({
                    'type': 'duplicates',
                    'severity': 'high',
                    'count': int(num_duplicates),
                    'message': f"Found {num_duplicates} duplicate (date, symbol) pairs"
                })
                logger.warning(f"{self.name}: Found {num_duplicates} duplicates")
                return True, num_duplicates
        
        return False, 0
    
    def check_outliers(self, column: str = 'close', threshold: float = 10.0) -> Tuple[bool, int]:
        """
        Check for price outliers using day-over-day changes.
        
        Args:
            column: Column to check for outliers
            threshold: Multiplier threshold (e.g., 10.0 = 10x jump)
            
        Returns:
            (has_outliers, num_outliers)
        """
        if column not in self.df.columns:
            return False, 0
        
        # Calculate day-over-day ratio per symbol
        df_sorted = self.df.sort_values(['symbol', 'date'])
        df_sorted['price_ratio'] = df_sorted.groupby('symbol')[column].pct_change().abs() + 1
        
        # Flag outliers
        outliers = df_sorted['price_ratio'] > threshold
        num_outliers = outliers.sum()
        
        if num_outliers > 0:
            self.issues.append({
                'type': 'outliers',
                'severity': 'medium',
                'count': int(num_outliers),
                'column': column,
                'threshold': threshold,
                'message': f"Found {num_outliers} price jumps >{threshold}x in {column}"
            })
            logger.warning(f"{self.name}: Found {num_outliers} outliers in {column}")
            return True, num_outliers
        
        return False, 0
    
    def check_missing_values(self) -> Dict[str, int]:
        """
        Check for missing values in each column.
        
        Returns:
            Dictionary of column: num_missing
        """
        missing = self.df.isnull().sum()
        missing_dict = missing[missing > 0].to_dict()
        
        if missing_dict:
            self.issues.append({
                'type': 'missing_values',
                'severity': 'low',
                'details': {k: int(v) for k, v in missing_dict.items()},
                'message': f"Missing values in {len(missing_dict)} columns"
            })
            logger.info(f"{self.name}: Missing values - {missing_dict}")
        
        return {k: int(v) for k, v in missing_dict.items()}
    
    def check_date_continuity(self, max_gap_days: int = 7) -> Dict[str, List]:
        """
        Check for gaps in trading dates per symbol.
        
        Args:
            max_gap_days: Maximum acceptable gap in trading days
            
        Returns:
            Dictionary of symbol: list of gaps
        """
        if 'date' not in self.df.columns or 'symbol' not in self.df.columns:
            return {}
        
        gaps_by_symbol = {}
        
        for symbol in self.df['symbol'].unique():
            symbol_df = self.df[self.df['symbol'] == symbol].sort_values('date')
            dates = pd.to_datetime(symbol_df['date'])
            
            # Calculate gaps
            date_diffs = dates.diff().dt.days
            large_gaps = date_diffs[date_diffs > max_gap_days]
            
            if len(large_gaps) > 0:
                gaps_by_symbol[symbol] = large_gaps.tolist()
        
        if gaps_by_symbol:
            total_gaps = sum(len(v) for v in gaps_by_symbol.values())
            self.issues.append({
                'type': 'date_gaps',
                'severity': 'low',
                'count': total_gaps,
                'symbols_affected': len(gaps_by_symbol),
                'message': f"Found {total_gaps} date gaps >{max_gap_days} days in {len(gaps_by_symbol)} symbols"
            })
            logger.info(f"{self.name}: Found date gaps in {len(gaps_by_symbol)} symbols")
        
        return gaps_by_symbol
    
    def check_zero_volume(self) -> Tuple[int, float]:
        """
        Check for zero-volume trading days.
        
        Returns:
            (num_zero_volume_days, percentage)
        """
        if 'volume' not in self.df.columns:
            return 0, 0.0
        
        zero_volume = (self.df['volume'] == 0).sum()
        percentage = (zero_volume / len(self.df)) * 100
        
        if zero_volume > 0:
            self.issues.append({
                'type': 'zero_volume',
                'severity': 'low',
                'count': int(zero_volume),
                'percentage': round(percentage, 2),
                'message': f"Found {zero_volume} zero-volume days ({percentage:.2f}%)"
            })
            logger.info(f"{self.name}: {zero_volume} zero-volume days ({percentage:.2f}%)")
        
        return int(zero_volume), percentage
    
    def validate_all(self) -> Dict:
        """
        Run all validation checks.
        
        Returns:
            Validation report dictionary
        """
        logger.info(f"Running validation on {self.name}")
        
        # Run all checks
        has_dupes, num_dupes = self.check_duplicates()
        has_outliers, num_outliers = self.check_outliers()
        missing = self.check_missing_values()
        gaps = self.check_date_continuity()
        zero_vol, zero_vol_pct = self.check_zero_volume()
        
        # Generate report
        report = {
            'dataset': self.name,
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'date_range': {
                'start': str(self.df['date'].min()) if 'date' in self.df.columns else None,
                'end': str(self.df['date'].max()) if 'date' in self.df.columns else None
            },
            'num_symbols': int(self.df['symbol'].nunique()) if 'symbol' in self.df.columns else 0,
            'issues': self.issues,
            'summary': {
                'duplicates': num_dupes,
                'outliers': num_outliers,
                'missing_values': sum(missing.values()),
                'date_gaps': len(gaps),
                'zero_volume_days': zero_vol
            }
        }
        
        logger.info(f"Validation complete: {len(self.issues)} issues found")
        
        return report
    
    def save_report(self, output_path: Path) -> None:
        """
        Save validation report to JSON file.
        
        Args:
            output_path: Path to save report
        """
        report = self.validate_all()
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Validation report saved to {output_path}")
