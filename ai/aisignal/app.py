import streamlit as st
import os
from dotenv import load_dotenv
from components.ui_elements import render_header
from components.cyberpunk_theme import apply_cyberpunk_theme
from pages import home, intelligence, oracle, wiki, dashboard

# 🎯 Environment Setup
load_dotenv()

# 🎯 Page Config & Custom CSS
st.set_page_config(
    page_title="AI SIGNAL Inc.", 
    page_icon="🛰️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🌌 네오-사이버펑크 오로라 테마 적용
apply_cyberpunk_theme()

# 🛰️ Header Implementation
render_header()

# 🧭 네비게이션 시스템 (5개 탭 구조)
tab_home, tab_intel, tab_oracle, tab_wiki, tab_dash = st.tabs([
    "🏠 홈", 
    "🧠 인텔리전스", 
    "🔮 오라클", 
    "🌐 위키", 
    "📊 대시보드"
])

with tab_home:
    home.show()

with tab_intel:
    intelligence.show()

with tab_oracle:
    oracle.show()

with tab_wiki:
    wiki.show()

with tab_dash:
    dashboard.show()

#  footer
st.markdown("---")
st.caption("AI SIGNAL Inc. | Powering Autonomous Data Sources | [Antigravity System]")