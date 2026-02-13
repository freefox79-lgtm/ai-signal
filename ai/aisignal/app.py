import streamlit as st
import os
from dotenv import load_dotenv
from components.ui_elements import render_header
from pages import home, intelligence, oracle, wiki, dashboard

# 🎯 Environment Setup
load_dotenv()

# 🎯 Page Config & Custom CSS
st.set_page_config(
    page_title="AI SIGNAL v4.0", 
    page_icon="🛰️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles/cyberpunk.css")

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
st.caption("AI SIGNAL v4.0 | Powering Autonomous Data Sources | [Antigravity System]")