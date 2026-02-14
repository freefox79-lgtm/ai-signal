#!/usr/bin/env python3
"""
커뮤니티 트렌드 수집 스크립트 (5개 커뮤니티)
n8n 워크플로우에서 호출됨
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from agents.jfit.trend_hunter import JfitTrendHunter

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting community trend collection...")
    
    try:
        jfit = JfitTrendHunter()
        
        # 커뮤니티 트렌드 수집
        community_trends = jfit._call_stealth_crawler('community', 'trending')
        
        print(f"✅ Collected {len(community_trends)} community trends")
        for trend in community_trends:
            print(f"  - {trend['platform']}: {trend['content'][:50]}...")
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Community trend collection completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Error collecting community trends: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
