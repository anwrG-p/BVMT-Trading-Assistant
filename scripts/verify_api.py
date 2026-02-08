import requests
import time
import sys
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...", end=" ")
    try:
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code == 200:
            print("OK")
            # print(json.dumps(r.json(), indent=2))
            return True
        else:
            print(f"FAILED ({r.status_code})")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_metrics():
    print("\nTesting /metrics...", end=" ")
    try:
        r = requests.get(f"{BASE_URL}/metrics")
        if r.status_code == 200:
            data = r.json()
            print("OK")
            if "price_metrics" in data:
                 print(f"  Price Metrics: {len(data['price_metrics'])} rows")
                 return True
            else:
                 print("FAILED: Missing keys")
                 return False
        else:
            print(f"FAILED ({r.status_code})")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_visualization(symbol):
    print(f"\nTesting /visualization/{symbol}...", end=" ")
    try:
        r = requests.get(f"{BASE_URL}/visualization/{symbol}")
        if r.status_code == 200:
            data = r.json()
            print("OK")
            if "data" in data and len(data["data"]) > 0:
                print(f"  Data Points: {len(data['data'])}")
                print(f"  First Point: {data['data'][0]}")
                print(f"  Last Point: {data['data'][-1]}")
                return True
            else:
                print("FAILED: No data points")
                print(data)
                return False
        else:
            print(f"FAILED ({r.status_code}): {r.text}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    # Wait for service to start
    print("Waiting for API to start...")
    started = False
    for i in range(120):
        try:
            if requests.get(f"{BASE_URL}/health").status_code == 200:
                print("\nAPI is ready.")
                started = True
                break
        except:
            time.sleep(1)
            print(".", end="", flush=True)
            
    if not started:
        print("\nAPI did not start in time.")
        sys.exit(1)
        
    # Run tests
    success = True
    success &= test_health()
    success &= test_metrics()
    
    # Get a valid symbol
    print("\nFetching available symbols...", end=" ")
    try:
        r = requests.get(f"{BASE_URL}/symbols")
        if r.status_code == 200:
            symbols = r.json().get("symbols", [])
            if symbols:
                symbol = symbols[0]
                print(f"OK (Using {symbol})")
                success &= test_visualization(symbol)
                # optionally test realtime
                # success &= test_predict_realtime(symbol)
            else:
                 print("FAILED: No symbols returned")
                 success = False
        else:
            print(f"FAILED ({r.status_code})")
            success = False
    except Exception as e:
        print(f"ERROR: {e}")
        success = False
    
    if success:
        print("\n✓ Verification Passed")
        sys.exit(0)
    else:
        print("\n✗ Verification Failed")
        sys.exit(1)
