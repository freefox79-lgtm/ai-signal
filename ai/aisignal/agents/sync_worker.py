import os
import psycopg2
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(".env.local")

# DB Connections
LOCAL_DB_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class SyncWorker:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL != "your_supabase_url_here" else None
        self.conn = psycopg2.connect(LOCAL_DB_URL)

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
