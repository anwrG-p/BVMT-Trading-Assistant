
import requests
from bs4 import BeautifulSoup

url = 'https://www.ilboursa.com/forums/display2?id=3'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Checking {url}...")
try:
    r = requests.get(url, headers=headers, timeout=20)
    print(f"Status: {r.status_code}")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables")
    
    for i, table in enumerate(tables):
        rows = table.find_all('tr')
        print(f"Table {i} has {len(rows)} rows.")
        if len(rows) > 0:
            header_cells = rows[0].find_all(['th', 'td'])
            print(f"  Header/Row 0: {[c.get_text(strip=True) for c in header_cells]}")
            
        # Check first row for links
        if len(rows) > 1:
            cells = rows[1].find_all('td')
            links = []
            for c in cells:
                a = c.find('a', href=True)
                if a:
                    links.append((a.get_text(strip=True), a['href']))
            print(f"  Row 1 links: {links}")
            
except Exception as e:
    print(e)
