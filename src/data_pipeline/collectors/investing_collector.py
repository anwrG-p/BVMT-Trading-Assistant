"""
Investing.com Currency Rates Collector

Scrapes real-time currency exchange rates for major pairs.
These rates influence the Tunisian Dinar (TND) intrinsic value calculations for the NLP model.
"""

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

# Playwright with stealth plugin for bot detection bypass
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth


class InvestingCollector:
    """Collector for real-time currency rates from Investing.com."""
    
    # Direct URLs for each currency pair (more reliable than scraping a table)
    TARGET_PAIRS = {
        "EUR/USD": "https://www.investing.com/currencies/eur-usd",
        "GBP/USD": "https://www.investing.com/currencies/gbp-usd",
        "USD/JPY": "https://www.investing.com/currencies/usd-jpy",
    }
    
    def __init__(self):
        """Initialize the Investing.com collector."""
        load_dotenv()
        
        self.raw_data_path = os.getenv("RAW_DATA_PATH", "data/raw")
        logger.info("InvestingCollector initialized.")
        logger.info(f"Output path: {self.raw_data_path}")
        logger.info(f"Target pairs: {list(self.TARGET_PAIRS.keys())}")
    
    def _extract_rate_from_page(self, page, symbol: str) -> dict | None:
        """
        Extract currency rate from a dedicated pair page.
        
        Args:
            page: Playwright page object
            symbol: Currency pair symbol (e.g., "EUR/USD")
            
        Returns:
            Dict with 'symbol', 'last_price', 'scraped_at' or None if failed
        """
        try:
            scraped_at = datetime.now().isoformat()
            
            # Wait for the price element to load - multiple fallback selectors
            selectors = [
                'span[data-test="instrument-price-last"]',
                'div[data-test="instrument-price-last"]',
                '.text-5xl.font-bold',
                '#last_last',
                '.instrument-price_last__KQzyA',
            ]
            
            last_price = None
            for selector in selectors:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    elem = page.query_selector(selector)
                    if elem:
                        last_price = elem.inner_text().strip()
                        if last_price:
                            break
                except Exception:
                    continue
            
            if not last_price:
                logger.warning(f"Could not extract price for {symbol}")
                return None
            
            logger.info(f"Extracted: {symbol} = {last_price}")
            return {
                "symbol": symbol,
                "last_price": last_price,
                "scraped_at": scraped_at
            }
            
        except Exception as e:
            logger.warning(f"Error extracting rate for {symbol}: {e}")
            return None
    
    def _save_to_csv(self, rates: list[dict]) -> str:
        """
        Save rates to CSV file, appending to existing data for time-series.
        
        Args:
            rates: List of rate dicts
            
        Returns:
            Path to saved CSV file
        """
        # Ensure output directory exists
        output_dir = Path(self.raw_data_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "global_indicators.csv"
        
        new_df = pd.DataFrame(rates)
        
        # Append to existing file or create new one
        if output_path.exists():
            existing_df = pd.read_csv(output_path)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(f"Appended {len(rates)} rates to existing file. Total rows: {len(combined_df)}")
        else:
            new_df.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(f"Created new file with {len(rates)} rates")
        
        return str(output_path)
    
    def scrape(self) -> str:
        """
        Main scraping method. Scrapes currency rates using Playwright with stealth.
        
        Returns:
            Path to output CSV file
        """
        logger.info(f"Starting Investing.com scrape for {list(self.TARGET_PAIRS.keys())}...")
        
        rates = []
        
        try:
            # Use Stealth context manager for bot detection bypass (playwright-stealth v2 API)
            with Stealth().use_sync(sync_playwright()) as p:
                # Launch browser with stealth settings
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                    ]
                )
                
                try:
                    # Create context with realistic viewport and user agent
                    context = browser.new_context(
                        viewport={"width": 1920, "height": 1080},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        locale="en-US",
                    )
                    
                    page = context.new_page()
                    
                    # Scrape each currency pair from its dedicated page
                    for symbol, url in self.TARGET_PAIRS.items():
                        logger.info(f"Fetching {symbol} from {url}")
                        
                        try:
                            page.goto(url, wait_until="domcontentloaded", timeout=60000)
                            
                            # Wait for page to stabilize
                            page.wait_for_timeout(2000)
                            
                            # Extract rate
                            rate = self._extract_rate_from_page(page, symbol)
                            if rate:
                                rates.append(rate)
                                
                        except Exception as e:
                            logger.warning(f"Failed to fetch {symbol}: {e}")
                            continue
                    
                    # Close context properly
                    context.close()
                    
                finally:
                    # Ensure browser is closed even on error
                    browser.close()
                    
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
        
        if not rates:
            logger.warning("No rates extracted. Selectors may need updating.")
            return ""
        
        logger.success(f"Successfully extracted {len(rates)} currency rates")
        
        # Save to CSV
        output_path = self._save_to_csv(rates)
        
        return output_path


def main():
    """Run the Investing.com collector."""
    collector = InvestingCollector()
    output_file = collector.scrape()
    if output_file:
        print(f"Output saved to: {output_file}")
    else:
        print("No data was collected.")


if __name__ == "__main__":
    main()

