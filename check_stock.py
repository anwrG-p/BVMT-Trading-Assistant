
import requests
from bs4 import BeautifulSoup

url = 'https://www.ilboursa.com/marches/cotation_ATL'
headers = {'User-Agent': 'Mozilla/5.0'}

print(f"Checking {url}...")
try:
    r = requests.get(url, headers=headers, timeout=20)
    print(f"Status: {r.status_code}")
    
    keywords_found = [w for w in ['forum', 'comment', 'avis', 'discussion'] if w in r.text.lower()]
    print(f"Keywords found: {keywords_found}")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    
    forum_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True).lower()
        if 'forum' in href.lower() or 'forum' in text or 'avis' in href or 'avis' in text:
            forum_links.append({'text': text, 'href': href})
            
    print(f"Forum/Discussion links: {forum_links}")
    
except Exception as e:
    print(f"Error: {e}")
