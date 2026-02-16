import os
import psycopg2
from dotenv import load_dotenv

# Load env
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
else:
    load_dotenv(".env.production")

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    print(f"🚀 Running migration on {DATABASE_URL.split('@')[-1] if DATABASE_URL else 'NONE'}...")
    if not DATABASE_URL:
        print("❌ DATABASE_URL is not set.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 1. intel_persona_reports
        print("Creating table: intel_persona_reports...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS intel_persona_reports (
                report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                agent VARCHAR(50) NOT NULL,
                category VARCHAR(50),
                title TEXT,
                content TEXT,
                source_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. intel_synthetic_spatial
        print("Creating table: intel_synthetic_spatial...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS intel_synthetic_spatial (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                district_name TEXT,
                apt_data JSONB,
                commercial_data JSONB,
                combined_insight TEXT,
                linked_report_id UUID REFERENCES intel_persona_reports(report_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Migration completed successfully.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate()
