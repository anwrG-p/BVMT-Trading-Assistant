
import requests

url = 'https://www.ilboursa.com/forums/display2?id=10005'
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    r = requests.get(url, headers=headers, timeout=20)
    print(r.text[:2000])
except Exception as e:
    print(e)
