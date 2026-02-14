#!/usr/bin/env python3
"""
경제 지표 데이터 수집 스크립트
n8n 워크플로우에서 호출됨
"""
import sys
import os
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from agents.jwem.market_analyzer import JwemMarketAnalyzer

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting economic data collection...")
    
    try:
        jwem = JwemMarketAnalyzer()
        
        # 경제 지표 수집
        indicators = jwem._analyze_economic_indicators()
        
        print(f"✅ Collected {len(indicators)} economic indicators")
        for key, value in indicators.items():
            source = value.get('source', 'FRED')
            print(f"  - {key}: {value['value']} ({source})")
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Economic data collection completed successfully")
        return 0
        
    except Exception as e:
        print(f"❌ Error collecting economic data: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
