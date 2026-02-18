import streamlit as st
# force deploy 2026-02-18 11:45 (Golden Ratio)
import time
from components.ui_elements import render_cyber_card
from api_connectors import APIConnectors

connectors = APIConnectors()

def show():
    # 🎯 Initialize Visibility State
    if 'show_results' not in st.session_state:
        st.session_state['show_results'] = False

    # 🎯 홈 네온 헤더
    st.markdown("""
        <style>
            /* 🚀 FINAL CONQUEST - Absolute Button Design Sync */
            div[data-testid="stMain"] button, 
            div[data-testid="stMain"] .stButton > button,
            div[data-testid="stMain"] [data-testid="stBaseButton-secondary"],
            div[data-testid="stMain"] [data-testid="stBaseButton-primary"] {
                background: transparent !important;
                background-color: transparent !important;
                background-image: none !important;
                color: #FFFFFF !important;
                font-weight: 800 !important;
                font-family: 'Orbitron', sans-serif !important;
                border: 1px solid #00FFFF !important;
                box-shadow: 0 0 15px rgba(0, 255, 255, 0.4) !important;
                transition: all 0.2s ease-in-out !important;
                text-transform: uppercase !important;
                letter-spacing: 1.5px !important;
                font-size: 0.9rem !important;
                border-radius: 4px !important;
                text-shadow: 0 0 10px #00FFFF !important;
                height: auto !important;
                padding: 8px 20px !important;
                min-height: unset !important;
            }
            div[data-testid="stMain"] button:hover {
                background-color: rgba(0, 255, 255, 0.2) !important;
                box-shadow: 0 0 25px rgba(0, 255, 255, 0.7) !important;
                transform: translateY(-1px) !important;
                border-color: #00FFFF !important;
            }
            div[data-testid="stMain"] button:active {
                transform: scale(0.97) !important;
            }
            /* Kill the Streamlit inner div background mass */
            div[data-testid="stMain"] [data-testid="stBaseButton-secondary"] > div {
                background: transparent !important;
            }
        </style>
        <div style="background: rgba(3, 199, 90, 0.05); padding: 8px 15px; border-radius: 10px; border: 1px solid var(--acc-green); margin-bottom: 12px;">
            <h3 style="color: var(--acc-green); margin: 0; text-shadow: 0 0-8px var(--acc-green); font-size: 1.8rem;">🏠 홈: 실시간 데이터 스캐너</h3>
            <p style="color: #888; margin: 2px 0 0 0; font-size: 0.95rem;">전역 데이터 소스 모니터링 및 퀀텀 분석 시스템 | 상태: 활성</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 🔍 멀티모달 검색 입력 (모바일 한 줄 배치)
    st.markdown("### 🧬 퀀텀 검색 및 분석")
    
    # Custom CSS-based horizontal row for mobile
    search_cols = st.columns([4, 1])
    with search_cols[0]:
        query = st.text_input("", placeholder="텍스트, URL 또는 시그널 지문을 입력하세요...", label_visibility="collapsed")
    with search_cols[1]:
        scan_btn = st.button("스캔 시작", key="main_search_btn", use_container_width=True)
    
    # 🎯 Callback for Closing Results
    def handle_close_results():
        st.session_state['show_results'] = False
        st.session_state.pop('last_scan', None)

    # 🚀 네온 애니메이션 / 스캔 상태 (결과 출력 위치 고정)
    if scan_btn and query:
        st.session_state['last_scan'] = query
        st.session_state['show_results'] = True
    
    if st.session_state.get('show_results', False) and 'last_scan' in st.session_state:
        query = st.session_state['last_scan']
        
        # 📊 통합 프로그레스 바 및 상태 표시
        progress_placeholder = st.empty()
        status_text = st.empty()
        
        # 📦 결과물 출력을 위한 별도 박스 (Container)
        with st.container():
            st.markdown(f"""
                <div class="scan-result-container">
                    <div class="result-header-neon">
                        <span style="font-size: 1.5rem;">🧬</span>
                        <h3 style="color: var(--neon-cyan); margin: 0; text-shadow: none;">퀀텀 스캔 및 지능형 분석 결과</h3>
                    </div>
            """, unsafe_allow_html=True)
            
            # 시뮬레이션된 프로그레스 업데이트 (UX 향상)
            for percent_complete in range(0, 101, 15):
                time.sleep(0.05)
                progress_placeholder.progress(percent_complete)
                if percent_complete < 40:
                    status_text.text("🛰️ 퀀텀 네트워크 스캔 중...")
                elif percent_complete < 80:
                    status_text.text("🧠 다차원 데이터 합성 및 분석 중...")
                else:
                    status_text.text("✅ 분석 완료")
            
            # Primary: Naver Search (via Unified)
            results = connectors.unified_search(query)
            
            if results:
                # 🦙 Local LLM Enrichment (Mac Mini Power)
                with st.spinner("🦙 로컬 AI(Llama 3)가 검색 결과(뉴스+유튜브)를 요약 중입니다..."):
                    enriched_results = connectors.enrich_search_results_with_ollama(results[:6])
                
                st.markdown(f"**[최신 시그널: {query}]**")
                for item in enriched_results:
                    st.markdown(f"""
                    <div style="margin-bottom: 5px;">
                        <a href="{item.get('link', '#')}" target="_blank" style="text-decoration: none; color: inherit;">
                            <span style="font-weight: bold; font-size: 1.05rem; color: var(--acc-blue);">{item.get('title', 'No Title')}</span>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(f"{item.get('snippet', 'No content available...')}")
            else:
                st.info("검색 결과가 없거나 MOCK 모드로 동작 중입니다.")
            
            # 💰 광고 슬롯 (현재는 비활성화됨)
            # st.markdown("""<div id="ad-slot" style="display: none; height: 100px; border: 1px dashed #444; margin: 20px 0; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #555;">광고 슬롯 (준비 중)</div>""", unsafe_allow_html=True)
            
            # 📊 합성 리포트 - [AI Signal 퀀트 분석 결과] (Gemini Integration)
            if results:
                with st.spinner("🧠 퀀텀 AI(Gemini)가 데이터를 분석 중입니다..."):
                    # Use enriched results for better context
                    analysis = connectors.fetch_gemini_analysis(query, enriched_results)
                
                st.markdown(f"""
                    <div class="glass-card" style="border-left: 4px solid var(--acc-blue); margin-top: 25px; background: rgba(0, 212, 255, 0.05);">
                        <h4 style="color: var(--acc-blue);">[AI Signal 퀀트 분석 결과] (Powered by Gemini)</h4>
                        <p style="font-size: 0.95rem; line-height: 1.6;">{analysis}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                 st.markdown(f"""
                    <div class="glass-card" style="border-left: 4px solid var(--acc-blue); margin-top: 25px; background: rgba(0, 212, 255, 0.05);">
                        <h4 style="color: var(--acc-blue);">[AI Signal 퀀트 분석 결과]</h4>
                        <p style="font-size: 0.95rem; line-height: 1.6;">분석할 데이터가 부족합니다. 검색 결과를 먼저 확보해주세요.</p>
                    </div>
                """, unsafe_allow_html=True)

            # 🛠️ "닫기" 버튼 (우측 하단)
            st.markdown('<div class="close-btn-container">', unsafe_allow_html=True)
            col_close_spacer, col_close_btn = st.columns([4, 1])
            with col_close_btn:
                # Use callback for clean state transition
                st.button("닫기", key="close_scan_results", use_container_width=True, on_click=handle_close_results)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # 🎯 AI Signal 실검 (Ranking Board)
    from datetime import datetime
    import json # Added import json here as it's used in the new code
    col_header, col_timestamp = st.columns([3, 1])
    with col_header:
        st.markdown("<h3 style='font-size: 1.8rem; margin: 0;'>🔥 AI Signal 실검 랭킹</h3>", unsafe_allow_html=True)
    with col_timestamp:
        st.markdown(f"<p style='text-align: right; color: #8e8e93; font-size: 0.95rem; margin-top: 15px;'>업데이트: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    
    try:
        # DataRouter를 통해 실시간 트렌드 로드 (Unified Engine)
        live_trends = connectors.fetch_active_realtime_trends_from_db()
        # Fallback & Top 15 Limit
        if not live_trends:
            live_trends = [{
                "keyword": "일본 무비자 여행",
                "related_insight": "네이버 검색량이 전일 대비 380% 급증하여 여행 수요 폭발 중",
                "type": "BREAKING",
                "avg_score": 98.5,
                "signal_breakdown": {"search": 95, "sns": 92, "news": 88}
            }] * 5 # Simulate some items if DB is empty for demo
        
        live_trends = live_trends[:15] # Limit to top 15
    except Exception as e:
        st.error(f"트렌드 엔진 오류: {e}")
        live_trends = []

    # Rendering the Ranking Board
    st.markdown('<div class="ranking-board">', unsafe_allow_html=True)
    
    # Row Header
    st.markdown("""
        <div class="ranking-row-header">
            <div style="text-align: center;">순위</div>
            <div>키워드</div>
            <div>선정 이유</div>
            <div>데이터 소스</div>
            <div style="text-align: right;">액션</div>
        </div>
    """, unsafe_allow_html=True)
    
    for i, item in enumerate(live_trends):
        rank = i + 1
        keyword = item.get('keyword', 'Unknown')
        insight = item.get('related_insight', 'AI가 퀀텀 시그널을 분석 중입니다...')
        if len(insight) > 60:
            insight = insight[:57] + "..."
            
        score = float(item.get('avg_score', 80))
        
        # Signal Breakdown Rendering (Graphical)
        breakdown = item.get('signal_breakdown', {})
        if isinstance(breakdown, str):
            try: breakdown = json.loads(breakdown)
            except: breakdown = {}
        
        sources_html = '<div class="source-grid">'
        if breakdown:
            icons = {'search': '🔍', 'video': '📺', 'sns': '🐦', 'community': '💬', 'finance': '💰'}
            colors = {'search': '#03c75a', 'video': '#ff0000', 'sns': '#1da1f2', 'community': '#ff4500', 'finance': '#f7931a'}
            for k, v in sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:3]:
                if v > 0:
                    icon = icons.get(k, '🔹')
                    color = colors.get(k, '#888')
                    sources_html += f'<span class="source-icon" style="border-color: {color}66;">{icon} {int(v)}</span>'
        else:
            sources_html += '<span class="source-icon">📡 System</span>'
        sources_html += '</div>'

        # Row Layout using Streamlit Columns for full interactivity
        with st.container():
            # Inject CSS Row Container Start
            st.markdown(f'<div class="ranking-row">', unsafe_allow_html=True)
            
            r_c1, r_c2, r_c3, r_c4, r_c5 = st.columns([80, 200, 300, 200, 140])
            
            with r_c1:
                st.markdown(f'<div class="rank-num">{rank}</div>', unsafe_allow_html=True)
            
            with r_c2:
                st.markdown(f'<div class="keyword-text">{keyword}</div>', unsafe_allow_html=True)
                
            with r_c3:
                st.markdown(f'<div class="reason-text">{insight}</div>', unsafe_allow_html=True)
                
            with r_c4:
                st.markdown(sources_html, unsafe_allow_html=True)
                
            with r_c5:
                if st.button("퀀텀 분석", key=f"q_scan_{i}", use_container_width=True):
                    st.session_state['last_scan'] = keyword
                    st.rerun()
            
            # Close CSS Row Container
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
