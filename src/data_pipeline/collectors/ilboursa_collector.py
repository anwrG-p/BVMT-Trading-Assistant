
import requests
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
import time
import random
import re
import os
from datetime import datetime
from urllib.parse import urljoin

class IlBoursaCollector:
    ENTRY_POINT = "https://www.ilboursa.com/forums/display2?id=3"
    BASE_URL = "https://www.ilboursa.com/forums/"
    OUTPUT_PATH = "data/raw/ilboursa_comments.csv"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.ilboursa.com/",
    }

    def __init__(self):
        os.makedirs(os.path.dirname(self.OUTPUT_PATH), exist_ok=True)
        logger.info("IlBoursaCollector initialized")

    def _fetch_page(self, url):
        """ robust fetch with retry """
        try:
            time.sleep(random.uniform(1.0, 2.0)) # Politeness delay
            response = requests.get(url, headers=self.HEADERS, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _extract_topics(self, html):
        """ Extract first 15 topics from the index page """
        topics = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # The main table usually has class 'tablenosort' or 'tbl100_6' (based on dump checks)
        # We look for rows in the table
        tables = soup.find_all('table')
        if not tables:
            logger.warning("No tables found on index page")
            return []
            
        # Usually the first relevant table contains the topics
        # Based on index check, row 1 had links.
        # We iterate through rows skipping header
        
        main_table = tables[0] 
        rows = main_table.find_all('tr')
        
        count = 0
        for row in rows:
            # Skip header (usually has th)
            if row.find('th'):
                continue
                
            # Look for the topic link. Usually in the first main cell.
            # cell structure: <td><a href="...">Topic Title</a></td>
            cells = row.find_all('td')
            if not cells:
                continue
                
            # The topic link is usually the first link in the row
            link = row.find('a', href=True)
            if link:
                href = link['href']
                title = link.get_text(strip=True)
                
                # Filter out profile links if they appear first (unlikely based on dump, but possible)
                if 'profile?' in href:
                    # Try next link
                    links = row.find_all('a', href=True)
                    for l in links:
                        if 'profile?' not in l['href']:
                            href = l['href']
                            title = l.get_text(strip=True)
                            break
                
                # Construct full URL
                if not href.startswith('http'):
                    # The user said links are relative e.g., /forums/313868... 
                    # But the base is likely https://www.ilboursa.com/forums/
                    # Only if href doesn't start with /forums
                    if href.startswith('display2'): 
                        # display2?id=...
                        full_url = urljoin(self.BASE_URL, href)
                    elif not href.startswith('/'):
                        # e.g. "236968_atl-analyse" -> join with BASE_URL
                        full_url = urljoin(self.BASE_URL, href)
                    else:
                        full_url = "https://www.ilboursa.com" + href
                else:
                    full_url = href

                topics.append({'title': title, 'url': full_url})
                count += 1
                if count >= 15:
                    break
        
        logger.info(f"Extracted {len(topics)} topics")
        return topics

    def _extract_comments(self, html, source_topic):
        """ Extract comments from a topic page """
        comments = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Selector: div.fo_cont1
        comment_divs = soup.find_all('div', class_='fo_cont1')
        
        for div in comment_divs:
            try:
                # Author
                author_tag = div.select_one('.fo_lft a.lkg')
                author = author_tag.get_text(strip=True) if author_tag else "Unknown"
                
                # Content wrapper: div.fo_rt
                content_div = div.select_one('.fo_rt')
                if not content_div:
                    continue
                    
                # Date
                date_div = content_div.select_one('.fo_dt')
                post_date = date_div.get_text(strip=True) if date_div else ""
                # Clean date: "Posté le 08/04/2025 12:25:33" -> "08/04/2025 12:25:33"
                post_date = post_date.replace("Posté le ", "").strip()
                
                # Text
                # Extract text from p tags in content_div
                # But filter out the date div text
                
                # Alternative: get all text and strip date
                full_text = content_div.get_text(" ", strip=True)
                # Remove date string
                if date_div:
                   date_text = date_div.get_text(strip=True)
                   full_text = full_text.replace(date_text, "").strip()
                   
                # Also remove "Répondre" button text if captured
                full_text = re.sub(r'Répondre\s*$', '', full_text).strip()
                
                # Spam Filter
                # 1. Short repetitive text?
                # 2. Non-financial ads? (Hard to detect without complex logic, use length heuristic)
                if len(full_text) < 5: # Too short
                    continue
                
                comments.append({
                    'source_topic': source_topic,
                    'author': author,
                    'text': full_text,
                    'date_posted': post_date,
                    'date_scraped': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.warning(f"Error parsing comment in {source_topic}: {e}")
                continue
                
        return comments

    def scrape(self):
        logger.info(f"Starting IlBoursa scrape from {self.ENTRY_POINT}")
        
        # 1. Indexing
        index_html = self._fetch_page(self.ENTRY_POINT)
        if not index_html:
            logger.error("Failed to fetch index page. Aborting.")
            return
            
        topics = self._extract_topics(index_html)
        if not topics:
            logger.error("No topics found. Aborting.")
            return

        all_comments = []
        
        # 2. Deep Crawl
        for i, topic in enumerate(topics):
            logger.info(f"Crawling topic {i+1}/{len(topics)}: {topic['title']}")
            
            topic_html = self._fetch_page(topic['url'])
            if topic_html:
                comments = self._extract_comments(topic_html, topic['title'])
                all_comments.extend(comments)
                logger.info(f"  Found {len(comments)} comments")
            
        # 3. Save
        if all_comments:
            df = pd.DataFrame(all_comments)
            df.to_csv(self.OUTPUT_PATH, index=False, encoding='utf-8-sig')
            logger.info(f"Saved {len(df)} comments to {self.OUTPUT_PATH}")
            return df
        else:
            logger.warning("No comments extracted.")
            return None

if __name__ == "__main__":
    collector = IlBoursaCollector()
    collector.scrape()
