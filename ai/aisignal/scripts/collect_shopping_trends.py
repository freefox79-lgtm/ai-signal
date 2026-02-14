#!/usr/bin/env python3
"""
쇼핑 트렌드 수집 스크립트 (Hypebeast, Kream)
n8n 워크플로우에서 호출됨
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from agents.jfit.trend_hunter import JfitTrendHunter

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting shopping trend collection...")
    
    try:
        jfit = JfitTrendHunter()
        
        # 쇼핑 트렌드 수집
        shopping_trends = jfit._call_stealth_crawler('shopping', 'trending')
        
        print(f"✅ Collected {len(shopping_trends)} shopping trends")
        for trend in shopping_trends:
            print(f"  - {trend['platform']}: {trend['content'][:50]}...")
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Shopping trend collection completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Error collecting shopping trends: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
