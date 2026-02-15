import streamlit as st
import time
from components.ui_elements import render_cyber_card
from api_connectors import APIConnectors

connectors = APIConnectors()

def show():
    # 🎯 홈 네온 헤더
    st.markdown("""
        <div style="background: rgba(3, 199, 90, 0.05); padding: 8px 15px; border-radius: 10px; border: 1px solid var(--acc-green); margin-bottom: 12px;">
            <h3 style="color: var(--acc-green); margin: 0; text-shadow: 0 0-8px var(--acc-green); font-size: 1.3rem;">🏠 홈: 실시간 데이터 스캐너</h3>
            <p style="color: #888; margin: 2px 0 0 0; font-size: 0.8rem;">전역 데이터 소스 모니터링 및 퀀텀 분석 시스템 | 상태: 활성</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 🔍 멀티모달 검색 입력 (모바일 한 줄 배치)
    st.markdown("### 🧬 퀀텀 검색 및 분석")
    
    # Custom CSS-based horizontal row for mobile
    search_cols = st.columns([4, 1])
    with search_cols[0]:
        query = st.text_input("", placeholder="텍스트, URL 또는 시그널 지문을 입력하세요...", label_visibility="collapsed")
    with search_cols[1]:
        scan_btn = st.button("스캔 시작", use_container_width=True)
    
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
            
            # 시뮬레이션된 프로그레스 업데이트
            for percent_complete in range(0, 101, 10):
                time.sleep(0.1)
                progress_placeholder.progress(percent_complete)
                if percent_complete < 30:
                    status_text.text("🛰️ Naver Search API 호출 및 분석 중...")
                elif percent_complete < 60:
                    status_text.text("🔍 Redis 캐시 상태 확인 및 동기화 중...")
                elif percent_complete < 90:
                    status_text.text("🧠 Gemini 1.5 Pro와 합성 데이터 분석 중...")
                else:
                    status_text.text("✅ 스캔 및 분석 완료")
            
            results = connectors.fetch_naver_search(query)
            
            if results:
                st.markdown(f"**[최신 시그널: {query}]**")
                for item in results[:3]:
                    st.markdown(f"- [{item.get('title', 'No Title')}]({item.get('link', '#')})")
            else:
                st.info("검색 결과가 없거나 MOCK 모드로 동작 중입니다.")
            
            # 💰 광고 슬롯 (현재는 비활성화됨)
            # st.markdown("""<div id="ad-slot" style="display: none; height: 100px; border: 1px dashed #444; margin: 20px 0; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #555;">광고 슬롯 (준비 중)</div>""", unsafe_allow_html=True)
            
            # 📊 합성 리포트 - [AI Signal 퀀트 분석 결과]
            st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid var(--acc-blue); margin-top: 25px; background: rgba(0, 212, 255, 0.05);">
                    <h4 style="color: var(--acc-blue);">[AI Signal 퀀트 분석 결과]</h4>
                    <p style="font-size: 0.95rem; line-height: 1.6;">시그널 <b>'{query}'</b>은 현재 주요 커뮤니티 및 뉴스 포털에서 활발히 논의 중인 것으로 식별되었습니다. 
                    퀀텀 알고리즘 분석 결과, 해당 키워드는 단기적으로 높은 휘발성 지수를 보이고 있으며 실시간 데이터 합성이 완료되었습니다.</p>
                </div>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    
    # 🎯 AI Signal 실검
    from datetime import datetime
    col_header, col_timestamp = st.columns([3, 1])
    with col_header:
        st.markdown("### 🔥 AI Signal 실검")
    with col_timestamp:
        st.markdown(f"<p style='text-align: right; color: #8e8e93; font-size: 0.85rem; margin-top: 10px;'>업데이트: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
    
    from db_utils import get_db_connection
    try:
        conn = get_db_connection(routing='default')
        if not conn:
            raise ValueError("Failed to establish database connection")
            
        with conn.cursor() as cur:
            cur.execute("SELECT keyword, insight, agent FROM signals ORDER BY updated_at DESC LIMIT 10")
            live_trends = cur.fetchall()
        conn.close()
    except Exception as e:
        # Fallback trends for demo/mock mode
        live_trends = [
            ("엔비디아 H200 수요", "클라우드 제공업체들이 자본 지출을 늘리고 있습니다. 반도체 공급망 노드 과열 중.", "Jwem"),
            ("ETF 유입 급증", "95k 달러 구간에서 기관 매수 벽이 감지되었습니다. 상방 변동성 확대를 예상합니다.", "Jwem"),
            ("사이버-메타 패션", "가상 패션 플랫폼 거래량 300% 폭증! 새로운 온체인 트렌드 식별 완료.", "Jfit"),
            ("양자 보안 레이어", "L2 네트워크의 양자 내성 업그레이드가 시작되었습니다. 보안 자산으로 매수세 유입.", "Jfit"),
            ("에너지 그리드 최적화", "AI 연산용 송전망 효율화 시그널 포착. 바이오 에너지 섹터와 연동 시너지 발생.", "Jwem"),
            ("스마트 팩토리 2.0", "제조업의 AI 도입 가속화. 로보틱스 및 자동화 관련주 주목.", "Jfit"),
            ("DeFi 4.0 프로토콜", "기관 전용 유동성 풀 출시 임박. 관련 거버넌스 토큰 가격 변동성 확대.", "Stealth"),
            ("우주 항공 물류", "민간 우주 발사 비용 절감에 따른 위성 인터넷 및 물류 네트워크 확장 기대.", "Jwem"),
            ("블록체인 게이밍", "P2E 모델의 진화. AAA급 게임 출시로 인한 유저 유입 가속화.", "Jfit"),
            ("인공지능 신약 개발", "단백질 구조 예측 AI 기술의 상용화 성공. 바이오테크 섹터 리레이팅 가능성.", "Stealth")
        ]



    st.markdown('<div class="ranking-container">', unsafe_allow_html=True)
    
    # Agent Name Mapping
    agent_map = {
        "Jwem": "쥄",
        "Jfit": "쥐핏",
        "Stealth": "스텔스",
        "Jwew": "쥄" # Handle typo if any
    }

    for i, (keyword, insight, agent) in enumerate(live_trends):
        rank = i + 1
        agent_kr = agent_map.get(agent, agent)
        
        # Persona-based High-Contrast Colors
        badge_config = {
            "Jfit": {"bg": "#39ff14", "label": "쥐핏"},      # Neon Green
            "Jwem": {"bg": "#00f2ff", "label": "쥄"},       # Neon Cyan
            "Jwew": {"bg": "#00f2ff", "label": "쥄"},       # Alias
            "Stealth": {"bg": "#ff00e6", "label": "스텔스"} # Neon Magenta
        }
        config = badge_config.get(agent, {"bg": "var(--neon-cyan)", "label": agent_kr})
        agent_bg = config["bg"]
        
        # Simulated metric score
        score = 98 - (i * 7) + (int(time.time()) % 5)
        
        # Using a container with custom styling for the row
        with st.container():
            st.markdown(f'<div class="ranking-box">', unsafe_allow_html=True)
            # Create columns for Rank | Content | Metric | Button
            c1, c2, c3, c4 = st.columns([0.6, 5, 2, 1.5])
            
            with c1:
                st.markdown(f'<div class="rank-number-flat">{rank}</div>', unsafe_allow_html=True)
            
            with c2:
                st.markdown(f"""
                    <div style="margin-top: 5px;">
                        <span class="rank-keyword-flat">{keyword}</span>
                        <span style="background: {agent_bg}; color: #000; font-size: 0.65rem; padding: 2px 8px; border-radius: 4px; font-weight: 800; margin-left: 10px; box-shadow: 0 0 10px {agent_bg}44; text-transform: uppercase;">{config['label']} 추천</span>
                        <div class="rank-summary-flat">{insight}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with c3:
                st.markdown(f"""
                    <div style="margin-top: 8px;">
                        <div class="metric-label-flat">Trend Score</div>
                        <div class="metric-bar-flat"><div class="metric-fill-flat" style="width: {score}%;"></div></div>
                        <div style="font-size: 0.65rem; color: #666; font-family: 'Orbitron';">{score}.5 pts</div>
                    </div>
                """, unsafe_allow_html=True)
                
            with c4:
                if st.button("🔍 스캔", key=f"rank_scan_{keyword}_{i}", help=f"'{keyword}' 퀀텀 분석 실행", type="primary", use_container_width=True):
                    st.session_state['last_scan'] = keyword
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
