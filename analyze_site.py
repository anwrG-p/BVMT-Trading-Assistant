import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

BASE_URL = "https://www.ilboursa.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_url(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return 0, 0
        text = r.text.lower()
        return text.count('charnière'), text.count('commentaire') + text.count('avis') + text.count('réaction')
    except:
        return 0, 0

def main():
    print(f"Scanning {BASE_URL}...")
    try:
        r = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                full_url = urljoin(BASE_URL, href)
                links.add(full_url)
        
        print(f"Found {len(links)} unique internal links.")
        
        candidates = []
        for i, link in enumerate(list(links)[:20]): # Check first 20 links
            if any(x in link for x in ['user', 'login', 'register', 'pubs']):
                continue
            
            print(f"Checking {link}...")
            _, comments_count = check_url(link)
            if comments_count > 0:
                print(f" -> Found {comments_count} potential comment markers!")
                candidates.append((link, comments_count))
            time.sleep(0.5)
            
        candidates.sort(key=lambda x: x[1], reverse=True)
        if candidates:
            print("\nBest candidates for comments:")
            for c in candidates:
                print(f"{c[0]} ({c[1]})")
        else:
            print("\nNo obvious comment sections found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
