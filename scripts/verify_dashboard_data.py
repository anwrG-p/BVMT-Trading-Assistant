import requests
import sys
import json

API_URL = "http://localhost:8000"

def test_dashboard_endpoints():
    print("Testing Dashboard Endpoints...")
    
    # 1. Metrics (Feature Importance)
    print("\n1. Testing /metrics (Feature Importance)...")
    try:
        r = requests.get(f"{API_URL}/metrics")
        if r.status_code == 200:
            data = r.json()
            if 'feature_importance' in data and data['feature_importance']:
                fi = data['feature_importance']
                print(f"✓ Feature importance found: {len(fi)} features")
                print(f"  Top feature: {fi[0]}")
            else:
                print("✗ Feature importance MISSING or EMPTY in response")
        else:
            print(f"✗ Failed: {r.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # 2. Visualization Data
    print("\n2. Testing /visualization/100010...")
    try:
        r = requests.get(f"{API_URL}/visualization/100010")
        if r.status_code == 200:
            data = r.json()
            points = data.get('data', [])
            history = [p for p in points if p['type'] == 'history']
            forecast = [p for p in points if p['type'] == 'forecast']
            
            print(f"✓ Visualization data found: {len(points)} points")
            print(f"  History points: {len(history)}")
            print(f"  Forecast points: {len(forecast)}")
            
            if forecast:
                print(f"  First forecast: {forecast[0]}")
        else:
            print(f"✗ Failed to get visualization data: {r.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_dashboard_endpoints()
