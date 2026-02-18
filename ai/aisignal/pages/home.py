import streamlit as st
# force deploy 2026-02-18 11:45 (Golden Ratio)
import time
from components.ui_elements import render_cyber_card
from api_connectors import APIConnectors

connectors = APIConnectors()

def show():
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
        scan_btn = st.button("퀀텀 검색", use_container_width=True)
    
    # 🚀 네온 애니메이션 / 스캔 상태 (결과 출력 위치 고정)
    if scan_btn and query:
        st.session_state['last_scan'] = query
    
    if 'last_scan' in st.session_state:
        query = st.session_state['last_scan']
        
        # 📊 통합 프로그레스 바 및 상태 표시
        progress_placeholder = st.empty()
        status_text = st.empty()
        
        # 📦 결과물 출력을 위한 별도 박스 (Container)
        with st.container():
            st.markdown(f"""
                <div style="border: 1px solid var(--acc-blue); border-radius: 15px; padding: 25px; background: rgba(0, 212, 255, 0.02); margin-top: 20px;">
                    <h3 style="color: var(--acc-blue); margin-top: 0;">🔍 스캔 및 분석 결과</h3>
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
                    </div>
                """, unsafe_allow_html=True)
            else:
                 st.markdown(f"""
                    <div class="glass-card" style="border-left: 4px solid var(--acc-blue); margin-top: 25px; background: rgba(0, 212, 255, 0.05);">
                        <h4 style="color: var(--acc-blue);">[AI Signal 퀀트 분석 결과]</h4>
                        <p style="font-size: 0.95rem; line-height: 1.6;">분석할 데이터가 부족합니다. 검색 결과를 먼저 확보해주세요.</p>
                    </div>
                    </div>
                """, unsafe_allow_html=True)

    st.divider()
    
    # 🎯 AI Signal 실검
    from datetime import datetime
    col_header, col_timestamp = st.columns([3, 1])
    with col_header:
        st.markdown("<h3 style='font-size: 1.8rem; margin: 0;'>🔥 AI Signal 실검</h3>", unsafe_allow_html=True)
    with col_timestamp:
        st.markdown(f"<p style='text-align: right; color: #8e8e93; font-size: 0.95rem; margin-top: 15px;'>업데이트: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    
    try:
        # DataRouter를 통해 실시간 트렌드 로드 (Unified Engine)
        live_trends = connectors.fetch_active_realtime_trends_from_db()
        # Fallback for UI Verification (King vs Soldier)
        if not live_trends:
            live_trends = [{
                "keyword": "일본 무비자 여행",
                "related_insight": "네이버 검색량이 전일 대비 380% 급증했습니다. 팬데믹 종료 후 첫 무비자 시즌을 맞이하여 여행 수요가 폭발 중입니다.",
                "type": "BREAKING",
                "avg_score": 98.5,
                "signal_breakdown": {"search": 95, "sns": 92, "news": 88}
            }]
    except Exception as e:
        st.error(f"트렌드 엔진 오류: {e}")
        live_trends = []

    st.markdown('<div class="ranking-container">', unsafe_allow_html=True)
    
    import json
    import html
    
    all_items_html = ""
    # Render loop with columns for interactivity
    for i, item in enumerate(live_trends):
        rank = i + 1
        keyword = item.get('keyword', 'Unknown')
        insight = item.get('related_insight', '')
        
        # Fallback if insight is missing or technical
        if not insight or insight.startswith("Signals:") or insight.startswith("Sources:"):
             insight = "AI가 퀀텀 시그널을 분석 중입니다..."

        source = item.get('source', 'System')
        signal_type = item.get('type', item.get('status', 'INFO'))
        link = item.get('link', '#')
        score = float(item.get('avg_score', 80))
        
        # Badge Configuration
        badge_config = {
            "BREAKING": {"bg": "#ff2a2a", "label": "🚨 속보"},
            "VIRAL": {"bg": "#ff00e6", "label": "🔥 바이럴"},
            "SHOPPING": {"bg": "#39ff14", "label": "🛍️ 쇼핑"},
            "MACRO": {"bg": "#00f2ff", "label": "🌍 거시"},
            "NEWS": {"bg": "#007AFF", "label": "📰 뉴스"},
            "RISING": {"bg": "#888", "label": "📈 상승"},
        }
        
        config = badge_config.get(signal_type, {"bg": "#444", "label": signal_type})
        badge_bg = config["bg"]
        badge_label = config["label"]
        
        # Signal Breakdown Rendering
        breakdown = item.get('signal_breakdown', {})
        if isinstance(breakdown, str):
            try:
                breakdown = json.loads(breakdown)
            except:
                breakdown = {}
        
        badges_html = ""
        if breakdown:
            sorted_signals = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:4]
            icons = {'search': '🔍', 'video': '📺', 'sns': '🐦', 'community': '💬', 'finance': '💰'}
            colors = {'search': '#03c75a', 'video': '#ff0000', 'sns': '#1da1f2', 'community': '#ff4500', 'finance': '#f7931a'}
            
            for k, v in sorted_signals:
                if v > 0:
                    icon = icons.get(k, '🔹')
                    color = colors.get(k, '#888')
                    badges_html += f'<span style="background: rgba(255,255,255,0.05); border: 1px solid {color}88; color: #ddd; font-size: 0.65rem; padding: 2px 8px; border-radius: 6px; margin-right: 5px; margin-bottom: 5px; display: inline-block;">{icon} {int(v)}</span>'

        # Ranking Row Container
        with st.container():
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; margin-bottom: 15px;">
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 6, 2])
            
            with c1:
                st.markdown(f"""<div style="font-family: 'Orbitron', sans-serif; font-size: 1.6rem; font-weight: 900; color: var(--acc-blue); text-shadow: 0 0 10px var(--acc-blue); text-align: center; line-height: 1.2;">{rank}</div>""", unsafe_allow_html=True)
                
            with c2:
                # Headline Keyword - The King (1.8rem / 900)
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 15px;">
                    <a href="{link}" target="_blank" style="text-decoration: none !important; color: white !important; font-size: 1.8rem !important; font-weight: 900 !important; letter-spacing: -1px !important; line-height: 1.0 !important; text-shadow: 0 0 15px rgba(255,255,255,0.2) !important;">{keyword}</a>
                    <span style="background: {badge_bg} !important; color: #000 !important; font-size: 0.8rem !important; padding: 2px 10px !important; border-radius: 4px !important; font-weight: 900 !important; vertical-align: middle !important;">{badge_label}</span>
                </div>
                <!-- Physical Gap Injection -->
                <div style="height: 30px !important;"></div>
                <!-- Analysis Report Section - The Soldier (1.15rem / 600) -->
                <div style="border-top: 1px solid rgba(255,255,255,0.1) !important; padding-top: 18px !important;">
                    <div style="color: #CCCCCC !important; font-size: 0.95rem !important; line-height: 1.7 !important; margin-bottom: 20px !important;">
                        <span id="report-title-{rank}" style="color: var(--acc-blue) !important; font-weight: 600 !important; font-size: 1.15rem !important; display: block !important; margin-bottom: 12px !important;">📊 분석 리포트</span>
                        <div id="report-body-{rank}">{insight}</div>
                    </div>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">{badges_html}</div>
                """, unsafe_allow_html=True)
                
            with c3:
                # Infographic Score Display
                st.markdown(f"""
                <div style="background: rgba(0, 212, 255, 0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(0, 212, 255, 0.15); text-align: center; margin-bottom: 15px;">
                    <div style="font-family: 'Orbitron', sans-serif; font-size: 0.9rem; font-weight: 600; color: #777; margin-bottom: 8px; letter-spacing: 1px;">시그널 강도</div>
                    <div style="font-family: 'Orbitron', sans-serif; font-size: 1.3rem; font-weight: 900; color: var(--acc-blue); text-shadow: 0 0 10px var(--acc-blue);">{score:.1f}%</div>
                    <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.08); border-radius: 20px; overflow: hidden; margin-top: 10px; border: 1px solid rgba(255,255,255,0.03);">
                        <div style="width: {min(score, 100)}%; height: 100%; background: linear-gradient(90deg, #00d4ff, #ff00e6); box-shadow: 0 0 15px rgba(0, 212, 255, 0.6);"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # The Missing Scan Button
                # High Contrast & Neon Effect via internal styling (simulated with help text or just text)
                # Streamlit button styling is limited, but we remove the icon.
                if st.button("퀀텀 검색", key=f"scan_{i}", help=f"🚀 {keyword} 심층 전략 분석 시작", use_container_width=True):
                    st.session_state['last_scan'] = keyword
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
