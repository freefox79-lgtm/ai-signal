import os
import sys
from dotenv import load_dotenv

load_dotenv() # Load .env file

print("--- DEBUG GEMINI START ---")
print(f"Python Version: {sys.version}")

# 1. Check Env Var
api_key = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY: {'[PRESENT]' if api_key else '[MISSING]'}")
if api_key:
    print(f"Key Length: {len(api_key)}")
    print(f"Key Start: {api_key[:5]}...")

# 2. Check Import
print("\nAttempting to import google.generativeai...")
try:
    import google.generativeai as genai
    print("✅ Import SUCCESS")
    print(f"Version: {genai.__version__}")
except ImportError as e:
    print(f"❌ Import FAILED: {e}")
except Exception as e:
    print(f"❌ Unexpected Error during import: {e}")

print("--- DEBUG GEMINI END ---")
