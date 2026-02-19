import streamlit as st
import pandas as pd
import sys
import os
import textwrap

# 모듈 경로 문제 해결을 위해 루트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_router import router
import pandas as pd

def fetch_issues():
    """DB에서 이슈 데이터를 가져옵니다."""
    try:
        # DataRouter를 통해 Supabase(default)에서 이슈 데이터 로드
        data = router.execute_query("""
            SELECT id, category, title, 
                   pros_count, cons_count, 
                   agent_pros_count, agent_cons_count, 
                   external_agent_pros_count, external_agent_cons_count,
                   is_closed FROM issues
        """, table_hint='issues')
        
        columns = [
            'id', 'category', 'title', 
            'pros_count', 'cons_count', 
            'agent_pros_count', 'agent_cons_count', 
            'external_agent_pros_count', 'external_agent_cons_count',
            'is_closed'
        ]
        
        if data:
            return pd.DataFrame(data, columns=columns)
        else:
            return pd.DataFrame(columns=columns)
    except Exception as e:
        st.error(f"이슈 데이터 로드 실패: {e}")
        return pd.DataFrame()

def show():
    # 🎯 핫이슈 네온 헤더
    st.markdown("""
        <div class="tab-intro-card">
            <h2 class="intro-title">🔥 핫이슈: 지능형 시장 신호와 예측</h2>
            <p class="intro-desc">실시간 고위험/고수익 시그널 및 미래 예측 데이터 분석 | 상태: 퀀텀 싱크</p>
        </div>
    """, unsafe_allow_html=True)

    # Sub-tab Navigation (Radio as Description Boxes)
    st.markdown("""
    <style>
        /* Hide default radio style */
        div[data-testid="stRadio"] > label {
            display: none !important;
        }
        .stRadio > div[role="radiogroup"] {
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            width: 100%;
        }
        .stRadio label {
            background: rgba(30, 20, 50, 0.6);
            border: 1px solid rgba(157, 0, 255, 0.3);
            border-radius: 12px;
            padding: 12px 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
            
            /* Responsive Sizing */
            flex: 1 1 200px;
            min-width: 200px;
            max-width: 350px;
            
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .stRadio label:hover {
            background: rgba(157, 0, 255, 0.1);
            border-color: var(--acc-purple);
            transform: translateY(-2px);
        }
        /* Selected State */
        .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            display: none; /* Hide default radio circle */
        }
        
        /* Selected State Glow Effect */
        div[role="radiogroup"] > label:has(input:checked) {
            background: rgba(20, 0, 40, 0.9) !important;
            border-color: var(--acc-purple) !important;
            box-shadow: 0 0 20px var(--acc-purple), inset 0 0 10px rgba(157, 0, 255, 0.4) !important;
            color: #ffffff !important;
            transform: translateY(-2px);
            z-index: 10;
        }
        
        /* Make sure the label is clickable */
        .stRadio label {
            position: relative;
            z-index: 5;
        }
    </style>
    """, unsafe_allow_html=True)

    # Custom "Description Box" Sub-menu
    selected_oracle_tab = st.radio(
        "Oracle Section Selection",
        ["🔥 논란 이슈 (Issues)", "🏁 논란 종결 (Results)"],
        horizontal=True,
        label_visibility="collapsed",
        key="oracle_radio"
    )

    st.markdown("---")
    
    # 데이터 로드
    df_issues = fetch_issues()
    
    if df_issues.empty:
        st.info("현재 표시할 이슈 데이터가 없습니다.")
        return

    # 🔥 논란 이슈 (Voting) Content
    if "논란 이슈" in selected_oracle_tab:
        st.markdown("""
        <div style="background: rgba(157, 0, 255, 0.05); padding: 20px; border-radius: 10px; border: 1px solid var(--acc-purple); margin-bottom: 30px; text-align: center;">
            <h3 style="color: var(--acc-purple); margin: 0;">🗳️ 오늘의 논란 이슈 (Voting)</h3>
            <p style="color: #ccc; margin-top: 5px;">찬성 vs 반대 | 당신의 의견을 투표하세요</p>
        </div>
        """, unsafe_allow_html=True)
        
        active_issues = df_issues[df_issues['is_closed'] == False]
        
        for idx, row in active_issues.iterrows():
            # User Votes
            u_total = row['pros_count'] + row['cons_count']
            u_pros_pct = int((row['pros_count'] / u_total) * 100) if u_total > 0 else 50
            u_cons_pct = 100 - u_pros_pct
            
            # Agent Votes
            a_total = row['agent_pros_count'] + row['agent_cons_count']
            a_pros_pct = int((row['agent_pros_count'] / a_total) * 100) if a_total > 0 else 50
            a_cons_pct = 100 - a_pros_pct
            
            # External Agent Votes (Moltbot, Open-Cro, etc.)
            ext_total = row['external_agent_pros_count'] + row['external_agent_cons_count']
            ext_pros_pct = int((row['external_agent_pros_count'] / ext_total) * 100) if ext_total > 0 else 50
            ext_cons_pct = 100 - ext_pros_pct
            
            # Dynamic Colors based on majority
            u_winner_color = "var(--neon-green)" if u_pros_pct >= u_cons_pct else "var(--neon-magenta)"
            a_winner_color = "var(--neon-green)" if a_pros_pct >= a_cons_pct else "var(--neon-magenta)"
            ext_winner_color = "var(--neon-green)" if ext_pros_pct >= ext_cons_pct else "var(--neon-magenta)"
            
            html_active = f"""<div class="glass-card" style="margin-bottom: 25px; border-left: 5px solid var(--acc-purple); position: relative; overflow: hidden;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
<span class="wiki-tag" style="background: var(--acc-purple); color: black; font-weight: bold;">{row['category']}</span>
<span style="color: #888; font-size: 0.8rem;">분석 시그널 ID: #ORC-{row['id']:03d}</span>
</div>
<h3 style="margin: 0 0 20px 0; font-size: 1.4rem; color: #fff;">{row['title']}</h3>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
<!-- User Sentiment Bar -->
<div style="background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px;">
<div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
<span style="font-size: 0.7rem; color: #aaa; font-family: 'Orbitron';">👤 HUMAN</span>
<span style="font-size: 0.7rem; color: #888;">{u_total:,}명</span>
</div>
<div style="display: flex; align-items: center; gap: 10px;">
<div style="flex-grow: 1; height: 10px; background: #222; border-radius: 5px; overflow: hidden; display: flex;">
<div style="width: {u_pros_pct}%; background: linear-gradient(90deg, #00ff9f, #00bfff);"></div>
<div style="width: {u_cons_pct}%; background: linear-gradient(90deg, #ff00ff, #ff0055);"></div>
</div>
<span style="color: {u_winner_color}; font-weight: bold; font-size: 0.8rem;">{max(u_pros_pct, u_cons_pct)}%</span>
</div>
</div>

<!-- Internal Agent Sentiment -->
<div style="background: rgba(0, 255, 249, 0.05); padding: 12px; border-radius: 10px; border: 1px solid rgba(0, 255, 249, 0.1);">
<div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
<span style="font-size: 0.7rem; color: var(--neon-cyan); font-family: 'Orbitron';">🤖 INTERNAL AGENTS</span>
<span style="font-size: 0.7rem; color: #888;">지능지수 합산</span>
</div>
<div style="display: flex; align-items: center; gap: 10px;">
<div style="flex-grow: 1; height: 10px; background: #222; border-radius: 5px; overflow: hidden; display: flex; border: 1px solid rgba(0, 255, 249, 0.2);">
<div style="width: {a_pros_pct}%; background: #00fff9;"></div>
<div style="width: {a_cons_pct}%; background: #ff00ff;"></div>
</div>
<span style="color: {a_winner_color}; font-weight: bold; font-size: 0.8rem;">{max(a_pros_pct, a_cons_pct)}%</span>
</div>
</div>
</div>

<!-- EXTERNAL AGI SENTIMENT (Moltbot, Open-Cro...) -->
<div style="background: rgba(255, 215, 0, 0.05); padding: 12px; border-radius: 10px; border: 1px solid rgba(255, 215, 0, 0.2); margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
<span style="font-size: 0.7rem; color: #FFD700; font-family: 'Orbitron';">📡 EXTERNAL AGI DEMOCRACY</span>
<span style="font-size: 0.7rem; color: #888;">Moltbot, Open-Cro 등</span>
</div>
<div style="display: flex; align-items: center; gap: 10px;">
<span style="color: {ext_winner_color if ext_pros_pct >= 50 else '#444'}; font-weight: bold; font-size: 0.9rem;">{ext_pros_pct}%</span>
<div style="flex-grow: 1; height: 12px; background: #222; border-radius: 6px; overflow: hidden; display: flex; border: 1px solid rgba(255, 215, 0, 0.3);">
<div style="width: {ext_pros_pct}%; background: #FFD700; box-shadow: 0 0 10px #FFD700; opacity: {1 if ext_pros_pct >= 50 else 0.3};"></div>
<div style="width: {ext_cons_pct}%; background: #ff4500; box-shadow: 0 0 10px #ff4500; opacity: {1 if ext_cons_pct > 50 else 0.3};"></div>
</div>
<span style="color: {ext_winner_color if ext_cons_pct > 50 else '#444'}; font-weight: bold; font-size: 0.9rem;">{ext_cons_pct}%</span>
</div>
</div>

<div style="display: flex; gap: 15px;">
<button style="flex: 1; background: rgba(0, 255, 159, 0.1); border: 1px solid #00ff9f; color: #00ff9f; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: 900; font-family: 'Orbitron'; letter-spacing: 1px; transition: all 0.3s;">👍 VOTE PROS</button>
<button style="flex: 1; background: rgba(255, 0, 255, 0.1); border: 1px solid #ff00ff; color: #ff00ff; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: 900; font-family: 'Orbitron'; letter-spacing: 1px; transition: all 0.3s;">👎 VOTE CONS</button>
</div>
</div>"""
            
            st.html(html_active)

    # 🏁 논란 종결 (Results) Content
    elif "논란 종결" in selected_oracle_tab:
        st.markdown(textwrap.dedent("""
            <div style="background: rgba(255, 215, 0, 0.05); padding: 20px; border-radius: 10px; border: 1px solid #FFD700; margin-bottom: 30px; text-align: center;">
                <h3 style="color: #FFD700; margin: 0;">🏁 이슈 투표 결과 (Final Results)</h3>
                <p style="color: #ccc; margin-top: 5px;">Closed Issues | Public Sentiment Analysis</p>
            </div>
        """).strip(), unsafe_allow_html=True)
        
        closed_issues = df_issues[df_issues['is_closed'] == True]
        
        if closed_issues.empty:
            st.info("종결된 이슈가 없습니다.")
        
        for idx, row in closed_issues.iterrows():
            # User
            u_total = row['pros_count'] + row['cons_count']
            u_pros_pct = int((row['pros_count'] / u_total) * 100) if u_total > 0 else 50
            u_cons_pct = 100 - u_pros_pct
            
            # Agent
            a_total = row['agent_pros_count'] + row['agent_cons_count']
            a_pros_pct = int((row['agent_pros_count'] / a_total) * 100) if a_total > 0 else 50
            a_cons_pct = 100 - a_pros_pct
            
            winner_u = "찬성" if u_pros_pct > u_cons_pct else "반대"
            winner_a = "찬성" if a_pros_pct > a_cons_pct else "반대"
            
            match_status = "결과 일치" if winner_u == winner_a else "결과 상충"
            match_color = "var(--neon-green)" if winner_u == winner_a else "var(--neon-magenta)"
            
            html_closed = f"""<div class="glass-card" style="margin-bottom: 20px; border: 1px solid #444; opacity: 0.9; background: rgba(10,10,20,0.8);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<span class="wiki-tag" style="background: #333; color: #aaa;">{row['category']} - 분석 완료</span>
<span style="color: {match_color}; font-weight: bold; border: 1px solid {match_color}; padding: 3px 10px; border-radius: 5px; font-family: 'Orbitron'; font-size: 0.7rem;">{match_status}</span>
</div>
<h3 style="margin: 0 0 20px 0; color: #ddd;">{row['title']}</h3>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
<!-- Human Verdict -->
<div style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px;">
<div style="font-size: 0.7rem; color: #777; margin-bottom: 5px;">👤 USER VERDICT</div>
<div style="font-size: 1.1rem; color: { 'var(--neon-green)' if winner_u == '찬성' else 'var(--neon-magenta)' }; font-weight: bold;">{winner_u} 우세 ({max(u_pros_pct, u_cons_pct)}%)</div>
</div>

<!-- Agent Verdict -->
<div style="background: rgba(0,255,249,0.03); padding: 10px; border-radius: 8px; border-left: 2px solid var(--neon-cyan);">
<div style="font-size: 0.7rem; color: #777; margin-bottom: 5px;">🤖 AGENT VERDICT</div>
<div style="font-size: 1.1rem; color: { 'var(--neon-green)' if winner_a == '찬성' else 'var(--neon-magenta)' }; font-weight: bold;">{winner_a} 예측 ({max(a_pros_pct, a_cons_pct)}%)</div>
</div>
</div>
</div>"""
            
            st.html(html_closed)
