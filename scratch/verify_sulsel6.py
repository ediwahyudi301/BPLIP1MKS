import requests
import json

def test_api():
    base_url = "http://127.0.0.1:5000"
    
    # Test Realisasi for sulsel_6
    print("Testing Realisasi API for sulsel_6...")
    try:
        resp = requests.get(f"{base_url}/realisasi?paket=sulsel_6&minggu=1")
        if resp.status_code == 200:
            print("Successfully accessed Realisasi page")
        else:
            print(f"Failed to access Realisasi page: {resp.status_code}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

    # Test Kurva S API for sulsel_6
    print("\nTesting Kurva S API for sulsel_6...")
    try:
        resp = requests.get(f"{base_url}/api/kurva_s/sulsel_6")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Labels: {data.get('labels')[:5]}...")
            print(f"Target: {data.get('target')[:5]}...")
            print(f"Realized: {data.get('realized')[:5]}...")
            if data.get('target'):
                print("Data parsing successful!")
            else:
                print("Warning: No target data found.")
        else:
            print(f"Failed to access Kurva S API: {resp.status_code}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    test_api()
