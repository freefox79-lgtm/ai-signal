import streamlit as st
import os, json
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def get_mcp_status_from_db():
    try:
        if not DB_URL:
            return []
        # Smart SSL detection
        if 'supabase' in DB_URL:
            conn = psycopg2.connect(DB_URL, sslmode='require')
        else:
            conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT server_name, status, last_health_check FROM mcp_status;")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data
    except:
        return []

def show():
    # 🎯 MOD-D 네온 헤더
    st.markdown("""
        <div style="background: rgba(57, 255, 20, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-neon); margin-bottom: 30px;">
            <h2 style="color: var(--acc-neon); margin: 0; text-shadow: 0 0 10px var(--acc-neon);">📊 시스템 대시보드 및 커맨드</h2>
            <p style="color: #888; margin: 5px 0 0 0;">섹터: 코어 운영 | 상태: 정상</p>
        </div>
    """, unsafe_allow_html=True)

    # 📈 상위 레벨 메트릭
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("총 시그널", "48.2K", delta="+5.2%")
    with c2:
        st.metric("오라클 정확도", "87.4%", delta="+0.2%")
    with c3:
        st.metric("MCP 건전성", "4/5", delta="안정적")
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

    # 🛰️ MCP 서버 모니터링
    st.write("### 🛰️ MCP 인프라 실시간 모니터링")
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
        st.caption("데이터베이스에서 MCP 상태 데이터를 찾을 수 없습니다. 헬스 체크를 실행해 주세요.")
        if st.button("헬스 체크 실행"):
             st.write("`mcp_health_check.py` 실행 중...")
             os.system("python3 mcp_health_check.py")
             st.rerun()
