import streamlit as st

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
        <div style="text-align: center; padding: 20px 0;">
            <h1 class="neon-text" style="color: var(--acc-green); font-size: 3rem; margin-bottom: 0;">AI SIGNAL Inc.</h1>
            <p style="color: #888; letter-spacing: 5px; font-weight: 300;">하이브리드 인텔리전스 인프라</p>
        </div>
    """, unsafe_allow_html=True)
