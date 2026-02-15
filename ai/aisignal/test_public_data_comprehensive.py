import requests
import urllib.parse
import json

def test_variation(name, endpoint, key):
    # Data.go.kr often fails if the serviceKey is double-encoded or not encoded when needed.
    # We test 3 variations:
    # 1. Raw appending (unquoted)
    # 2. urllib.parse.quote
    # 3. urllib.parse.unquote (if it was already partially encoded)
    
    variations = {
        "Raw (Unquoted)": key,
        "URL Encoded (Quote)": urllib.parse.quote(key),
        "URL Decoded (Unquote)": urllib.parse.unquote(key)
    }
    
    print(f"\n--- Testing Endpoint: {endpoint} ---")
    print(f"--- Key Base: {key[:8]}...{key[-8:]} ---")
    
    for v_name, v_key in variations.items():
        # Construct URL with raw append to avoid 'requests' doing any auto-encoding if possible
        full_url = f"{endpoint}?key=573&_type=json&serviceKey={v_key}"
        
        try:
            # We don't pass params here to ensure the URL remains EXACTLY as constructed
            response = requests.get(full_url, timeout=10)
            status = response.status_code
            text = response.text[:200].replace("\n", " ")
            
            result_mark = "✅" if status == 200 else "❌"
            print(f"[{result_mark}] {v_name}: Status {status} | Response: {text}")
            
        except Exception as e:
            print(f"[💥] {v_name}: Exception: {e}")

def run_comprehensive_test():
    keys = [
        "b630afb87c22ad39d655d3f8c4c389e204d6fe5129bf165f1601bc0b32386e99",
        "c04280dda4d3271cc7b3f6fe0f991db2a2808832f8aae93b38df2c2d5c20a2f2"
    ]
    
    endpoints = [
        "https://apis.data.go.kr/B553077/api/open/sdsc2/storeZoneOne",
        "http://apis.data.go.kr/B553077/api/open/sdsc2/storeZoneOne"
    ]
    
    print("🔬 Data.go.kr Exhaustive Key Test Running...")
    
    for key in keys:
        for endpoint in endpoints:
            test_variation("Test", endpoint, key)

if __name__ == "__main__":
    run_comprehensive_test()
