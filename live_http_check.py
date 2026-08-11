import json
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

def test_live_server():
    print(f"Connecting to live server at {BASE_URL}...")
    
    # Check Docs
    with urllib.request.urlopen(f"{BASE_URL}/docs") as response:
        print(f"[LIVE HTTP] GET /docs -> Status: {response.status}")
        assert response.status == 200
    
    # Check OpenAPI
    with urllib.request.urlopen(f"{BASE_URL}/openapi.json") as response:
        data = json.loads(response.read().decode())
        print(f"[LIVE HTTP] GET /openapi.json -> Status: {response.status}, Endpoints count: {len(data['paths'])}")
        assert response.status == 200
    
    print("\nLive server is responding cleanly to real HTTP socket connections!")

if __name__ == "__main__":
    test_live_server()
