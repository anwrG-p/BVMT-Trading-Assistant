
import requests
from bs4 import BeautifulSoup

url = "https://www.ilboursa.com"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Connecting to {url}...")
try:
    response = requests.get(url, headers=headers, timeout=20)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        print(f"Found {len(links)} links.")
        
        forum_links = []
        for l in links:
            if 'forum' in l['href'].lower() or 'forum' in l.get_text().lower():
                forum_links.append((l.get_text(strip=True), l['href']))
        
        print(f"Forum links found: {forum_links}")
        
except Exception as e:
    print(f"Error: {e}")

