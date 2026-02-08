
import requests
from bs4 import BeautifulSoup

url = 'https://www.ilboursa.com'
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    r = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    print("Top Headings:")
    for h in soup.find_all(['h1', 'h2', 'h3'])[:30]:
        text = h.get_text(strip=True)
        link = h.find('a')['href'] if h.find('a') else 'No link'
        print(f"{h.name}: {text[:50]}... -> {link}")
        
except Exception as e:
    print(e)
