import streamlit as st
# force deploy 2026-02-18 11:45 (Golden Ratio)
import time
from components.ui_elements import render_cyber_card
from api_connectors import APIConnectors

connectors = APIConnectors()

def show():
    # 🚨 RELOAD CONFIRMED - UI Version 5.5 (SYMMETRIC MOBILE CARDS)
    st.markdown('<div style="display:none">REL_FINAL_SYNC_V5_5</div>', unsafe_allow_html=True)

    # 🎯 HARD CONNECTIVITY SYNC (Must happen before widgets are instantiated)
    if 'pending_scan_keyword' in st.session_state:
        st.session_state['main_query_input'] = st.session_state['pending_scan_keyword']
        st.session_state['last_scan'] = st.session_state['pending_scan_keyword']
        st.session_state['show_results'] = True
        del st.session_state['pending_scan_keyword']

    # 🎯 Initialize Visibility State
    if 'show_results' not in st.session_state:
        st.session_state['show_results'] = False
    if 'last_scan' not in st.session_state:
        st.session_state['last_scan'] = ""

    # 💉 DEFINITIVE UI OVERRIDE (Injected for Reliability)
    st.markdown("""
        <style>
            /* 🖥️ Desktop Grid Layout */
            @media (min-width: 769px) {
                .ranking-row-header {
                    display: grid !important;
                    grid-template-columns: 80px 200px 1fr 200px 160px !important;
                    gap: 15px !important;
                    align-items: center !important;
                    padding: 12px 20px !important;
                    border-bottom: 2px solid rgba(0, 255, 249, 0.3) !important;
                }
                .ranking-row {
                    display: grid !important;
                    grid-template-columns: 80px 200px 1fr 200px 160px !important;
                    gap: 15px !important;
                    align-items: center !important;
                    padding: 15px 20px !important;
                    min-height: 80px !important;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
                }
                .col-rank, .col-keyword, .col-reason, .col-source, .col-action {
                    display: block !important;
                    text-align: left !important;
                }
                .col-rank { text-align: center !important; }
                
                /* Action Button Sync - Adjusting for Streamlit wrapper */
                .action-btn-wrapper {
                    position: absolute !important;
                    right: 20px !important;
                    width: 140px !important;
                    z-index: 100 !important;
                    margin-top: -62px !important; /* Finely tuned for middle alignment */
                }
            }
            
            /* 📱 Mobile Card Layout (Strict Vertical Symmetry & Impact) */
            @media (max-width: 768px) {
                .ranking-row-header { display: none !important; }
                .ranking-row {
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: center !important;
                    justify-content: center !important;
                    padding: 30px 15px 15px 15px !important;
                    margin-bottom: 0 !important;
                    background: rgba(15, 20, 40, 0.8) !important;
                    backdrop-filter: blur(15px) !important;
                    border: 1px solid rgba(0, 255, 249, 0.45) !important;
                    border-bottom: none !important;
                    border-top-left-radius: 30px !important;
                    border-top-right-radius: 30px !important;
                    text-align: center !important;
                    width: 100% !important;
                }
                
                /* Rank Number - Maximal Centralized Presence */
                .col-rank { 
                    width: 100% !important; 
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    margin-bottom: 5px !important;
                }
                .rank-num { 
                    font-size: 5rem !important; 
                    color: var(--neon-cyan) !important; 
                    font-weight: 1000 !important;
                    text-shadow: 0 0 40px rgba(0, 255, 249, 0.9) !important;
                    line-height: 1 !important;
                    display: block !important;
                    text-align: center !important;
                }

                /* Keyword - Centered Stylish Link */
                .col-keyword { 
                    width: 100% !important; 
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    margin-bottom: 25px !important;
                    margin-top: -10px !important;
                }
                .keyword-text { 
                    font-size: 1.8rem !important; 
                    color: white !important; 
                    font-weight: 900 !important;
                    text-align: center !important;
                    display: inline-block !important;
                    border-bottom: 2px solid transparent !important;
                    transition: all 0.3s ease !important;
                    padding-bottom: 2px !important;
                }
                .keyword-link {
                    text-decoration: none !important;
                    display: flex !important;
                    justify-content: center !important;
                    width: auto !important;
                }
                .keyword-link:hover .keyword-text {
                    color: var(--neon-cyan) !important;
                    border-bottom-color: var(--neon-cyan) !important;
                    text-shadow: 0 0 15px rgba(0, 255, 249, 0.6) !important;
                }
                
                /* Analysis Box - Filling the Space (85-90% Width) */
                .col-reason {
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    width: 100% !important;
                    margin-bottom: 30px !important;
                }
                .reason-text {
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    width: 90% !important; /* Maximized presence as requested */
                    background: rgba(0, 255, 249, 0.08) !important;
                    border: 1px solid rgba(0, 255, 249, 0.3) !important;
                    border-left: 6px solid var(--neon-cyan) !important;
                    padding: 18px 25px !important; /* Voluminous padding */
                    border-radius: 15px !important;
                    font-size: 1.05rem !important;
                    color: #FFFFFF !important;
                    line-height: 1.6 !important;
                    text-align: center !important;
                    min-height: 80px !important;
                    box-shadow: inset 0 0 20px rgba(0, 255, 249, 0.05) !important;
                }

                /* Metrics - Centralized Horizontal Metrics */
                .col-source {
                    width: 100% !important;
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    margin-bottom: 25px !important;
                }
                .source-grid {
                    display: flex !important;
                    flex-direction: row !important;
                    justify-content: center !important;
                    align-items: center !important;
                    gap: 25px !important;
                }
                .source-icon {
                    font-size: 1rem !important;
                    padding: 6px 12px !important;
                    background: rgba(255, 255, 255, 0.05) !important;
                    border-radius: 20px !important;
                    border: 1px solid rgba(255, 255, 255, 0.1) !important;
                }

                /* Action Button Wrapper Merged (Unified Bottom) */
                .action-btn-wrapper {
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    width: 100% !important;
                    margin-top: 0 !important;
                    margin-bottom: 60px !important;
                    padding: 0 30px 30px 30px !important;
                    background: rgba(15, 20, 40, 0.8) !important;
                    backdrop-filter: blur(15px) !important;
                    border: 1px solid rgba(0, 255, 249, 0.45) !important;
                    border-top: none !important;
                    border-bottom-left-radius: 30px !important;
                    border-bottom-right-radius: 30px !important;
                    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8) !important;
                }
            }

                /* Metrics - Bottom Horizontal Centered */
                .col-source {
                    width: 100% !important;
                    display: flex !important;
                    justify-content: center !important;
                    margin-bottom: 15px !important;
                }
                .source-grid {
                    display: flex !important;
                    flex-direction: row !important;
                    justify-content: center !important;
                    gap: 15px !important;
                }

                /* Action Button Wrapper Merged */
                .action-btn-wrapper {
                    display: flex !important;
                    justify-content: center !important;
                    width: 100% !important;
                    margin-top: 0 !important;
                    margin-bottom: 45px !important;
                    padding: 0 25px 25px 25px !important;
                    background: rgba(15, 20, 40, 0.75) !important;
                    backdrop-filter: blur(15px) !important;
                    border: 1px solid rgba(0, 255, 249, 0.4) !important;
                    border-top: none !important;
                    border-bottom-left-radius: 25px !important;
                    border-bottom-right-radius: 25px !important;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7) !important;
                }
            }
            
            /* 🔗 Keyword Hyperlink Style */
            .keyword-link {
                text-decoration: none !important;
                color: inherit !important;
                transition: all 0.3s ease !important;
            }
            .keyword-link:hover .keyword-text {
                color: var(--neon-cyan) !important;
                text-shadow: 0 0 15px rgba(0, 255, 249, 0.8) !important;
                text-decoration: underline !important;
            }

            /* 👑 Neon Title Style (Unified) */
            .neon-title {
                display: flex !important;
                align-items: center !important;
                gap: 12px !important;
                font-family: 'Orbitron', sans-serif !important;
                font-size: 1.85rem !important;
                font-weight: 900 !important;
                color: #FFFFFF !important;
                text-shadow: 0 0 10px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.4) !important;
                margin-bottom: 20px !important;
                visibility: visible !important;
                opacity: 1 !important;
            }

            /* 🔬 Scan Result UI Polish */
            .scan-result-title {
                font-size: 1.5rem !important;
                font-weight: 800 !important;
                color: var(--neon-cyan) !important;
                margin: 0 !important;
                display: block !important;
                visibility: visible !important;
            }
        </style>
    """, unsafe_allow_html=True)

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
        <div class="tab-intro-card">
            <h2 class="intro-title">🏠 홈: 실시간 데이터 스캐너</h2>
            <p class="intro-desc">전역 데이터 소스 모니터링 및 퀀텀 분석 시스템 | 상태: 활성</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 🧬 Restoration: Quantum Search Title (Unified Style)
    st.markdown("""
        <div class="quantum-title-container" style="margin: 0px 0 15px 0 !important;">
            <div class="neon-title">
                <span>🧬</span>
                <span>퀀텀 검색 및 분석</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Custom CSS-based horizontal row for mobile
    search_cols = st.columns([4, 1])
    with search_cols[0]:
        # Connect text_input to st.session_state for connectivity
        # Using a unique key to ensure state persists and forces update
        query = st.text_input("", 
                              value=st.session_state.get('last_scan', ""),
                              placeholder="텍스트, URL 또는 시그널 지문을 입력하세요...", 
                              label_visibility="collapsed",
                              key="main_query_input")
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
                        <div class="scan-result-title">퀀텀 스캔 및 지능형 분석 결과</div>
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
        # 👑 RESTORED TITLE - Using unique class to bypass global hiding
        st.markdown('<div class="neon-title">🔥 AI Signal 실검 랭킹</div>', unsafe_allow_html=True)
    with col_timestamp:
        st.markdown(f"<p style='text-align: right; color: #8e8e93; font-size: 0.95rem; margin-top: 15px;'>업데이트: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    
    def interpret_signal_breakdown(breakdown):
        """Generates a concise evidence-based summary of signal sources."""
        if not breakdown:
            return "실시간 시그널 분석 중"
        
        # Evidence-based fragments
        parts = []
        if breakdown.get('search', 0) > 70: parts.append(f"검색 지표 {int(breakdown['search'])}% 돌파")
        if breakdown.get('video', 0) > 70: parts.append(f"영상 화제성 {int(breakdown['video'])}% 상승")
        if breakdown.get('sns', 0) > 70: parts.append(f"SNS 언급 {int(breakdown['sns'])}% 폭증")
        if breakdown.get('community', 0) > 70: parts.append(f"커뮤니티 반응 {int(breakdown['community'])}% 활성")
        if breakdown.get('finance', 0) > 70: parts.append(f"거래 변동성 {int(breakdown['finance'])}% 확대")
        
        if not parts:
            # Fallback to strongest signal if none are over threshold
            max_key = max(breakdown.items(), key=lambda x: x[1])[0]
            label_map = {'search': '검색', 'video': '영상', 'sns': 'SNS', 'community': '커뮤니티', 'finance': '시장'}
            return f"{label_map.get(max_key, '다각도')} 시그널 유입 중 ({int(breakdown[max_key])}%)"
            
        return "📌 " + " | ".join(parts[:2]) # Keep it short

    try:
        # DataRouter를 통해 실시간 트렌드 로드 (Unified Engine)
        live_trends = connectors.fetch_active_realtime_trends_from_db()
        # Fallback & Top 15 Limit
        if not live_trends or len(live_trends) < 5:
            # Enhanced Fallback with 15 items to ensure UI verification
            fallback_items = [
                {"keyword": "일본 무비자 여행", "signal_breakdown": {"search": 95, "sns": 92, "news": 88}},
                {"keyword": "뉴진스 컴백 루머", "signal_breakdown": {"sns": 98, "video": 90}},
                {"keyword": "엔비디아 실적 발표", "signal_breakdown": {"finance": 96, "news": 94}},
                {"keyword": "아이폰 17 유출", "signal_breakdown": {"search": 85, "community": 88}},
                {"keyword": "비트코인 신고가", "signal_breakdown": {"finance": 99, "sns": 85}},
                {"keyword": "테슬라 로보택시", "signal_breakdown": {"video": 92, "news": 87}},
                {"keyword": "K-콘텐츠 글로벌 흥행", "signal_breakdown": {"sns": 88, "video": 95}},
                {"keyword": "금리 인하 전망", "signal_breakdown": {"finance": 85, "news": 90}},
                {"keyword": "생성형 AI 신기술", "signal_breakdown": {"search": 80, "community": 85}},
                {"keyword": "벚꽃 개화시기", "signal_breakdown": {"search": 95}},
                {"keyword": "리그 오브 레전드 패치", "signal_breakdown": {"community": 92, "video": 80}},
                {"keyword": "전기차 보조금 개편", "signal_breakdown": {"news": 88, "search": 82}},
                {"keyword": "스타벅스 신메뉴", "signal_breakdown": {"sns": 85, "search": 80}},
                {"keyword": "넷플릭스 신작 라인업", "signal_breakdown": {"video": 90, "sns": 82}},
                {"keyword": "서울 아파트 매매가", "signal_breakdown": {"search": 88, "finance": 80}}
            ]
            live_trends = fallback_items
        
        live_trends = live_trends[:10] # Limit to top 10
    except Exception as e:
        st.error(f"트렌드 엔진 오류: {e}")
        live_trends = []

    # Rendering the Ranking Board
    # Rendering the Ranking Board
    st.markdown('<div class="ranking-board">', unsafe_allow_html=True)
    
    # 🏁 Row Header (Desktop Only)
    # Using explicit classes for grid alignment synchronization
    st.markdown("""
        <div class="ranking-row-header">
            <div class="col-rank">순위</div>
            <div class="col-keyword">키워드</div>
            <div class="col-reason">실시간 시그널 해석</div>
            <div class="col-source">데이터 소스</div>
            <div class="col-action"></div> <!-- 🪓 Action field removed per user request -->
        </div>
    """, unsafe_allow_html=True)
    
    for i, item in enumerate(live_trends):
        rank = i + 1
        keyword = item.get('keyword', 'Unknown')
        
        # Signal Breakdown Processing
        breakdown = item.get('signal_breakdown', {})
        if isinstance(breakdown, str):
            try: breakdown = json.loads(breakdown)
            except: breakdown = {}
            
        insight = interpret_signal_breakdown(breakdown)
        
        # Data Source Icons HTML
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

        # 🔗 Keyword Link
        keyword_link = f"https://search.naver.com/search.naver?query={keyword}"

        # 📦 Flattened Column Structure for Grid/Flex Control
        # Using a sub-grid in col-rank/keyword for ultra-robust mobile layout
        row_html = f"""
        <div class="ranking-row">
            <div class="col-rank">
                <span class="rank-num">{rank}</span>
            </div>
            <div class="col-keyword">
                <a href="{keyword_link}" target="_blank" class="keyword-link">
                    <span class="keyword-text">{keyword}</span>
                </a>
            </div>
            <div class="col-reason">
                <div class="reason-text">{insight}</div>
            </div>
            <div class="col-source">
                <div class="source-container">{sources_html}</div>
            </div>
            <div class="col-action">
                <!-- Action button placeholder -->
            </div>
        </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)

        # 🚀 Connect Button via wrapper
        st.markdown('<div class="action-btn-wrapper">', unsafe_allow_html=True)
        if st.button("퀀텀 분석", key=f"q_scan_{i}", use_container_width=True):
            # 🎯 SAFE CONNECTIVITY SYNC (Pending pattern)
            st.session_state['pending_scan_keyword'] = keyword
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
