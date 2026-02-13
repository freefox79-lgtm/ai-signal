import os
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

# Supabase / Postgres connection
DB_URL = os.getenv("DATABASE_URL")

def update_mcp_status():
    """
    Checks if MCP server build files exist and updates the database.
    In a real scenario, this would also check process health.
    """
    config_path = "mcp-config.json"
    if not os.path.exists(config_path):
        print(f"[ERROR] {config_path} not found.")
        return

    with open(config_path, "r") as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})
    
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        for name, details in servers.items():
            # Check if the build file exists
            index_path = details.get("args", [None])[0]
            status = "RUNNING" if index_path and os.path.exists(index_path) else "DOWN"
            
            print(f"[MCP] {name}: {status} (Path: {index_path})")
            
            # Update database
            cur.execute("""
                INSERT INTO mcp_status (server_name, status, last_health_check, config_data)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (server_name) DO UPDATE 
                SET status = EXCLUDED.status, 
                    last_health_check = EXCLUDED.last_health_check,
                    config_data = EXCLUDED.config_data;
            """, (name, status, datetime.now(), json.dumps(details)))
            
        conn.commit()
        cur.close()
        conn.close()
        print("[SUCCESS] MCP status updated in database.")
        
    except Exception as e:
        print(f"[ERROR] Database update failed: {e}")

if __name__ == "__main__":
    update_mcp_status()
