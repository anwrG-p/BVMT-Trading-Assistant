
import requests

url = 'https://www.ilboursa.com/forums/236968_atl-analyse'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    r = requests.get(url, headers=headers, timeout=20)
    with open('topic_thread.html', 'w', encoding='utf-8') as f:
        f.write(r.text)
    print("Dumped thread structure to topic_thread.html")
except Exception as e:
    print(e)
