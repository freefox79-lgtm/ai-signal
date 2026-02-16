import os
import sys
import psycopg2
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

# 중앙 집중식 DB 유틸리티 임포트
from db_utils import get_db_connection

load_dotenv(".env.local")

# DB Connections
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class SyncWorker:
    def __init__(self, local_db_url=None):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL != "your_supabase_url_here" else None
        # DataRouter를 통해 로컬 DB 연결 (MACMINI 라우트 사용)
        from data_router import router
        self.conn = router.get_connection(table_name='raw_feeds') # Forces Mac Mini connection

    def fetch_local_signals(self):
        """Fetches raw signals from local PG that haven't been synced."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, category, keyword, insight, agent FROM signals WHERE synced = False")
            return cur.fetchall()

    def sync_to_supabase(self):
        """Processes and pushes refined data to Supabase."""
        if not self.supabase:
            print("[SYNC] Supabase credentials not set. Skipping.")
            return

        raw_signals = self.fetch_local_signals()
        if not raw_signals:
            print("[SYNC] No new signals to sync.")
            return

        for sig in raw_signals:
            # Sync only refined 'insight' to cloud
            data = {
                "category": sig[1],
                "keyword": sig[2],
                "insight": sig[3],
                "agent": sig[4]
            }
            try:
                self.supabase.table("signals").insert(data).execute()
                # Mark as synced locally
                with self.conn.cursor() as cur:
                    cur.execute("UPDATE signals SET synced = True WHERE id = %s", (sig[0],))
                self.conn.commit()
                print(f"[SYNC] Synced signal {sig[0]} to Supabase.")
            except Exception as e:
                print(f"[SYNC] Error syncing {sig[0]}: {e}")

if __name__ == "__main__":
    worker = SyncWorker()
    worker.sync_to_supabase()
