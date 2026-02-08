
import requests
from bs4 import BeautifulSoup

url = 'https://www.ilboursa.com'
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    r = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    links = soup.find_all('a', href=True)
    news_links = []
    
    for l in links:
        href = l['href']
        text = l.get_text(strip=True)
        if '/marches/' in href and 'cotation' not in href and len(text) > 15:
            news_links.append({'text': text, 'href': href})
            
    print(f"Found {len(news_links)} potential news links:")
    for l in news_links[:20]:
        print(f" - {l['text'][:50]}... -> {l['href']}")
        
except Exception as e:
    print(e)
