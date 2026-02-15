import streamlit as st
import psycopg2
import os
from components.ui_elements import render_cyber_card
from api_connectors import APIConnectors
from dotenv import load_dotenv
from db_utils import get_db_connection

load_dotenv()
connectors = APIConnectors()

def get_live_data():
    try:
        # 시장 지배 지수 & 트렌드는 로컬 및 기본 DB에서 혼합 추출
        conn_local = get_db_connection(routing='local')
        conn_cloud = get_db_connection(routing='default')
        
        indices = []
        trends = []
        
        if conn_local:
            with conn_local.cursor() as cur:
                cur.execute("SELECT name, value, change FROM market_indices LIMIT 4")
                indices = cur.fetchall()
        
        if conn_cloud:
            with conn_cloud.cursor() as cur:
                cur.execute("SELECT keyword, insight FROM signals WHERE agent = 'Jfit' ORDER BY updated_at DESC LIMIT 3")
                trends = cur.fetchall()
                
        return indices, trends
    except Exception as e:
        print(f"[UI ERROR] {e}")
        return [], []

def get_expanded_intelligence():
    """새로운 지능형 레이어 데이터 추출"""
    intel = {
        "correlations": [],
        "district": [],
        "briefings": []
    }
    try:
        conn_local = get_db_connection(routing='local')
        conn_cloud = get_db_connection(routing='default')
        
        if conn_local:
            with conn_local.cursor() as cur:
                # 1. 매크로-마이크로 상관관계
                cur.execute("SELECT fred_series_id, signal_keyword, correlation_coefficient, insight_text FROM market_macro_correlations ORDER BY updated_at DESC LIMIT 2")
                intel["correlations"] = cur.fetchall()
                
                # 2. 지역 상권 지능
                cur.execute("SELECT district_name, jfit_hype_score, ai_recommendation FROM local_district_intelligence ORDER BY last_scan_at DESC LIMIT 2")
                intel["district"] = cur.fetchall()
        
        if conn_cloud:
            with conn_cloud.cursor() as cur:
                # 3. 합성 브리핑
                cur.execute("SELECT title, summary, agent_consensus, is_hot FROM synthetic_briefings ORDER BY created_at DESC LIMIT 1")
                intel["briefings"] = cur.fetchall()
                
        return intel
    except Exception as e:
        print(f"[UI ERROR] Expanded Intel: {e}")
        return intel

def show():
    # 🎯 에이전트스페이스 네온 헤더
    st.markdown("""
        <div style="background: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-blue); margin-bottom: 30px;">
            <h2 style="color: var(--acc-blue); margin: 0; text-shadow: 0 0 10px var(--acc-blue);">🤖 에이전트스페이스: 지능형 협업 분석</h2>
            <p style="color: #888; margin: 5px 0 0 0;">쥄(금융/매크로) & 쥐핏(트렌드/SNS) AI 에이전트 브리핑 | 상태: 동기화됨</p>
        </div>
    """, unsafe_allow_html=True)

    indices, trends = get_live_data()
    intel = get_expanded_intelligence()

    # 🚀 분할 뷰 설정 (쥄 & 쥐핏 기본 브리핑)
    col_jwem, col_jfit = st.columns(2)
    
    with col_jwem:
        st.markdown("<h3 style='color: var(--acc-blue);'>📘 쥄: 시장 모니터링</h3>", unsafe_allow_html=True)
        if indices:
            for name, value, change in indices:
                trend_color = "green" if change > 0 else "red"
                render_cyber_card(f"{name}", f"지수: {value} | 변동: {change}%", trend_color)
        else:
            st.caption("시장 데이터를 가져오는 중입니다...")

    with col_jfit:
        st.markdown("<h3 style='color: var(--acc-neon);'>🔥 쥐핏: 하이프 & SNS</h3>", unsafe_allow_html=True)
        if trends:
            print(f"[DEBUG] Trends Data: {trends}")
            for row in trends:
                # Mock Mode may return 3 cols (including agent), Real Mode 2 cols. Safe unpack.
                keyword = row[0]
                insight = row[1]
                render_cyber_card(f"LIVE: {keyword}", insight, "green")
        else:
            render_cyber_card("S-Tier 밈 경보", "데이터 수집 중...", "green")

    st.divider()
    
    # 🧠 지능형 레이어 확장 섹션
    st.markdown("### 🧬 Intelligence Layer: 복합 데이터 합성")
    
    # 1. 합성 브리핑 (Synthetic Briefing)
    if intel["briefings"]:
        for title, summary, consensus, is_hot in intel["briefings"]:
            hot_badge = "🔥 [HOT] " if is_hot else ""
            st.markdown(f"""
                <div style="background: rgba(138, 43, 226, 0.1); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-purple); margin-bottom: 20px;">
                    <h4 style="color: var(--acc-purple); margin-top: 0;">{hot_badge}{title}</h4>
                    <p style="font-size: 0.9rem; line-height: 1.6;">{summary}</p>
                    <div style="display: flex; gap: 10px; font-size: 0.8rem; opacity: 0.8;">
                        <span>신뢰도: {consensus.get('jwem', 0)*100:.0f}% (쥄) | {consensus.get('jfit', 0)*100:.0f}% (쥐핏)</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        # Fallback Mock if no briefing
        st.info("실시간 매크로-트렌드 합성 브리핑을 생성 중입니다...")

    # 2. 하부 카드 (상관관계 & 지역 상권)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📉 매크로-마이크로 상관성")
        if intel["correlations"]:
            for series, keyword, coeff, text in intel["correlations"]:
                render_cyber_card(f"{series} ↔ {keyword}", f"상계수: {coeff} | {text}", "blue")
        else:
            st.caption("상관관계 분석 엔진 가동 중...")
            
    with c2:
        st.markdown("#### 📍 지역 상권 SNS 하이프")
        if intel["district"]:
            for name, score, rec in intel["district"]:
                score_color = "green" if score > 70 else "yellow"
                render_cyber_card(f"{name} (Score: {score})", rec, score_color)
        else:
            st.caption("지역 상권 시그널 스캔 중...")
