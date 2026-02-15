import streamlit as st
import psycopg2
import os
from components.ui_elements import render_cyber_card
from api_connectors import APIConnectors
from dotenv import load_dotenv
from db_utils import get_db_connection

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
connectors = APIConnectors()

def get_live_data():
    try:
        if not DB_URL:
            return [], []
        # Use the utility function to get the database connection
        conn = get_db_connection(DB_URL)
        with conn.cursor() as cur:
            # Fetch Jwem's Portfolio
            cur.execute("SELECT stock_code, current_price, profit_rate FROM jwem_portfolio LIMIT 5")
            portfolio = cur.fetchall()
            # Fetch Jfit's Trends
            cur.execute("SELECT keyword, insight FROM signals WHERE agent = 'Jfit' ORDER BY updated_at DESC LIMIT 3")
            trends = cur.fetchall()
        conn.close()
        return portfolio, trends
    except Exception as e:
        print(f"[UI ERROR] {e}")
        return [], []

def show():
    # 🎯 에이전트스페이스 네온 헤더
    st.markdown("""
        <div style="background: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-blue); margin-bottom: 30px;">
            <h2 style="color: var(--acc-blue); margin: 0; text-shadow: 0 0 10px var(--acc-blue);">🤖 에이전트스페이스: 지능형 협업 분석</h2>
            <p style="color: #888; margin: 5px 0 0 0;">쥄(금융/매크로) & 쥐핏(트렌드/SNS) AI 에이전트 브리핑 | 상태: 동기화됨</p>
        </div>
    """, unsafe_allow_html=True)

    portfolio, trends = get_live_data()

    # 🚀 분할 뷰 설정
    col_jwem, col_jfit = st.columns(2)
    
    with col_jwem:
        st.markdown("""
            <div style='background: rgba(0, 212, 255, 0.1); padding: 10px; border-radius: 10px; border-bottom: 2px solid var(--acc-blue); margin-bottom: 20px;'>
                <h3 style='color: var(--acc-blue); margin: 0;'>📘 쥄: 매크로 & 금융</h3>
            </div>
        """, unsafe_allow_html=True)
        
        if portfolio:
            for stock, price, p_rate in portfolio:
                render_cyber_card(f"{stock}", f"현재가: ${price} | 수익률: {p_rate or 0}%", "blue")
        else:
            st.caption("포트폴리오 데이터가 아직 없습니다.")

    with col_jfit:
        st.markdown("""
            <div style='background: rgba(57, 255, 20, 0.1); padding: 10px; border-radius: 10px; border-bottom: 2px solid var(--acc-neon); margin-bottom: 20px;'>
                <h3 style='color: var(--acc-neon); margin: 0;'>🔥 쥐핏: 하이프 & SNS</h3>
            </div>
        """, unsafe_allow_html=True)
        
        if trends:
            for keyword, insight in trends:
                render_cyber_card(f"LIVE: {keyword}", insight, "green")
        else:
            render_cyber_card("S-Tier 밈 경보", "데이터 수집 중... 쥐핏이 열일하고 있습니다.", "green")

    st.divider()
    
    # 🎯 크로스 페르소나 합성
    st.markdown("### 🧬 하이브리드 합성 리포트")
    st.markdown("""
        <div class="glass-card" style="border: 1px solid var(--acc-purple);">
            <p style="color: var(--acc-purple); font-weight: bold;">[로고스 + 파토스 수렴]</p>
            <p>쥄은 기술적 타당성을 확인했고, 쥐핏은 바이럴 잠재력을 확인했습니다. 섹터: <b>AI 기반 엔터테인먼트</b>. 
            권장 사항: 인프라 노드 강력 매수, 개별 토큰은 신중한 진입 권장.</p>
        </div>
    """, unsafe_allow_html=True)
