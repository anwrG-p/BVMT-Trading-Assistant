"""Base file loader with Factory pattern."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import pandas as pd
import chardet

from src.utils import logger, DataLoadError
from src.data.schema import standardize_columns, parse_french_date, apply_schema, STOCK_SCHEMA


class BaseFileLoader(ABC):
    """Abstract base class for file loaders."""
    
    def __init__(self, file_path: Path):
        """
        Initialize loader.
        
        Args:
            file_path: Path to file to load
        """
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise DataLoadError(f"File not found: {file_path}")
    
    @abstractmethod
    def load(self) -> pd.DataFrame:
        """Load data from file."""
        pass
    
    def detect_encoding(self) -> str:
        """
        Detect file encoding.
        
        Returns:
            Detected encoding (e.g., 'utf-8', 'latin-1')
        """
        with open(self.file_path, 'rb') as f:
            result = chardet.detect(f.read(100000))  # Read first 100KB
        
        encoding = result['encoding'] or 'utf-8'
        confidence = result['confidence']
        
        logger.debug(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
        
        # Fallback to utf-8 if confidence is low
        if confidence < 0.7:
            logger.warning(f"Low encoding confidence ({confidence:.2f}), using UTF-8")
            encoding = 'utf-8'
        
        return encoding


class CSVLoader(BaseFileLoader):
    """Loader for CSV files (2022-2025 data)."""
    
    def load(self) -> pd.DataFrame:
        """
        Load CSV file with semicolon separator.
        
        Returns:
            DataFrame with standardized columns
        """
        logger.info(f"Loading CSV file: {self.file_path.name}")
        
        try:
            encoding = self.detect_encoding()
            
            # Load CSV with semicolon separator
            df = pd.read_csv(
                self.file_path,
                sep=';',
                encoding=encoding,
                dtype=str,  # Load as string first
                na_values=['', 'NA', 'N/A', 'null']
            )
            
            # Standardize column names
            df = standardize_columns(df)
            
            # Parse date column
            if 'date' in df.columns:
                df['date'] = df['date'].apply(parse_french_date)
            
            # Apply schema
            df = apply_schema(df, STOCK_SCHEMA)
            
            logger.info(f"Loaded {len(df)} rows from {self.file_path.name}")
            
            return df
            
        except Exception as e:
            raise DataLoadError(f"Failed to load CSV {self.file_path}: {str(e)}")


class TXTLoader(BaseFileLoader):
    """Loader for TXT files (2012-2021 data)."""
    
    def load(self) -> pd.DataFrame:
        """
        Load TXT file with robust separation handling.
        
        Returns:
            DataFrame with standardized columns
        """
        logger.info(f"Loading TXT file: {self.file_path.name}")
        
        try:
            encoding = self.detect_encoding()
            
            # Strategy 1: Try Tab Separator first (common in older BVMT files)
            try:
                df = pd.read_csv(
                    self.file_path,
                    sep='\t',
                    encoding=encoding,
                    dtype=str,
                    na_values=['', 'NA', 'N/A', 'null'],
                    on_bad_lines='warn'
                )
                if len(df.columns) <= 1:
                    raise ValueError("Tab separator failed")
            except Exception:
                # Strategy 2: Regex whitespace separator
                try:
                    df = pd.read_csv(
                        self.file_path,
                        sep=r'\s+',
                        encoding=encoding,
                        dtype=str,
                        na_values=['', 'NA', 'N/A', 'null'],
                        engine='python',
                        on_bad_lines='skip'  # Skip bad lines to salvage data
                    )
                except Exception as e:
                    # Strategy 3: Fixed width or messier format - try to just read and log error
                    logger.error(f"Failed to parse {self.file_path.name} with standard separators")
                    raise e
            
            # Standardize column names
            df = standardize_columns(df)
            
            # Parse date column
            if 'date' in df.columns:
                df['date'] = df['date'].apply(parse_french_date)
            
            # Apply schema
            df = apply_schema(df, STOCK_SCHEMA)
            
            logger.info(f"Loaded {len(df)} rows from {self.file_path.name}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to load TXT {self.file_path}: {str(e)}")
            # Return empty DataFrame instead of raising to allow partial loading
            return pd.DataFrame()


class ExcelLoader(BaseFileLoader):
    """Loader for Excel files (dividend data)."""
    
    def load(self, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Load Excel file.
        
        Args:
            sheet_name: Sheet name to load (default: first sheet)
            
        Returns:
            DataFrame with dividend data
        """
        logger.info(f"Loading Excel file: {self.file_path.name}")
        
        try:
            # Determine engine based on file extension
            engine = 'xlrd' if self.file_path.suffix == '.xls' else 'openpyxl'
            
            # Load Excel file
            df = pd.read_excel(
                self.file_path,
                sheet_name=sheet_name or 0,
                engine=engine
            )
            
            logger.info(f"Loaded {len(df)} rows from {self.file_path.name}")
            
            return df
            
        except Exception as e:
            raise DataLoadError(f"Failed to load Excel {self.file_path}: {str(e)}")


class FileLoaderFactory:
    """Factory for creating appropriate file loaders."""
    
    @staticmethod
    def create_loader(file_path: Path) -> BaseFileLoader:
        """
        Create appropriate loader based on file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Appropriate file loader instance
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension == '.csv':
            return CSVLoader(file_path)
        elif extension == '.txt':
            return TXTLoader(file_path)
        elif extension in ['.xls', '.xlsx']:
            return ExcelLoader(file_path)
        else:
            raise DataLoadError(f"Unsupported file type: {extension}")
