import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load tiered env
load_dotenv(".env.local")

from api_connectors import APIConnectors

def test_real_data():
    print("🚀 Starting Real Public Data Test")
    connectors = APIConnectors(mode="REAL")
    
    # 1. Test APT Transactions (Gangnam-gu: 11680, Oct 2025 for stability)
    print("\n🏠 Testing APT Transactions (Gangnam, Oct 2025)...")
    apt_data = connectors.fetch_apt_transactions(lawd_cd="11680", deal_ymd="202510")
    if apt_data:
        print("✅ APT Fetch SUCCESS!")
        # Basic check of the structure (XML converted to dict usually)
        print(f"   Data snippet: {str(apt_data)[:300]}...")
    else:
        print("❌ APT Fetch FAILED (No data or Auth error).")

    # 2. Test Shopping District (Gangnam-gu area)
    print("\n🏙️ Testing Shopping District (Gangnam)...")
    shop_data = connectors.fetch_shopping_district(div_id="11680")
    if shop_data:
        print("✅ Shopping District SUCCESS!")
        # Check for items
        items = shop_data.get('body', {}).get('items', [])
        print(f"   Found {len(items)} district entries.")
        if items:
            print(f"   Example: {items[0].get('trarNm', 'Unknown Zone')}")
    else:
        print("❌ Shopping District FAILED (No data or Auth error).")

if __name__ == "__main__":
    test_real_data()

