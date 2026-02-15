import os
import json
from api_connectors import APIConnectors
from dotenv import load_dotenv

load_dotenv(".env.local")

def test_fred_integration():
    print("🚀 FRED API Verification Start")
    
    # 1. Initialize connector (FORCE REAL mode for test)
    connectors = APIConnectors(mode="REAL")
    
    # 2. Test common series
    # GS10: 10-Year Treasury Constant Maturity Rate
    # UNRATE: Unemployment Rate
    series_to_test = ["GS10", "UNRATE"]
    
    for series in series_to_test:
        print(f"\n📡 Fetching series: {series}...")
        try:
            data = connectors.fetch_fred_series(series)
            if data and "observations" in data:
                latest = data["observations"][0]
                print(f"✅ Success! Latest {series} value: {latest['value']} (Date: {latest['date']})")
            else:
                print(f"❌ Failed to fetch {series}. Response: {json.dumps(data)}")
        except Exception as e:
            print(f"💥 Exception during fetch: {e}")

if __name__ == "__main__":
    test_fred_integration()
