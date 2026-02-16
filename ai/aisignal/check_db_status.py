import os
import psycopg2
from data_router import router
from dotenv import load_dotenv

load_dotenv(".env.local")

def check_db():
    print("Checking intel_persona_reports...")
    try:
        res = router.execute_query("SELECT count(*) FROM intel_persona_reports", table_hint='intel_persona_reports')
        print(f"intel_persona_reports count: {res[0][0]}")
    except Exception as e:
        print(f"Error checking intel_persona_reports: {e}")

    print("Checking intel_synthetic_spatial...")
    try:
        res = router.execute_query("SELECT count(*) FROM intel_synthetic_spatial", table_hint='intel_synthetic_spatial')
        print(f"intel_synthetic_spatial count: {res[0][0]}")
        if res[0][0] > 0:
            details = router.execute_query("SELECT district_name, combined_insight FROM intel_synthetic_spatial LIMIT 1", table_hint='intel_synthetic_spatial')
            print(f"Sample data: {details}")
    except Exception as e:
        print(f"Error checking intel_synthetic_spatial: {e}")

if __name__ == "__main__":
    check_db()
