import os
import sys
# Add parent dir to path to find modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dotenv to prevent overwriting env vars passed from CLI
import dotenv
def mock_load_dotenv(*args, **kwargs):
    pass
dotenv.load_dotenv = mock_load_dotenv

from scripts.trend_collector import collect_and_analyze_trends

if __name__ == "__main__":
    print("🚀 Running single collection cycle...")
    try:
        collect_and_analyze_trends()
        print("✅ Done.")
    except Exception as e:
        print(f"❌ Error: {e}")
