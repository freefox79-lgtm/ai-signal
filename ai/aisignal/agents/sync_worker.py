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

    def pull_feedback_from_supabase(self):
        """Fetches user feedback from Supabase to Local for AI learning."""
        if not self.supabase:
            return
            
        try:
            response = self.supabase.table("briefing_feedback").select("*").order("created_at", descending=True).limit(20).execute()
            feedback_items = response.data
            
            if not feedback_items:
                return

            with self.conn.cursor() as cur:
                for item in feedback_items:
                    cur.execute("""
                        INSERT INTO briefing_feedback (id, briefing_id, rating, comment, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, (item['id'], item['briefing_id'], item['rating'], item['comment'], item['created_at']))
            self.conn.commit()
            print(f"[SYNC] Pulled {len(feedback_items)} feedback items from Supabase.")
        except Exception as e:
            print(f"[SYNC] Error pulling feedback: {e}")

    def sync_to_supabase(self):
        """Processes and pushes refined data to Supabase."""
        if not self.supabase:
            print("[SYNC] Supabase credentials not set. Skipping.")
            return

        # 1. Push Local Signals to Supabase
        raw_signals = self.fetch_local_signals()
        if raw_signals:
            for sig in raw_signals:
                data = {
                    "category": sig[1],
                    "keyword": sig[2],
                    "insight": sig[3],
                    "agent": sig[4]
                }
                try:
                    self.supabase.table("signals").insert(data).execute()
                    with self.conn.cursor() as cur:
                        cur.execute("UPDATE signals SET synced = True WHERE id = %s", (sig[0],))
                    self.conn.commit()
                except Exception as e:
                    print(f"[SYNC] Error syncing signal {sig[0]}: {e}")
        
        # 2. Pull Feedback from Supabase
        self.pull_feedback_from_supabase()

if __name__ == "__main__":
    worker = SyncWorker()
    worker.sync_to_supabase()
