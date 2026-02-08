"""
Central Bank of Tunisia (BCT) Exchange Rates Collector

Scrapes official exchange rates from the BCT website.
These are the official fixing rates used for TND valuations.
"""

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from loguru import logger


class BCTCollector:
    """Collector for official exchange rates from the Central Bank of Tunisia."""
    
    # The full exchange rate table is on this page
    TARGET_URL = "https://www.bct.gov.tn/bct/siteprod/cours.jsp?la=FR"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    }
    
    def __init__(self):
        """Initialize the BCT collector."""
        load_dotenv()
        
        self.raw_data_path = os.getenv("RAW_DATA_PATH", "data/raw")
        logger.info("BCTCollector initialized.")
        logger.info(f"Target URL: {self.TARGET_URL}")
        logger.info(f"Output path: {self.raw_data_path}")
    
    def _find_exchange_table(self, tables: list[pd.DataFrame]) -> pd.DataFrame | None:
        """
        Find the exchange rate table by looking for 'Dinar' or 'Devise'.
        
        Args:
            tables: List of DataFrames from pd.read_html
            
        Returns:
            The exchange rate DataFrame or None if not found
        """
        for i, table in enumerate(tables):
            table_str = table.to_string().upper()
            if "DINAR" in table_str or "DEVISE" in table_str:
                logger.info(f"Found exchange rate table at index {i}")
                return table
        
        logger.warning("No table with 'Dinar' or 'Devise' found")
        return None
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the extracted DataFrame.
        
        BCT table structure: Monnaie (Currency), Code, Unité (Unit), Valeur (Rate)
        We extract: Currency (col 0), Unit (col 2), Rate (col 3)
        
        Args:
            df: Raw DataFrame from read_html
            
        Returns:
            Cleaned DataFrame with Currency, Unit, Rate columns
        """
        # Make a copy
        cleaned_df = df.copy()
        
        logger.info(f"Raw table columns: {list(cleaned_df.columns)}")
        logger.info(f"Raw table shape: {cleaned_df.shape}")
        
        # Drop rows where all values are NaN
        cleaned_df = cleaned_df.dropna(how="all")
        
        num_cols = len(cleaned_df.columns)
        
        # BCT table typically has 4 columns: Monnaie, Code, Unité, Valeur
        if num_cols >= 4:
            # Select columns: Currency (0), Unit (2), Rate (3)
            cleaned_df = cleaned_df.iloc[:, [0, 2, 3]]
            cleaned_df.columns = ["Currency", "Unit", "Rate"]
        elif num_cols == 3:
            cleaned_df.columns = ["Currency", "Unit", "Rate"]
        else:
            logger.warning(f"Unexpected column count: {num_cols}")
            return pd.DataFrame()
        
        # Convert to string for cleaning
        cleaned_df["Currency"] = cleaned_df["Currency"].astype(str)
        cleaned_df["Unit"] = cleaned_df["Unit"].astype(str)
        cleaned_df["Rate"] = cleaned_df["Rate"].astype(str)
        
        # Remove header rows (where Currency = 'Monnaie' or Rate = 'Valeur')
        cleaned_df = cleaned_df[~cleaned_df["Currency"].str.lower().isin(["monnaie", "devise"])]
        cleaned_df = cleaned_df[~cleaned_df["Rate"].str.lower().isin(["valeur", "cours"])]
        
        # Remove rows with 'None', 'nan', or empty values
        cleaned_df = cleaned_df[~cleaned_df["Currency"].str.lower().isin(['none', 'nan', ''])]
        cleaned_df = cleaned_df[~cleaned_df["Rate"].str.lower().isin(['none', 'nan', ''])]
        
        # Convert Rate to numeric (handle comma as decimal separator)
        try:
            cleaned_df["Rate"] = cleaned_df["Rate"].str.replace(',', '.').str.strip()
            cleaned_df["Rate"] = pd.to_numeric(cleaned_df["Rate"], errors="coerce")
        except Exception as e:
            logger.warning(f"Could not convert Rate to float: {e}")
        
        # Convert Unit to numeric
        try:
            cleaned_df["Unit"] = pd.to_numeric(cleaned_df["Unit"], errors="coerce").fillna(1).astype(int)
        except Exception as e:
            logger.warning(f"Could not convert Unit: {e}")
        
        # Drop rows where Rate is NaN (failed conversion)
        cleaned_df = cleaned_df.dropna(subset=["Rate"])
        
        # Add timestamp
        cleaned_df["scraped_at"] = datetime.now().isoformat()
        
        # Reset index
        cleaned_df = cleaned_df.reset_index(drop=True)
        
        logger.info(f"Cleaned DataFrame has {len(cleaned_df)} rows")
        return cleaned_df
    
    def _save_to_csv(self, df: pd.DataFrame) -> str:
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            
        Returns:
            Path to saved CSV file
        """
        output_dir = Path(self.raw_data_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "bct_fixing_rates.csv"
        
        df.to_csv(output_path, index=False, encoding="utf-8")
        logger.info(f"Saved {len(df)} rows to {output_path}")
        
        return str(output_path)
    
    def scrape(self) -> pd.DataFrame | None:
        """
        Main scraping method. Fetches and cleans BCT exchange rates.
        
        Uses requests to fetch HTML, then pandas.read_html to parse tables.
        
        Returns:
            Cleaned DataFrame or None if scraping failed
        """
        logger.info("Starting BCT exchange rate scrape...")
        
        try:
            # Fetch HTML with requests for better encoding handling
            response = requests.get(self.TARGET_URL, headers=self.HEADERS, timeout=30)
            response.raise_for_status()
            
            # BCT site uses ISO-8859-1 or Windows-1252 encoding
            response.encoding = response.apparent_encoding or 'utf-8'
            html = response.text
            
            logger.info(f"Successfully fetched BCT page (status: {response.status_code})")
            
            # Parse all tables from the HTML
            from io import StringIO
            tables = pd.read_html(StringIO(html))
            logger.info(f"Found {len(tables)} tables on the page")
            
            if not tables:
                logger.warning("No tables found on the page")
                return None
            
        except Exception as e:
            logger.error(f"Failed to fetch tables from BCT page: {e}")
            return None
        
        # Find the exchange rate table
        raw_df = self._find_exchange_table(tables)
        if raw_df is None or raw_df.empty:
            logger.warning("No exchange rate data extracted")
            return None
        
        # Clean the data
        cleaned_df = self._clean_dataframe(raw_df)
        
        if cleaned_df.empty:
            logger.warning("Cleaned DataFrame is empty")
            return None
        
        # Save to CSV
        self._save_to_csv(cleaned_df)
        
        logger.success(f"Successfully extracted {len(cleaned_df)} exchange rates")
        return cleaned_df


def main():
    """Run the BCT collector and print sample data."""
    collector = BCTCollector()
    df = collector.scrape()
    
    if df is not None:
        print("\n" + "=" * 60)
        print("BCT Exchange Rates - First 5 Rows:")
        print("=" * 60)
        print(df.head().to_string())
        print("=" * 60)
        print(f"\nTotal rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
    else:
        print("Failed to scrape BCT exchange rates")


if __name__ == "__main__":
    main()
