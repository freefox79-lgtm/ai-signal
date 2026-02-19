import streamlit as st
# force deploy 2026-02-18 22:25 (Golden Ratio V2.5)
import os
from dotenv import load_dotenv
from components.ui_elements import render_header
from components.cyberpunk_theme import apply_cyberpunk_theme
from pages import home, agent_space, oracle, wiki, dashboard, intelligence

# 🎯 Environment Setup
load_dotenv()

# 🎯 Page Config & Custom CSS
st.set_page_config(
    page_title="AI SIGNAL Inc.", 
    page_icon="🛰️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cache Busting Hash: REL_FINAL_SYNC_20260219
st.markdown(f"<!-- version: REL_FINAL_SYNC -->", unsafe_allow_html=True)

# 🌌 네오-사이버펑크 오로라 테마 적용
apply_cyberpunk_theme()

# 🛰️ Header Implementation
render_header()


# 🧭 네비게이션 시스템 (6개 탭 구조)
tab_home, tab_intel, tab_agent, tab_oracle, tab_wiki, tab_dash = st.tabs([
    "🏠 홈", 
    "🧠 지능형분석",
    "🤖 에이전트스페이스", 
    "🔥 핫이슈", 
    "🔍 이슈근원지", 
    "📈 회사현황"
])

with tab_home:
    home.show()

with tab_intel:
    intelligence.show()

with tab_agent:
    agent_space.show()

with tab_oracle:
    oracle.show()

with tab_wiki:
    wiki.show()

with tab_dash:
    dashboard.show()

#  footer
st.markdown("---")
st.caption("AI SIGNAL Inc. | Powering Autonomous Data Sources | [freefox System]")