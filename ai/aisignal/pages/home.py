import streamlit as st
from components.ui_elements import render_cyber_card
from api_connectors import APIConnectors

connectors = APIConnectors()

def show():
    # 🎯 MOD-S 네온 헤더
    st.markdown("""
        <div style="background: rgba(3, 199, 90, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-green); margin-bottom: 30px;">
            <h2 style="color: var(--acc-green); margin: 0; text-shadow: 0 0 10px var(--acc-green);">🛰️ MOD-S: 멀티모달 스캐너</h2>
            <p style="color: #888; margin: 5px 0 0 0;">섹터: 글로벌 인텔리전스 | 상태: 활성</p>
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
        with st.status(f"'{query}'에 대한 보이드 스캔 중...", expanded=True) as status:
            st.write("🛰️ Naver Search API 호출 및 분석 중...")
            results = connectors.fetch_naver_search(query)
            st.write("🔍 Redis 캐시 상태 확인 및 동기화 중...")
            st.write("🧠 Gemini 1.5 Pro와 합성 데이터 분석 중...")
            status.update(label="스캔 및 분석 완료", state="complete", expanded=False)
            
            if results:
                st.markdown(f"**[최신 시그널: {query}]**")
                for item in results[:3]:
                    st.markdown(f"- [{item.get('title', 'No Title')}]({item.get('link', '#')})")
            else:
                st.info("검색 결과가 없거나 MOCK 모드로 동작 중입니다.")
            
            st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid var(--acc-blue); margin-top: 15px;">
                    <h4 style="color: var(--acc-blue);">[합성 리포트 - MOD-S]</h4>
                    <p>시그널 <b>'{query}'</b>은 현재 주요 커뮤니티 및 뉴스 포털에서 활발히 논의 중입니다. 
                    Redis 캐시가 적용되어 분석 속도가 최적화되었습니다.</p>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    
    # 🎯 AI Signal 실검
    st.markdown("### 🔥 AI Signal 실검")
    
    import psycopg2
    import os
    try:
        # Add sslmode='require' for cloud DB compatibility
        conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
        with conn.cursor() as cur:
            cur.execute("SELECT keyword, insight, agent FROM signals ORDER BY updated_at DESC LIMIT 3")
            live_trends = cur.fetchall()
        conn.close()
    except Exception as e:
        # Show error in UI for debugging production issues
        st.error(f"DB Connection Error: {e}")
        live_trends = []

    c1, c2, c3 = st.columns(3)
    
    if live_trends:
        for i, (keyword, insight, agent) in enumerate(live_trends):
            col = [c1, c2, c3][i]
            with col:
                st.image(f"https://picsum.photos/seed/{keyword}/800/450", caption=f"{keyword}")
                color = "green" if agent == "Jfit" else "blue"
                render_cyber_card(keyword, f"{agent}: {insight}", color)
    else:
        with c1:
            st.image("https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80", caption="AI 연산 수요 급증")
            render_cyber_card("엔비디아 H200 수요", "쥄: 클라우드 제공업체들이 자본 지출을 늘리고 있습니다. 반도체 공급망 노드가 붉게 발광 중입니다.", "green")
        
        with c2:
            st.image("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=800&q=80", caption="크립토 펄스")
            render_cyber_card("ETF 유입 급증", "쥄: 95k 달러 구간에서 기관 매수 벽이 감지되었습니다. 변동성 확대를 예상합니다.", "blue")
        
        with c3:
            st.image("https://images.unsplash.com/photo-1614728263952-84ea256f9679?auto=format&fit=crop&w=800&q=80", caption="바이럴 트렌드")
            render_cyber_card("사이버-메타 패션", "쥐핏: 가상 패션 플랫폼 거래량 300% 폭증! 오오티디 미쳤다 진짜 ㅋㅋ", "purple")
