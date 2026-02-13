import streamlit as st

def show():
    # 🎯 MOD-W 네온 헤더
    st.markdown("""
        <div style="background: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-blue); margin-bottom: 30px;">
            <h2 style="color: var(--acc-blue); margin: 0; text-shadow: 0 0 10px var(--acc-blue);">🌐 MOD-W: GRAPHRAG 지식 지도</h2>
            <p style="color: #888; margin: 5px 0 0 0;">섹터: 지식 합성 | 상태: 매핑 중...</p>
        </div>
    """, unsafe_allow_html=True)

    # 🔍 노드 검색
    st.markdown("### 🔍 지식 노드 검색")
    query = st.text_input("", placeholder="검색할 노드를 입력하세요 (예: '반도체 공급망')...", label_visibility="collapsed")
    
    if query:
        st.write(f"**{query}**와 관련된 그래프 노드 탐색 중...")
    
    # 🕸️ 그래프 시각화 플레이스홀더
    st.markdown("""
        <div class="glass-card" style="height: 500px; position: relative; overflow: hidden; border: 1px dashed var(--acc-blue); background: radial-gradient(circle, rgba(0,212,255,0.05) 0%, rgba(0,0,0,1) 100%);">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                <h2 style="color: var(--acc-blue); opacity: 0.5; letter-spacing: 10px;" class="neon-text">시스템 매핑 중</h2>
                <p style="color: #555;">[ Cytoscape.js / Pyvis 캔버스 연동 타겟 ]</p>
                <div style="display: flex; gap: 20px; justify-content: center; margin-top: 20px;">
                    <span style="color: var(--acc-green);">● 노드: 1,420</span>
                    <span style="color: var(--acc-purple);">● 엣지: 5,280</span>
                </div>
            </div>
            <!-- 목 노드 -->
            <div style="position: absolute; top: 20%; left: 30%; width: 10px; height: 10px; background: var(--acc-blue); border-radius: 50%; box-shadow: 0 0 10px var(--acc-blue);"></div>
            <div style="position: absolute; top: 60%; left: 70%; width: 10px; height: 10px; background: var(--acc-green); border-radius: 50%; box-shadow: 0 0 10px var(--acc-green);"></div>
            <div style="position: absolute; top: 40%; left: 50%; width: 15px; height: 15px; background: var(--acc-purple); border-radius: 50%; box-shadow: 0 0 15px var(--acc-purple);"></div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 📚 최근 합성 데이터
    st.write("### 📖 최근 지식 합성 내역")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
            <div class="glass-card">
                <h5 style="color: var(--acc-green);">[노드 싱크] HBM3e 제조 공정</h5>
                <p style="font-size: 0.9rem; color: #888;">합성 시간: 2시간 전 | 신뢰도: 94%</p>
                <p>SK 하이닉스 수율과 엔비디아 B200 타임라인 간의 연결 관계가 수립되었습니다. 시장 영향: 치명적.</p>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class="glass-card">
                <h5 style="color: var(--acc-blue);">[이벤트 GRAG] 미국 대선 변동성</h5>
                <p style="font-size: 0.9rem; color: #888;">합성 시간: 5시간 전 | 신뢰도: 82%</p>
                <p>경합 주 정서와 친환경 에너지 주식 선물 간의 상관관계가 매핑되었습니다. 권장 조치: 헤지.</p>
            </div>
        """, unsafe_allow_html=True)
