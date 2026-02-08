
import requests
from bs4 import BeautifulSoup

url = "https://www.ilboursa.com"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Analyzing links on {url}...")
try:
    response = requests.get(url, headers=headers, timeout=20)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        marches_links = []
        for l in links:
            href = l['href']
            if '/marches/' in href:
                marches_links.append(href)
        
        print(f"Found {len(marches_links)} links under /marches/.")
        print("First 20 unique links:")
        for l in sorted(list(set(marches_links)))[:20]:
            print(f" - {l}")

except Exception as e:
    print(f"Error: {e}")
