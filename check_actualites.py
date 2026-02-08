
import requests
from bs4 import BeautifulSoup

url = 'https://www.ilboursa.com'
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    r = requests.get(url, headers=headers, timeout=20)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        links = soup.find_all('a', href=True)
        print(f"Found {len(links)} links on /actualites")
        
        # Look for potential article links
        articles = [l['href'] for l in links if '/marches/' in l['href'] or '/actualites/' in l['href']]
        print(f"Potential articles found: {len(articles)}")
        print(articles[:10])
except Exception as e:
    print(e)
