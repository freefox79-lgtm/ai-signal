import sys
import os
from datetime import datetime, timedelta

# Add root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from data_router import router

def populate_wiki():
    print("🚀 Populating Wiki Origin Data...")
    
    # Mock Data for "Deepfake" visualization
    # schema: id, source, target, type, confidence, timestamp, metadata
    
    base_time = datetime.now()
    
    data = [
        ("User_X89", "Web_DarkForum", "uploaded_to", 0.9, base_time - timedelta(hours=48)),
        ("Web_DarkForum", "User_Alpha", "shared_with", 0.8, base_time - timedelta(hours=47)),
        ("Web_DarkForum", "User_Beta", "shared_with", 0.8, base_time - timedelta(hours=46)),
        ("User_Alpha", "Social_Twitter", "posted_on", 0.95, base_time - timedelta(hours=40)),
        ("User_Beta", "Social_Telegram", "posted_on", 0.95, base_time - timedelta(hours=39)),
        ("Social_Twitter", "Influencer_J", "retweeted_by", 0.6, base_time - timedelta(hours=35)),
        ("Social_Telegram", "Community_Crypto", "forwarded_to", 0.7, base_time - timedelta(hours=34)),
        ("Influencer_J", "Media_DailyTech", "covered_by", 0.85, base_time - timedelta(hours=10)),
        ("Community_Crypto", "Media_DailyTech", "cited_by", 0.5, base_time - timedelta(hours=9)),
    ]
    
    success_count = 0
    
    for source, target, rel_type, conf, ts in data:
        try:
            # Metadata as JSON string
            meta = '{"credibility": ' + str(int(conf*100)) + '}'
            
            router.execute_query(
                """
                INSERT INTO origin_tracking (source, target, relation_type, confidence, timestamp, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (source, target, rel_type, conf, ts, meta),
                table_hint='origin_tracking'
            )
            success_count += 1
        except Exception as e:
            print(f"Error inserting {source}->{target}: {e}")
            
    print(f"✅ Wiki Data Populated: {success_count} edges.")

if __name__ == "__main__":
    populate_wiki()
