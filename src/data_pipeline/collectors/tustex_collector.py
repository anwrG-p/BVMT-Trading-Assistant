"""
Tustex News Collector

Scrapes economic news articles from Tustex.com for NLP sentiment analysis.
"""

import os
import random
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from loguru import logger


class TustexCollector:
    """Collector for Tustex economic news articles."""
    
    BASE_URL = "https://www.tustex.com/economie/actualites-economiques"
    
    # Request configuration
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    
    def __init__(self, num_pages: int = 3):
        """
        Initialize the Tustex collector.
        
        Args:
            num_pages: Number of pages to scrape (default: 3)
        """
        load_dotenv()
        
        self.num_pages = num_pages
        self.raw_data_path = os.getenv("RAW_DATA_PATH", "data/raw")
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        
        logger.info(f"TustexCollector initialized. Will scrape {num_pages} pages.")
        logger.info(f"Output path: {self.raw_data_path}")
    
    def _random_delay(self, min_sec: float = 2.0, max_sec: float = 5.0) -> None:
        """Add random delay to avoid rate limiting."""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def _get_page_url(self, page_num: int) -> str:
        """
        Get URL for a specific page.
        
        Args:
            page_num: Page number (1-indexed)
            
        Returns:
            URL string
        """
        if page_num == 1:
            return self.BASE_URL
        return f"{self.BASE_URL}?page={page_num - 1}"
    
    def _fetch_page(self, url: str, max_retries: int = 3) -> BeautifulSoup | None:
        """
        Fetch a page with retry logic.
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retries
            
        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.text, "html.parser")
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2  # Exponential backoff
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
    
    def _get_page_articles(self, page_num: int) -> list[dict]:
        """
        Get article links and titles from a listing page.
        
        Args:
            page_num: Page number (1-indexed)
            
        Returns:
            List of dicts with 'title' and 'url' keys
        """
        url = self._get_page_url(page_num)
        logger.info(f"Fetching article list from page {page_num}: {url}")
        
        soup = self._fetch_page(url)
        if not soup:
            return []
        
        articles = []
        
        # Find article links in the main content area
        # Tustex uses links with pattern: /economie-actualites-economiques/
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if "/economie-actualites-economiques/" in href and "Lire la suite" not in link.get_text():
                title = link.get_text(strip=True)
                if title and len(title) > 10:  # Filter out short/empty titles
                    full_url = href if href.startswith("http") else f"https://www.tustex.com{href}"
                    
                    # Avoid duplicates
                    if not any(a["url"] == full_url for a in articles):
                        articles.append({
                            "title": title,
                            "url": full_url
                        })
        
        logger.info(f"Found {len(articles)} articles on page {page_num}")
        return articles
    
    def _get_article_content(self, article: dict) -> dict:
        """
        Fetch full content of an article.
        
        Args:
            article: Dict with 'title' and 'url' keys
            
        Returns:
            Dict with 'title', 'date', 'full_text' keys
        """
        self._random_delay()  # Respect rate limits
        
        soup = self._fetch_page(article["url"])
        if not soup:
            return {
                "title": article["title"],
                "date": "",
                "full_text": ""
            }
        
        # Extract date - look for common date patterns
        date = ""
        date_elem = soup.find("span", class_="date") or soup.find("time") or soup.find(class_="submitted")
        if date_elem:
            date = date_elem.get_text(strip=True)
        
        # Extract article body
        full_text = ""
        
        # Try different selectors for article content
        content_selectors = [
            ("div", {"class": "field-name-body"}),
            ("div", {"class": "content"}),
            ("article", {}),
            ("div", {"class": "node-content"}),
        ]
        
        for tag, attrs in content_selectors:
            content_elem = soup.find(tag, attrs) if attrs else soup.find(tag)
            if content_elem:
                # Get all paragraph text
                paragraphs = content_elem.find_all("p")
                if paragraphs:
                    full_text = "\n".join(p.get_text(strip=True) for p in paragraphs)
                    break
        
        # Fallback: get text from main content area
        if not full_text:
            main_content = soup.find("main") or soup.find("div", {"id": "content"})
            if main_content:
                paragraphs = main_content.find_all("p")
                full_text = "\n".join(p.get_text(strip=True) for p in paragraphs[:10])  # Limit to first 10 paragraphs
        
        return {
            "title": article["title"],
            "date": date,
            "full_text": full_text
        }
    
    def _save_to_csv(self, articles: list[dict]) -> str:
        """
        Save articles to CSV file.
        
        Args:
            articles: List of article dicts
            
        Returns:
            Path to saved CSV file
        """
        # Ensure output directory exists
        output_dir = Path(self.raw_data_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "tustex_news.csv"
        
        df = pd.DataFrame(articles)
        df.to_csv(output_path, index=False, encoding="utf-8")
        
        logger.info(f"Saved {len(articles)} articles to {output_path}")
        return str(output_path)
    
    def scrape(self) -> str:
        """
        Main scraping method. Scrapes articles from configured number of pages.
        
        Returns:
            Path to output CSV file
        """
        logger.info(f"Starting Tustex scrape for {self.num_pages} pages...")
        
        all_articles = []
        
        for page_num in range(1, self.num_pages + 1):
            # Get article links from listing page
            page_articles = self._get_page_articles(page_num)
            
            # Fetch full content for each article
            for article in page_articles:
                article_data = self._get_article_content(article)
                all_articles.append(article_data)
                logger.debug(f"Scraped: {article_data['title'][:50]}...")
            
            # Delay between pages
            if page_num < self.num_pages:
                self._random_delay(3.0, 6.0)
        
        logger.success(f"Successfully collected {len(all_articles)} articles from {self.num_pages} pages")
        
        # Save to CSV
        output_path = self._save_to_csv(all_articles)
        
        return output_path


def main():
    """Run the Tustex collector."""
    collector = TustexCollector(num_pages=3)
    output_file = collector.scrape()
    print(f"Output saved to: {output_file}")


if __name__ == "__main__":
    main()
