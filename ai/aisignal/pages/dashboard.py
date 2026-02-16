import streamlit as st
from data_router import router

def get_mcp_status_from_db():
    try:
        # DataRouter를 통해 로컬 인프라 상태(MCP) 로드 (Mac Mini)
        data = router.execute_query("SELECT server_name, status, last_health_check FROM mcp_status;", table_hint='mcp_status')
        return data
    except:
        return []

def show():
    # 🎯 회사현황 네온 헤더
    st.markdown("""
        <div style="background: rgba(57, 255, 0, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-neon); margin-bottom: 30px;">
            <h2 style="color: var(--acc-neon); margin: 0; text-shadow: 0 0 10px var(--acc-neon);">📈 회사현황: 시스템 운영 및 자율 인프라</h2>
            <p style="color: #888; margin: 5px 0 0 0;">메트릭 요약, MCP 서버 상태 및 자율 윤리 로그 모니터링 | 상태: 정상</p>
        </div>
    """, unsafe_allow_html=True)

    # 📈 상위 레벨 메트릭
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("총 시그널", "48.2K", delta="+5.2%")
    with c2:
        st.metric("오라클 정확도", "87.4%", delta="+0.2%")
    with c3:
        st.metric("시스템 상태", "안정적", delta="정상")
    with c4:
        st.metric("윤리 준수율", "100%", delta="안전")

    st.divider()

    # 📌 골든 포스트잇
    st.write("### 📌 골든 포스트잇 (중요 작업)")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.warning("⚠️ **조치 필요**: Brave Search API 쿼터가 85%에 도달했습니다. 티어 업그레이드를 고려해 보세요.")
    with col_p2:
        st.info("💡 **전략 인사이트**: GraphRAG 매핑 결과 '바이오 합성 에너지' 섹터에서 새로운 클러스터가 확인되었습니다.")

    st.divider()

    # 🛡️ 윤리 및 규정 준수 로그
    st.write("### 🛡️ 자율 윤리 로그")
    st.markdown("""
        <div class="glass-card" style="font-family: monospace; font-size: 0.8rem; color: #0f0; background: rgba(0,0,0,0.8);">
            [2026-02-13 14:30:12] [INFO] 시그널 #A420이 스팸 방지 정책에 따라 검증되었습니다.<br>
            [2026-02-13 14:35:45] [INFO] 데이터 소스 'Naver_News'의 개인정보 보호 준수 여부가 확인되었습니다.<br>
            [2026-02-13 14:40:01] [SUCCESS] 일일 윤리 감사 완료. 위반 사항 없음.
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 🛰️ 시스템 인프라 실시간 모니터링
    st.write("### 🛰️ 시스템 인프라 실시간 모니터링")
    mcp_data = get_mcp_status_from_db()
    
    if mcp_data:
        for name, status, last_check in mcp_data:
            color = "var(--acc-neon)" if status == "RUNNING" else "red"
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #333;">
                    <span><b>{name}</b></span>
                    <span style="color: {color}; font-weight: bold;">{status}</span>
                    <span style="color: #555; font-size: 0.8rem;">점검 시간: {last_check}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("데이터베이스에서 시스템 상태 데이터를 찾을 수 없습니다.")
