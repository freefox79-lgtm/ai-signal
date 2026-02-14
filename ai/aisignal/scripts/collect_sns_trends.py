#!/usr/bin/env python3
"""
SNS 트렌드 수집 스크립트 (X, Instagram)
n8n 워크플로우에서 호출됨
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from agents.jfit.trend_hunter import JfitTrendHunter

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting SNS trend collection...")
    
    try:
        jfit = JfitTrendHunter()
        
        # SNS 트렌드 수집 (X + Instagram)
        x_trends = jfit._call_stealth_crawler('x', 'trending')
        insta_trends = jfit._call_stealth_crawler('instagram', 'trending')
        
        total = len(x_trends) + len(insta_trends)
        print(f"✅ Collected {total} SNS trends")
        print(f"  - X: {len(x_trends)} trends")
        print(f"  - Instagram: {len(insta_trends)} trends")
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SNS trend collection completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Error collecting SNS trends: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
