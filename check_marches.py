
import requests
from bs4 import BeautifulSoup

url = "https://www.ilboursa.com/marches"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Checking {url}...")
try:
    response = requests.get(url, headers=headers, timeout=20)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for potential article links
        # Often in 'h1', 'h2', 'h3' or specific classes
        articles = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if len(text) > 10 and '/marches/' in href and not any(x in href for x in ['user', 'login']):
                 articles.append({'title': text, 'url': href})
                 
        print(f"Found {len(articles)} potential articles (first 5):")
        for art in articles[:5]:
            print(f" - {art['title']} -> {art['url']}")
            
        # Check for comments structure in an article if possible
        if articles:
            sample_art = articles[0]['url']
            if not sample_art.startswith('http'):
                sample_art = "https://www.ilboursa.com" + sample_art
            
            print(f"\nChecking sample article: {sample_art}")
            art_resp = requests.get(sample_art, headers=headers, timeout=20)
            art_soup = BeautifulSoup(art_resp.text, 'html.parser')
            
            # Look for comments section
            comments = art_soup.find_all(lambda tag: tag.name in ['div', 'section'] and any(c in (tag.get('class') or []) for c in ['comments', 'commentaires', 'reaction']))
            print(f"Found {len(comments)} comment sections/containers.")
            
            # Look for specific comment elements
            individual_comments = art_soup.find_all(lambda tag: tag.name in ['div', 'li'] and ('comment' in str(tag.get('class')) or 'avis' in str(tag.get('class'))))
            print(f"Found {len(individual_comments)} individual comment elements.")
            
except Exception as e:
    print(f"Error: {e}")
