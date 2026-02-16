import streamlit as st
import streamlit.components.v1 as components

def render_cyber_card(title, content, category="green"):
    st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid var(--acc-{category});">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: #fff;">{title}</h4>
                <span class="neon-badge badge-{category}">시그널</span>
            </div>
            <p style="margin-top: 10px; color: #ccc;">{content}</p>
        </div>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown("""
        <div class="fixed-header">
            <h1 class="neon-text" style="color: var(--acc-green); font-size: 2.8rem; margin-bottom: 0; filter: drop-shadow(0 0 10px var(--acc-green));">AI SIGNAL Inc.</h1>
            <p style="color: #666; letter-spacing: 8px; font-weight: 300; text-transform: uppercase; font-family: 'Orbitron', sans-serif; font-size: 0.75rem; margin-top: -8px;">Hybrid Intelligence Infrastructure</p>
        </div>
        <div class="header-spacer"></div>
    """, unsafe_allow_html=True)

def render_wiki_card(title, content, agent_type="Jwem", detailed=False):
    """
    Standardized Wiki Card for Agent Space & Intelligence Page
    """
    # CSS injection for ensuring styles exist if not already applied
    st.markdown("""
    <style>
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
        .jwem-card { --card-border-color: var(--neon-cyan); }
        .jwem-card h3 { color: var(--neon-cyan); text-shadow: 0 0 10px rgba(0, 242, 255, 0.3); }
        .jfit-card { --card-border-color: var(--neon-green); }
        .jfit-card h3 { color: var(--neon-green); text-shadow: 0 0 10px rgba(57, 255, 20, 0.3); }
        .stealth-card { --card-border-color: var(--neon-magenta); }
        .stealth-card h3 { color: var(--neon-magenta); text-shadow: 0 0 10px rgba(255, 0, 230, 0.3); }
    </style>
    """, unsafe_allow_html=True)

    card_class = "jwem-card"
    icon = "📈"
    
    if agent_type == "Jfit":
        card_class = "jfit-card"
        icon = "🔥"
    elif agent_type == "Stealth":
        card_class = "stealth-card"
        icon = "🕵️"
    
    st.markdown(f"""
    <div class="wiki-card {card_class}">
        <div class="wiki-card-meta">{icon} Analyst: {agent_type}</div>
        <h3>{title}</h3>
        <p style="color: #ccc; font-size: 0.95rem; line-height: 1.5;">{content}</p>
        <div style="margin-top: 15px;">
            <span class="wiki-tag">#Signal</span>
            <span class="wiki-tag">#Analysis</span>
            <span class="wiki-tag">#{agent_type}Pick</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if detailed:
        with st.expander("🔍 상세 분석 보기"):
            st.markdown(f"**키워드 정의**:")
            st.write(f"{title}에 대한 심층 분석 데이터가 여기에 표시됩니다.")
            st.markdown(f"**투자/트렌드 점수**:")
            st.progress(80)
