import streamlit as st
import pandas as pd
import sys
import os

# 모듈 경로 문제 해결을 위해 루트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db_utils import get_db_connection

# 페이지 설정 (Deprecated: integrated into app.py)
# st.set_page_config(
#     page_title="Agent Space | AI SIGNAL",
#     page_icon="🧠",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# CSS 로드
# CSS 로드
try:
    from components.cyberpunk_theme import apply_cyberpunk_theme, create_neon_header
    apply_cyberpunk_theme()
except ImportError as e:
    st.error(f"테마 로드 실패: {e}")
    # Fallback functions
    def apply_cyberpunk_theme(): pass
    def create_neon_header(title, subtitle=None):
        st.title(title)
        if subtitle: st.caption(subtitle)

def render_header_inline():
    st.markdown("""
        <div class="fixed-header">
            <h1 class="neon-text" style="color: var(--acc-green); font-size: 2.8rem; margin-bottom: 0; filter: drop-shadow(0 0 10px var(--acc-green));">AI SIGNAL INC.</h1>
            <p style="color: #666; letter-spacing: 8px; font-weight: 300; text-transform: uppercase; font-family: 'Orbitron', sans-serif; font-size: 0.75rem; margin-top: -8px;">Hybrid Intelligence Infrastructure</p>
        </div>
        <div class="header-spacer"></div>
    """, unsafe_allow_html=True)

def fetch_signals_safe():
    """DB에서 시그널 데이터를 가져옵니다."""
    try:
        conn = get_db_connection()
        # 강제 Mock Mode (UI 검증용)
        mock_mode = True
        
        with conn.cursor() as cur:
            cur.execute("SELECT keyword, insight, agent FROM signals ORDER BY updated_at DESC LIMIT 50")
            data = cur.fetchall()
            
            # Mock Data Column Definition
            columns = ['keyword', 'insight', 'agent']
            
            # DataFrame 변환
            if data:
                df = pd.DataFrame(data, columns=columns)
            else:
                 df = pd.DataFrame(columns=columns)
                 
        conn.close()
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

