import psycopg2
import os
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(".env.local")

class StealthSessionManager:
    """
    Manages browser sessions for stealth crawling of SNS platforms.
    Handles session pooling, fingerprint spoofing, and session rotation.
    """
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not set in environment")
        
        from db_utils import get_db_connection
        self.get_db_connection = get_db_connection
    
    def get_session(self, source_name):
        """
        Get an available session from the pool for the specified source.
        
        Args:
            source_name (str): Name of the data source (e.g., 'twitter', 'instagram')
        
        Returns:
            dict: Session data with token, cookies, and fingerprint, or None if no session available
        """
        try:
            # Smart SSL detection
            if 'supabase' in self.db_url:
                conn = psycopg2.connect(self.db_url, sslmode='require')
            else:
                conn = psycopg2.connect(self.db_url)
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        cs.id,
                        cs.session_token, 
                        cs.login_cookies, 
                        cs.browser_fingerprint,
                        cs.user_agent,
                        cs.viewport_width,
                        cs.viewport_height
                    FROM crawl_sessions cs
                    JOIN data_sources ds ON cs.source_id = ds.id
                    WHERE ds.source_name = %s 
                      AND cs.status = 'IDLE'
                      AND cs.expires_at > NOW()
                      AND cs.use_count < cs.max_uses
                    ORDER BY cs.last_used_at ASC NULLS FIRST
                    LIMIT 1
                    FOR UPDATE SKIP LOCKED
                """, (source_name,))
                
                result = cur.fetchone()
                
                if result:
                    session_id, token, cookies, fingerprint, ua, vw, vh = result
                    
                    # Mark session as active and increment use count
                    cur.execute("""
                        UPDATE crawl_sessions 
                        SET status = 'ACTIVE', 
                            last_used_at = NOW(),
                            use_count = use_count + 1
                        WHERE id = %s
                    """, (session_id,))
                    
                    conn.commit()
                    
                    return {
                        'session_id': session_id,
                        'token': token,
                        'cookies': cookies,
                        'fingerprint': fingerprint,
                        'user_agent': ua,
                        'viewport': {'width': vw, 'height': vh}
                    }
                else:
                    # No available session, create a new one
                    return self.create_session(source_name)
            
            conn.close()
            
        except Exception as e:
            print(f"[StealthSessionManager] Error getting session: {e}")
            return None
    
    def release_session(self, session_id):
        """
        Release a session back to the pool (mark as IDLE).
        
        Args:
            session_id (int): ID of the session to release
        """
        try:
            if 'supabase' in self.db_url:
                conn = psycopg2.connect(self.db_url, sslmode='require')
            else:
                conn = psycopg2.connect(self.db_url)
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE crawl_sessions 
                    SET status = 'IDLE'
                    WHERE id = %s
                """, (session_id,))
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            print(f"[StealthSessionManager] Error releasing session: {e}")
    
    def create_session(self, source_name):
        """
        Create a new session with randomized fingerprint.
        
        Args:
            source_name (str): Name of the data source
        
        Returns:
            dict: Newly created session data
        """
        try:
            if 'supabase' in self.db_url:
                conn = psycopg2.connect(self.db_url, sslmode='require')
            else:
                conn = psycopg2.connect(self.db_url)
            
            # Generate random fingerprint
            fingerprint = self.create_fingerprint()
            session_token = self._generate_token()
            
            with conn.cursor() as cur:
                # Get source_id
                cur.execute("SELECT id FROM data_sources WHERE source_name = %s", (source_name,))
                source_result = cur.fetchone()
                
                if not source_result:
                    print(f"[StealthSessionManager] Source '{source_name}' not found")
                    return None
                
                source_id = source_result[0]
                
                # Insert new session
                cur.execute("""
                    INSERT INTO crawl_sessions (
                        source_id, session_token, browser_fingerprint,
                        user_agent, viewport_width, viewport_height,
                        timezone, language, status, expires_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE', NOW() + INTERVAL '24 hours')
                    RETURNING id
                """, (
                    source_id,
                    session_token,
                    json.dumps(fingerprint),
                    fingerprint['user_agent'],
                    fingerprint['viewport_width'],
                    fingerprint['viewport_height'],
                    fingerprint['timezone'],
                    fingerprint['language']
                ))
                
                session_id = cur.fetchone()[0]
                conn.commit()
            
            conn.close()
            
            return {
                'session_id': session_id,
                'token': session_token,
                'cookies': None,
                'fingerprint': fingerprint,
                'user_agent': fingerprint['user_agent'],
                'viewport': {
                    'width': fingerprint['viewport_width'],
                    'height': fingerprint['viewport_height']
                }
            }
            
        except Exception as e:
            print(f"[StealthSessionManager] Error creating session: {e}")
            return None
    
    def rotate_session(self, session_id):
        """
        Mark session as expired and create a new one.
        
        Args:
            session_id (int): ID of the session to rotate
        """
        try:
            if 'supabase' in self.db_url:
                conn = psycopg2.connect(self.db_url, sslmode='require')
            else:
                conn = psycopg2.connect(self.db_url)
            
            with conn.cursor() as cur:
                # Get source_name from the session
                cur.execute("""
                    SELECT ds.source_name 
                    FROM crawl_sessions cs
                    JOIN data_sources ds ON cs.source_id = ds.id
                    WHERE cs.id = %s
                """, (session_id,))
                
                result = cur.fetchone()
                if not result:
                    return None
                
                source_name = result[0]
                
                # Mark old session as expired
                cur.execute("""
                    UPDATE crawl_sessions 
                    SET status = 'EXPIRED'
                    WHERE id = %s
                """, (session_id,))
                
                conn.commit()
            
            conn.close()
            
            # Create new session
            return self.create_session(source_name)
            
        except Exception as e:
            print(f"[StealthSessionManager] Error rotating session: {e}")
            return None
    
    def create_fingerprint(self):
        """
        Generate randomized browser fingerprint to avoid detection.
        
        Returns:
            dict: Randomized fingerprint data
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        viewports = [
            (1920, 1080),
            (1366, 768),
            (1440, 900),
            (1536, 864),
            (1280, 720)
        ]
        
        timezones = [
            "Asia/Seoul",
            "America/New_York",
            "Europe/London",
            "Asia/Tokyo",
            "America/Los_Angeles"
        ]
        
        languages = ["ko-KR", "en-US", "ja-JP", "en-GB"]
        
        viewport = random.choice(viewports)
        
        return {
            "user_agent": random.choice(user_agents),
            "viewport_width": viewport[0],
            "viewport_height": viewport[1],
            "timezone": random.choice(timezones),
            "language": random.choice(languages),
            "webgl_vendor": random.choice(["Intel Inc.", "NVIDIA Corporation", "AMD"]),
            "webgl_renderer": random.choice(["Intel Iris OpenGL Engine", "NVIDIA GeForce GTX", "AMD Radeon"]),
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            "hardware_concurrency": random.choice([4, 8, 12, 16]),
            "device_memory": random.choice([4, 8, 16, 32])
        }
    
    def _generate_token(self):
        """Generate a unique session token"""
        import hashlib
        import time
        
        data = f"{time.time()}{random.random()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def cleanup_expired_sessions(self):
        """
        Clean up expired sessions from the database.
        Should be run periodically (e.g., via cron job).
        """
        try:
            if 'supabase' in self.db_url:
                conn = psycopg2.connect(self.db_url, sslmode='require')
            else:
                conn = psycopg2.connect(self.db_url)
            
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM crawl_sessions 
                    WHERE expires_at < NOW() OR status = 'EXPIRED'
                """)
                deleted_count = cur.rowcount
                conn.commit()
            
            conn.close()
            
            print(f"[StealthSessionManager] Cleaned up {deleted_count} expired sessions")
            return deleted_count
            
        except Exception as e:
            print(f"[StealthSessionManager] Error cleaning up sessions: {e}")
            return 0
