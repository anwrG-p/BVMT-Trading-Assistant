
import requests

url = 'https://www.ilboursa.com/forums/display2?id=10005'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    r = requests.get(url, headers=headers, timeout=20)
    with open('topic_structure.html', 'w', encoding='utf-8') as f:
        f.write(r.text)
    print("Dumped topic structure to topic_structure.html")
except Exception as e:
    print(e)