# CSS 커스텀 (Wiki Card 스타일)
st.markdown("""
<style>
    /* Wiki Card Style */
    .wiki-card {
        background: rgba(15, 20, 30, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .wiki-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border-color: var(--card-border-color, #444);
    }
    .wiki-card h3 {
        margin-top: 0;
        font-size: 1.2rem;
        font-weight: 700;
        color: #fff;
    }
    .wiki-card-meta {
        font-size: 0.8rem;
        color: #888;
        margin-bottom: 10px;
    }
    .wiki-tag {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        margin-right: 5px;
        background: rgba(255, 255, 255, 0.1);
        color: #ccc;
    }
    
    /* Persona Colors */
    .jwem-card {
        --card-border-color: var(--neon-cyan);
    }
    .jwem-card h3 {
        color: var(--neon-cyan);
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.3);
    }
    
    .jfit-card {
        --card-border-color: var(--neon-green);
    }
    .jfit-card h3 {
        color: var(--neon-green);
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def render_wiki_card(row, agent_type):
    """위키 카드 렌더링"""
    card_class = "jwem-card" if agent_type == "Jwem" else "jfit-card"
    icon = "📈" if agent_type == "Jwem" else "🔥"
    
    st.markdown(f"""
    <div class="wiki-card {card_class}">
        <div class="wiki-card-meta">{icon} Analyst: {agent_type}</div>
        <h3>{row['keyword']}</h3>
        <p style="color: #ccc; font-size: 0.95rem; line-height: 1.5;">{row['insight']}</p>
        <div style="margin-top: 15px;">
            <span class="wiki-tag">#Signal</span>
            <span class="wiki-tag">#Analysis</span>
            <span class="wiki-tag">#{agent_type}Pick</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 상세 분석 보기"):
        st.markdown(f"**키워드 정의**:")
        st.write(f"{row['keyword']}에 대한 심층 분석 데이터가 여기에 표시됩니다.")
        st.markdown(f"**관련 소스**:")
        st.code("Bloomberg, Reuters, Twitter API, Reddit", language="text")
        st.markdown(f"**투자/트렌드 점수**:")
        st.progress(85 if agent_type == "Jwem" else 72)

def show():
    # 헤더 (Integrated: App.py renders global header)
    # render_header_inline() 
    create_neon_header("AGENT SPACE", "지식 아카이브 및 페르소나별 인사이트")
    
    # 데이터 로드
    df = fetch_signals_safe()
    
    if df.empty:
        st.warning("데이터가 없습니다. DB 연결 상태를 확인하세요.")
        return

    # Sub-tab Navigation (Radio as Description Boxes)
    st.markdown("""
    <style>
        /* Hide default radio style */
        .stRadio > div {
            flex-direction: row;
            justify-content: center;
            gap: 20px;
        }
        .stRadio label {
            background: rgba(20, 30, 50, 0.6);
            border: 1px solid rgba(0, 255, 249, 0.2);
            border-radius: 15px;
            padding: 15px 30px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            width: 300px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .stRadio label:hover {
            background: rgba(0, 255, 249, 0.1);
            border-color: var(--neon-cyan);
            transform: translateY(-2px);
        }
        /* Selected State */
        .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            display: none; /* Hide default radio circle */
        }
        
        /* Custom Selected Highlight via Text Color/Border logic is handled by Streamlit's internal classes which are hard to override purely by CSS without :has(). 
           Instead, we trust the visual distinction or add more specific hacks if needed. 
           For now, we use a general card style. */
           
    </style>
    """, unsafe_allow_html=True)

    # Custom "Description Box" Sub-menu
    selected_agent = st.radio(
        "Agent Selection",
        ["📈 쥄 (Market Trends)", "🔥 쥐핏 (Viral Buzz)"],
        horizontal=True,
        label_visibility="collapsed",
        key="agent_radio"
    )

    st.markdown("---")

    # 쥄 (Jwem) Content
    if "쥄" in selected_agent:
        st.markdown("""
        <div style="background: rgba(0, 242, 255, 0.05); padding: 20px; border-radius: 10px; border: 1px solid var(--neon-cyan); margin-bottom: 30px; text-align: center;">
            <h3 style="color: var(--neon-cyan); margin: 0;">🏛️ 쥄 (JWEM)</h3>
            <p style="color: #ccc; margin-top: 5px;">Global Market Trend Analyst | Quantitative Logic | Blue Chip Focus</p>
        </div>
        """, unsafe_allow_html=True)
        
        jwem_df = df[df['agent'].astype(str).str.lower().isin(['jwem', 'jwew'])]
        
        if not jwem_df.empty:
            cols = st.columns(2)
            for idx, row in jwem_df.reset_index().iterrows():
                with cols[idx % 2]:
                    with st.container():
                        render_wiki_card(row, "Jwem")
        else:
            st.info("쥄의 기록이 없습니다.")

    # 쥐핏 (Jfit) Content
    elif "쥐핏" in selected_agent:
        st.markdown("""
        <div style="background: rgba(57, 255, 20, 0.05); padding: 20px; border-radius: 10px; border: 1px solid var(--neon-green); margin-bottom: 30px; text-align: center;">
            <h3 style="color: var(--neon-green); margin: 0;">⚡ 쥐핏 (JFIT)</h3>
            <p style="color: #ccc; margin-top: 5px;">Viral Buzz Trend Setter | Qualitative Insight | Meme & Community Focus</p>
        </div>
        """, unsafe_allow_html=True)
        
        jfit_df = df[df['agent'].astype(str).str.lower() == 'jfit']
        
        if not jfit_df.empty:
            cols = st.columns(2)
            for idx, row in jfit_df.reset_index().iterrows():
                with cols[idx % 2]:
                    with st.container():
                        render_wiki_card(row, "Jfit")
        else:
            st.info("쥐핏의 기록이 없습니다.")

if __name__ == "__main__":
    st.set_page_config(layout="wide") # Standalone test support
    show()
