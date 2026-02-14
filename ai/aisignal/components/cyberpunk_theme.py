"""
네오-사이버펑크 오로라 테마

Streamlit 커스텀 CSS로 구현
Mac Mini 로컬 자원 최적화
"""

import streamlit as st

def apply_cyberpunk_theme():
    """사이버펑크 테마 적용"""
    
    st.markdown("""
    <style>
        /* ========================================
           Google Fonts Import
           ======================================== */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@300;400;700&display=swap');
        
        /* ========================================
           네오-사이버펑크 컬러 팔레트
           ======================================== */
        :root {
            /* Primary Neon Colors */
            --neon-cyan: #00fff9;
            --neon-magenta: #ff00ff;
            --neon-yellow: #ffff00;
            --neon-green: #00ff9f;
            --neon-blue: #00bfff;
            --neon-purple: #8a2be2;
            
            /* Background */
            --bg-dark: #0a0e27;
            --bg-darker: #050812;
            --bg-card: #1a1f3a;
            --bg-card-hover: #252b4a;
            
            /* Text */
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --text-neon: #00fff9;
            
            /* Accent */
            --accent-glow: rgba(0, 255, 249, 0.3);
            --accent-glow-strong: rgba(0, 255, 249, 0.6);
        }
        
        /* ========================================
           Global Styles
           ======================================== */
        .stApp {
            background: linear-gradient(
                135deg,
                var(--bg-darker) 0%,
                var(--bg-dark) 50%,
                var(--bg-darker) 100%
            );
            color: var(--text-primary);
            font-family: 'Roboto Mono', monospace;
        }
        
        /* Main content area */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* ========================================
           오로라 배경 애니메이션
           ======================================== */
        @keyframes aurora {
            0%, 100% {
                background-position: 0% 50%;
                opacity: 0.3;
            }
            50% {
                background-position: 100% 50%;
                opacity: 0.5;
            }
        }
        
        @keyframes pulse-glow {
            0%, 100% {
                box-shadow: 0 0 20px var(--accent-glow);
            }
            50% {
                box-shadow: 0 0 40px var(--accent-glow-strong);
            }
        }
        
        /* 오로라 배경 레이어 */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                45deg,
                rgba(0, 255, 249, 0.05),
                rgba(255, 0, 255, 0.05),
                rgba(0, 255, 159, 0.05),
                rgba(255, 255, 0, 0.05)
            );
            background-size: 400% 400%;
            animation: aurora 15s ease infinite;
            pointer-events: none;
            z-index: 0;
        }
        
        /* ========================================
           Typography
           ======================================== */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Orbitron', sans-serif;
            color: var(--neon-cyan);
            text-shadow: 
                0 0 10px var(--accent-glow),
                0 0 20px var(--accent-glow);
            letter-spacing: 2px;
        }
        
        h1 {
            font-size: 3rem;
            font-weight: 900;
            text-transform: uppercase;
        }
        
        /* ========================================
           Cards & Containers
           ======================================== */
        .stCard, div[data-testid="stMetricValue"] {
            background: var(--bg-card);
            border: 1px solid var(--neon-cyan);
            border-radius: 10px;
            box-shadow: 
                0 0 20px rgba(0, 255, 249, 0.2),
                inset 0 0 20px rgba(0, 255, 249, 0.05);
            padding: 20px;
            margin: 10px 0;
            transition: all 0.3s ease;
        }
        
        .stCard:hover {
            background: var(--bg-card-hover);
            box-shadow: 
                0 0 30px rgba(0, 255, 249, 0.4),
                inset 0 0 30px rgba(0, 255, 249, 0.1);
            transform: translateY(-2px);
        }
        
        /* Metric containers */
        div[data-testid="stMetricValue"] {
            font-family: 'Orbitron', sans-serif;
            color: var(--neon-green);
            font-size: 2rem;
            font-weight: 700;
        }
        
        /* ========================================
           Buttons
           ======================================== */
        .stButton > button {
            background: linear-gradient(
                135deg,
                var(--neon-cyan),
                var(--neon-magenta)
            );
            color: var(--bg-dark);
            border: none;
            border-radius: 5px;
            padding: 12px 24px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 0 20px var(--accent-glow);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 30px var(--accent-glow-strong);
            animation: pulse-glow 2s ease-in-out infinite;
        }
        
        .stButton > button:active {
            transform: translateY(-1px);
        }
        
        /* ========================================
           Input Fields
           ======================================== */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            background: var(--bg-card);
            border: 1px solid var(--neon-cyan);
            border-radius: 5px;
            color: var(--text-primary);
            font-family: 'Roboto Mono', monospace;
            padding: 10px;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--neon-magenta);
            box-shadow: 0 0 15px var(--accent-glow);
        }
        
        /* ========================================
           Data Tables
           ======================================== */
        .dataframe {
            background: var(--bg-card);
            border: 1px solid var(--neon-cyan);
            border-radius: 5px;
            font-family: 'Roboto Mono', monospace;
        }
        
        .dataframe thead tr th {
            background: linear-gradient(
                135deg,
                var(--neon-cyan),
                var(--neon-blue)
            );
            color: var(--bg-dark);
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 12px;
        }
        
        .dataframe tbody tr {
            border-bottom: 1px solid rgba(0, 255, 249, 0.1);
            transition: background 0.2s ease;
        }
        
        .dataframe tbody tr:hover {
            background: rgba(0, 255, 249, 0.05);
        }
        
        .dataframe tbody tr td {
            padding: 10px;
            color: var(--text-primary);
        }
        
        /* ========================================
           Charts (Altair/Plotly)
           ======================================== */
        .vega-embed, .js-plotly-plot {
            border: 1px solid var(--neon-cyan);
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 249, 0.2);
            background: var(--bg-card);
        }
        
        /* ========================================
           Sidebar
           ======================================== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                var(--bg-darker) 0%,
                var(--bg-dark) 100%
            );
            border-right: 2px solid var(--neon-cyan);
            box-shadow: 5px 0 20px rgba(0, 255, 249, 0.2);
        }
        
        section[data-testid="stSidebar"] .stMarkdown h1,
        section[data-testid="stSidebar"] .stMarkdown h2,
        section[data-testid="stSidebar"] .stMarkdown h3 {
            color: var(--neon-green);
        }
        
        /* ========================================
           Tabs
           ======================================== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: var(--bg-darker);
            padding: 10px;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: var(--bg-card);
            border: 1px solid var(--neon-cyan);
            border-radius: 5px;
            color: var(--text-primary);
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            padding: 10px 20px;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: var(--bg-card-hover);
            box-shadow: 0 0 15px var(--accent-glow);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(
                135deg,
                var(--neon-cyan),
                var(--neon-blue)
            );
            color: var(--bg-dark);
            box-shadow: 0 0 20px var(--accent-glow-strong);
        }
        
        /* ========================================
           Expander
           ======================================== */
        .streamlit-expanderHeader {
            background: var(--bg-card);
            border: 1px solid var(--neon-cyan);
            border-radius: 5px;
            color: var(--neon-cyan);
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
        }
        
        .streamlit-expanderHeader:hover {
            background: var(--bg-card-hover);
            box-shadow: 0 0 15px var(--accent-glow);
        }
        
        /* ========================================
           Progress Bar
           ======================================== */
        .stProgress > div > div > div > div {
            background: linear-gradient(
                90deg,
                var(--neon-cyan),
                var(--neon-magenta)
            );
            box-shadow: 0 0 15px var(--accent-glow);
        }
        
        /* ========================================
           Alerts
           ======================================== */
        .stAlert {
            background: var(--bg-card);
            border-left: 4px solid var(--neon-cyan);
            border-radius: 5px;
            box-shadow: 0 0 15px rgba(0, 255, 249, 0.2);
        }
        
        /* ========================================
           Scrollbar
           ======================================== */
        ::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-darker);
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(
                180deg,
                var(--neon-cyan),
                var(--neon-magenta)
            );
            border-radius: 6px;
            box-shadow: 0 0 10px var(--accent-glow);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            box-shadow: 0 0 20px var(--accent-glow-strong);
        }
        
        /* ========================================
           Custom Classes
           ======================================== */
        .neon-text {
            color: var(--neon-cyan);
            text-shadow: 
                0 0 10px var(--accent-glow),
                0 0 20px var(--accent-glow),
                0 0 30px var(--accent-glow);
        }
        
        .glow-box {
            background: var(--bg-card);
            border: 2px solid var(--neon-cyan);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 
                0 0 30px rgba(0, 255, 249, 0.3),
                inset 0 0 30px rgba(0, 255, 249, 0.1);
            animation: pulse-glow 3s ease-in-out infinite;
        }
        
        .cyber-badge {
            display: inline-block;
            background: linear-gradient(
                135deg,
                var(--neon-cyan),
                var(--neon-magenta)
            );
            color: var(--bg-dark);
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            font-size: 0.8rem;
            padding: 4px 12px;
            border-radius: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 0 15px var(--accent-glow);
        }
    </style>
    """, unsafe_allow_html=True)


def create_neon_header(title: str, subtitle: str = None):
    """네온 헤더 생성"""
    html = f'<h1 class="neon-text">{title}</h1>'
    if subtitle:
        html += f'<p style="color: var(--text-secondary); font-size: 1.2rem; margin-top: -10px;">{subtitle}</p>'
    
    st.markdown(html, unsafe_allow_html=True)


def create_glow_box(content: str):
    """글로우 박스 생성"""
    st.markdown(f'<div class="glow-box">{content}</div>', unsafe_allow_html=True)


def create_cyber_badge(text: str):
    """사이버 배지 생성"""
    return f'<span class="cyber-badge">{text}</span>'
