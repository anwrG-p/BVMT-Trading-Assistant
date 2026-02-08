import sys
import os
import requests
from src.data_pipeline.collectors.ilboursa_collector import IlBoursaCollector

def debug():
    try:
        collector = IlBoursaCollector()
        url = "https://www.ilboursa.com"
        print(f"Fetching {url}...")
        r = requests.get(url, headers=collector.HEADERS, timeout=10)
        
        lower_html = r.text.lower()
        
        keywords = ['sujet', 'derniers messages', 'forum', 'discussions', 'communauté']
        
        for kw in keywords:
            index = lower_html.find(kw)
            if index != -1:
                print(f"Found '{kw}' at index {index}")
                context = r.text[max(0, index-100):min(len(r.text), index+100)].replace('\n', ' ')
                print(f"Context: ...{context}...")
            else:
                print(f"Did not find '{kw}'")
                
    except Exception as e:
        print(f"Error: {e}") 

if __name__ == "__main__":
    debug()
