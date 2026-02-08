
import requests
from bs4 import BeautifulSoup

url = 'https://www.ilboursa.com/forums/display2?id=10005'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

print(f"Checking {url}...")
try:
    r = requests.get(url, headers=headers, timeout=20)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Try various selectors for comments/messages
        messages = soup.select('.message') or soup.find_all('td', class_='contenu_message') or soup.select('.forum_message')
        
        print(f"Messages found: {len(messages)}")
        
        if messages:
            print("First message snippet:")
            print(messages[0].get_text(strip=True)[:100])
             
        # Check for user info
        users = soup.select('.username') or soup.select('.user_info')
        print(f"Users found: {len(users)}")
        
except Exception as e:
    print(f"Error: {e}")
