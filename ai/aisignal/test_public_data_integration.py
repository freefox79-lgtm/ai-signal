import os
import requests
from urllib.parse import unquote, quote
from dotenv import load_dotenv

load_dotenv(".env.local")

def test_public_api_logic():
    endpoint = "http://apis.data.go.kr/B553077/api/open/sdsc2/storeZoneOne"
    service_key = os.getenv("DATA_GO_KR_KEY")
    
    if not service_key:
        print("❌ Error: DATA_GO_KR_KEY not found in .env.local")
        return

    print(f"🚀 Key: {service_key[:10]}...")

    # Case 1: Standard requests (will URL-encode the key)
    # This works if the key in ENV is the "Decoding" version.
    print(f"\n--- Attempt 1: Standard requests.get (Automated Encoding) ---")
    params = {"key": "573", "serviceKey": service_key, "_type": "json"}
    try:
        r1 = requests.get(endpoint, params=params, timeout=10)
        print(f"📡 Status: {r1.status_code}")
        if r1.status_code == 200 and "Unauthorized" not in r1.text:
            print("✅ Success with Case 1!")
            print(f"Data Sample: {r1.text[:200]}...")
        else:
            print(f"❌ Failed: {r1.text[:100]}")
    except Exception as e:
        print(f"⚠️ Exception: {e}")

    # Case 2: Manual URL Construction (Using key AS-IS)
    # This works if the key in ENV is the "Encoding" version. 
    # requests.get(url, params=...) will double-encode if it sees % in the key.
    print(f"\n--- Attempt 2: Manual URL Construction (Raw Service Key) ---")
    params_str = f"key=573&_type=json&serviceKey={service_key}"
    full_url = f"{endpoint}?{params_str}"
    try:
        r2 = requests.get(full_url, timeout=10)
        print(f"📡 Status: {r2.status_code}")
        if r2.status_code == 200 and "Unauthorized" not in r2.text:
            print("✅ Success with Case 2!")
            print(f"Data Sample: {r2.text[:200]}...")
        else:
            print(f"❌ Failed: {r2.text[:100]}")
    except Exception as e:
        print(f"⚠️ Exception: {e}")

    # Case 3: URL-Decoded + Standard requests
    # If the user provided the "Encoding" key, and we want requests to encode it once.
    print(f"\n--- Attempt 3: unquote(key) + Standard requests.get ---")
    decoded_key = unquote(service_key)
    params = {"key": "573", "serviceKey": decoded_key, "_type": "json"}
    try:
        r3 = requests.get(endpoint, params=params, timeout=10)
        print(f"📡 Status: {r3.status_code}")
        if r3.status_code == 200 and "Unauthorized" not in r3.text:
            print("✅ Success with Case 3!")
            print(f"Data Sample: {r3.text[:200]}...")
        else:
            print(f"❌ Failed: {r3.text[:100]}")
    except Exception as e:
        print(f"⚠️ Exception: {e}")

if __name__ == "__main__":
    test_public_api_logic()
