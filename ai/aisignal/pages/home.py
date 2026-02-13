import streamlit as st
from components.ui_elements import render_cyber_card

def show():
    # 🎯 MOD-S 네온 헤더
    st.markdown("""
        <div style="background: rgba(3, 199, 90, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-green); margin-bottom: 30px;">
            <h2 style="color: var(--acc-green); margin: 0; text-shadow: 0 0 10px var(--acc-green);">🛰️ MOD-S: 멀티모달 스캐너</h2>
            <p style="color: #888; margin: 5px 0 0 0;">섹터: 글로벌 인텔리전스 | 상태: 활성</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 🔍 멀티모달 검색 입력
    st.markdown("### 🧬 퀀텀 검색 및 분석")
    cols = st.columns([5, 1])
    with cols[0]:
        query = st.text_input("", placeholder="텍스트, URL 또는 시그널 지문을 여기에 입력하세요...", label_visibility="collapsed")
    with cols[1]:
        if st.button("스캔 시작", use_container_width=True):
            if query:
                st.toast(f"MCP 서버와 동기화 중: {query}")
                st.session_state['last_scan'] = query
            else:
                st.warning("시그널 소스를 제공해 주세요.")
    
    # 🚀 네온 애니메이션 / 스캔 상태
    if 'last_scan' in st.session_state:
        with st.status(f"'{st.session_state['last_scan']}'에 대한 보이드 스캔 중...", expanded=True) as status:
            st.write("🛰️ Google Search MCP 쿼리 중...")
            st.write("🔍 Puppeteer MCP로 브라우징 중...")
            st.write("🧠 Gemini 1.5 Pro와 합성 중...")
            status.update(label="분석 완료", state="complete", expanded=False)
            
            st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid var(--acc-blue);">
                    <h4 style="color: var(--acc-blue);">[합성 리포트]</h4>
                    <p>시그널 <b>'{st.session_state['last_scan']}'</b>은 AI 자동화 섹터의 신흥 트렌드와 높은 상관관계를 보입니다. 
                    권장 조치: 변동성에 대비해 <i>오라클 마켓</i>을 모니터링하십시오.</p>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    
    # 🎯 트렌딩 시그널
    st.markdown("### 🔥 고우선순위 시그널")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.image("https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80", caption="AI 연산 수요 급증")
        render_cyber_card("엔비디아 H200 수요", "쥄: 클라우드 제공업체들이 자본 지출을 늘리고 있습니다. 반도체 공급망 노드가 붉게 발광 중입니다.", "green")
    
    with c2:
        st.image("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=800&q=80", caption="크립토 펄스")
        render_cyber_card("ETF 유입 급증", "쥄: 95k 달러 구간에서 기관 매수 벽이 감지되었습니다. 변동성 확대를 예상합니다.", "blue")
    
    with c3:
        st.image("https://images.unsplash.com/photo-1614728263952-84ea256f9679?auto=format&fit=crop&w=800&q=80", caption="바이럴 트렌드")
        render_cyber_card("사이버-메타 패션", "쥐핏: 가상 패션 플랫폼 거래량 300% 폭증! 오오티디 미쳤다 진짜 ㅋㅋ", "purple")
