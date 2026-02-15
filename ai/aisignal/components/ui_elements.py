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
        <div class="fixed-header">
            <h1 class="neon-text" style="color: var(--acc-green); font-size: 2.8rem; margin-bottom: 0; filter: drop-shadow(0 0 10px var(--acc-green));">AI SIGNAL Inc.</h1>
            <p style="color: #666; letter-spacing: 8px; font-weight: 300; text-transform: uppercase; font-family: 'Orbitron', sans-serif; font-size: 0.75rem; margin-top: -8px;">Hybrid Intelligence Infrastructure</p>
        </div>
        <div class="header-spacer"></div>
    """, unsafe_allow_html=True)
