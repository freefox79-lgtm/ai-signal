#!/usr/bin/env python3
"""
시장 데이터 수집 스크립트
n8n 워크플로우에서 호출됨
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from agents.jwem.market_analyzer import JwemMarketAnalyzer

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting market data collection...")
    
    try:
        jwem = JwemMarketAnalyzer()
        
        # 시장 지수 수집
        indices = jwem._analyze_major_indices()
        
        print(f"✅ Collected {len(indices)} market indices")
        for key, value in indices.items():
            print(f"  - {key}: {value['value']} ({value['change']})")
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Market data collection completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Error collecting market data: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
