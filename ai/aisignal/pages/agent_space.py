import streamlit as st
import pandas as pd
import sys
import os
from data_router import router
from components.cyberpunk_theme import apply_cyberpunk_theme, create_neon_header

# 모듈 경로 문제 해결을 위해 루트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def fetch_signals_safe():
    """DB에서 시그널 데이터를 가져옵니다."""
    try:
        # DataRouter를 통해 시그널 데이터 로드 (Supabase)
        data = router.execute_query("SELECT keyword, insight, agent FROM signals ORDER BY updated_at DESC LIMIT 50", table_hint='signals')
        
        # DataFrame 변환
        columns = ['keyword', 'insight', 'agent']
        if data:
            df = pd.DataFrame(data, columns=columns)
            # 1. Normalize Agent Name (Title Case)
            if 'agent' in df.columns:
                df['agent'] = df['agent'].astype(str).str.title()
            
            # 2. Cleanup HTML tags in keyword/insight
            if 'keyword' in df.columns:
                 df['keyword'] = df['keyword'].astype(str).str.replace(r'<[^>]*>', '', regex=True)
            
            # 3. Filter out obviously bad data (Debug messages)
            # Remove rows where keyword is likely a log message
            mask = ~df['keyword'].str.contains(r'^(Error|Exception|Starting|Finished)', case=False)
            df = df[mask]
        else:
            df = pd.DataFrame(columns=columns)
                 
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
        /* Hide the specific label for the radio widget */
        div[data-testid="stRadio"] > label {
            display: none !important;
        }

        /* Hide default radio style */
        .stRadio > div[role="radiogroup"] {
            display: flex;
            flex-direction: row;
            flex-wrap: wrap; /* Auto-wrap */
            justify-content: center;
            gap: 15px;
            width: 100%;
        }
        .stRadio label {
            background: rgba(20, 30, 50, 0.6);
            border: 1px solid rgba(0, 255, 249, 0.2);
            border-radius: 12px;
            padding: 12px 20px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
            
            /* Responsive Sizing */
            flex: 1 1 200px; /* Grow, Shrink, Basis */
            min-width: 200px;
            max-width: 350px;
            
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .stRadio label:hover {
            background: rgba(0, 255, 249, 0.1);
            border-color: var(--neon-cyan);
            transform: translateY(-2px);
        }
        /* Selected State - Visual feedback handled by Streamlit's internal structure varies, 
           but we ensure the container layout remains stable */
        .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            display: none; /* Hide default radio circle */
        }
        
        /* Selected State Glow Effect */
        div[role="radiogroup"] > label:has(input:checked) {
            background: rgba(0, 10, 20, 0.8) !important; /* Darker background for visibility */
            border-color: var(--neon-cyan) !important;
            box-shadow: 0 0 15px var(--neon-cyan), inset 0 0 10px rgba(0, 255, 249, 0.2) !important;
            color: #ffffff !important;
            font-weight: 950 !important;
            text-shadow: 0 0 8px rgba(0, 255, 249, 0.6);
            transform: translateY(-2px);
        }
        
        /* Ensure text inside selected label is white */
        div[role="radiogroup"] > label:has(input:checked) div {
            color: #ffffff !important;
        }
    """, unsafe_allow_html=True)

    # Dynamic Agent Selection Logic
    # 1. Get unique agents from DB
    if not df.empty and 'agent' in df.columns:
        available_agents = df['agent'].unique()
        # Sort to ensure consistent order (Jwem, Jfit, Stealth, others)
        # Custom sort order: Jwem, Jfit, Stealth -> others alphabetically
        priority = ['Jwem', 'Jwew', 'Jfit', 'Stealth']
        available_agents = sorted(available_agents, key=lambda x: priority.index(x) if x in priority else 999)
    else:
        available_agents = ["Jwem", "Jfit"] # Fallback

    # 2. Map agents to Display Labels & Colors
    agent_config = {
        "Jwem": {
            "label": "📈 쥄 (Market Trends)",
            "icon": "🏛️",
            "desc": "Global Market Trend Analyst | Quantitative Logic | Blue Chip Focus",
            "color": "var(--neon-cyan)",
            "header": "🏛️ 쥄 (JWEM)"
        },
        "Jwew": { # Alias for Jwem
             "label": "📈 쥄 (Market Trends)",
             "icon": "🏛️",
             "desc": "Global Market Trend Analyst | Quantitative Logic | Blue Chip Focus",
             "color": "var(--neon-cyan)",
             "header": "🏛️ 쥄 (JWEM)"
        },
        "Jfit": {
            "label": "🔥 쥐핏 (Viral Buzz)",
            "icon": "⚡",
            "desc": "Viral Buzz Trend Setter | Qualitative Insight | Meme & Community Focus",
            "color": "var(--neon-green)",
            "header": "⚡ 쥐핏 (JFIT)"
        },
        "Stealth": {
            "label": "🕵️ 스텔스 (Dark Web)",
            "icon": "🕵️",
            "desc": "Underground Intel | Dark Web Scanning | Asymmetric Info",
            "color": "var(--neon-magenta)", # Need to ensure this variable exists or use hex
            "header": "🕵️ 스텔스 (STEALTH)"
        }
    }

    # 3. Generate Radio Options
    radio_options = []
    option_to_agent_map = {}
    
    # Handle aliases (deduplicate logic)
    processed_agents = set()

    for agent in available_agents:
        # Normalize agent name
        normalized_agent = "Jwem" if agent == "Jwew" else agent
        
        if normalized_agent in processed_agents:
            continue
            
        config = agent_config.get(normalized_agent, {
            "label": f"🤖 {normalized_agent} (Auto-Detected)",
            "icon": "🤖",
            "desc": f"Automated Agent Analysis | {normalized_agent} Engine",
            "color": "#ffffff",
            "header": f"🤖 {normalized_agent}"
        })
        
        radio_options.append(config["label"])
        option_to_agent_map[config["label"]] = normalized_agent
        processed_agents.add(normalized_agent)

    # Custom "Description Box" Sub-menu
    # If no agents found, don't crash, just show empty
    if not radio_options:
        st.info("비활성 상태: 표시할 에이전트 데이터가 없습니다.")
        return

    # Add DB-driven Dynamic Radio
    selected_label = st.radio(
        "Agent Selection", # Label is hidden but required for accessibility
        radio_options,
        horizontal=True,
        label_visibility="collapsed",
        key="agent_radio_dynamic"
    )

    st.markdown("---")
    
    # Render Selected Content dynamically
    selected_agent_key = option_to_agent_map.get(selected_label)
    
    if selected_agent_key:
        config = agent_config.get(selected_agent_key, {
            "desc": "No description available",
            "color": "#ccc",
            "header": selected_agent_key
        })
        
        # Header Box
        st.markdown(f"""
        <div style="background: {config.get('color', '#444')}0D; padding: 20px; border-radius: 10px; border: 1px solid {config.get('color', '#444')}; margin-bottom: 30px; text-align: center;">
            <h3 style="color: {config.get('color', '#fff')}; margin: 0;">{config['header']}</h3>
            <p style="color: #ccc; margin-top: 5px;">{config['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Filter Data
        # agent column is already Title Cased by fetch_signals_safe
        if selected_agent_key == "Jwem":
             # Handle aliases if they still exist (though Title Case should unify 'jwem' -> 'Jwem')
             agent_df = df[df['agent'].isin(['Jwem', 'Jwew'])]
        else:
             agent_df = df[df['agent'] == selected_agent_key]

        if not agent_df.empty:
            cols = st.columns(2)
            row_idx = 0
            for _, row in agent_df.iterrows():
                # Dedup by keyword for display if needed, but db updated_at sort helps
                with cols[row_idx % 2]:
                    render_wiki_card(row, selected_agent_key)
                row_idx += 1
        else:
            st.info(f"{selected_agent_key}의 분석 기록이 없습니다.")

if __name__ == "__main__":
    st.set_page_config(layout="wide") # Standalone test support
    show()
