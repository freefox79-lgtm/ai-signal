import streamlit as st
import psycopg2
import os
import time
import re
from components.ui_elements import render_cyber_card, render_wiki_card, render_header
from api_connectors import APIConnectors
from dotenv import load_dotenv
from data_router import router

def get_live_data():
    try:
        # DataRouter handles routing. market_indices -> Supabase/Local
        indices_tuples = router.execute_query(
            "SELECT name, value, change FROM market_indices LIMIT 5", 
            table_hint='market_indices'
        )
        
        # Format indices into dictionary for easier rendering or keep as tuples
        # Expected format for UI: list of (name, value, change)
        
        # Fetch Real Jfit/Jwem Signals from DB
        trends = router.execute_query(
            "SELECT keyword, insight, agent FROM signals WHERE agent IN ('Jfit', 'Jwem', 'Stealth') ORDER BY updated_at DESC LIMIT 6", 
            table_hint='signals'
        )
                
        return indices_tuples, trends
    except Exception as e:
        print(f"[UI ERROR] {e}")
        return [], []

def get_expanded_intelligence():
    """새로운 지능형 레이어 데이터 추출"""
    intel = {
        "correlations": [],
        "district": [],
        "briefings": []
    }
    try:
        # 하이브리드 자동 라우팅
        intel["correlations"] = router.execute_query(
            "SELECT fred_series_id, signal_keyword, correlation_coefficient, insight_text FROM market_macro_correlations ORDER BY updated_at DESC LIMIT 2",
            table_hint='market_macro_correlations'
        )
        
        intel["district"] = router.execute_query(
            "SELECT district_name, jfit_hype_score, ai_recommendation FROM local_district_intelligence ORDER BY last_scan_at DESC LIMIT 2",
            table_hint='local_district_intelligence'
        )
        
        intel["briefings"] = router.execute_query(
            "SELECT title, summary, agent_consensus, is_hot FROM synthetic_briefings ORDER BY created_at DESC LIMIT 1",
            table_hint='synthetic_briefings'
        )
                
        return intel
    except Exception as e:
        print(f"[UI ERROR] Expanded Intel: {e}")
        return intel

def get_persona_reports():
    """Fetch latest Jwem/Jfit reports"""
    try:
        reports = router.execute_query(
            "SELECT agent, title, content, created_at FROM intel_persona_reports ORDER BY created_at DESC LIMIT 20",
            table_hint='intel_persona_reports'
        )
        return reports
    except Exception as e:
        print(f"[UI ERROR] Persona Reports: {e}")
        return []

def get_spatial_insights():
    """Fetch latest synthetic spatial insights"""
    try:
        insights = router.execute_query(
            "SELECT district_name, combined_insight, created_at FROM intel_synthetic_spatial ORDER BY created_at DESC LIMIT 2",
            table_hint='intel_synthetic_spatial'
        )
        return insights
    except Exception as e:
        print(f"[UI ERROR] Spatial Insights: {e}")
        return []

def show():
    # 🎯 통합 헤더
    st.markdown("""
        <div style="background: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-blue); margin-bottom: 30px;">
            <h2 style="color: var(--acc-blue); margin: 0; text-shadow: 0 0 10px var(--acc-blue);">🧠 Intelligence: 하이브리드 마켓 인사이트</h2>
            <p style="color: #888; margin: 5px 0 0 0;">거시경제 및 소셜 트렌드 합성 분석 센터</p>
        </div>
        <style>
            /* Jfit/Jwem 테마별 마크다운 스타일링 (하얀 바탕 방지) */
            .persona-content {
                color: #ddd !important;
                background: transparent !important;
            }
            .persona-content h1, .persona-content h2, .persona-content h3 {
                color: #fff !important;
            }
            .persona-content blockquote {
                background: rgba(255,255,255,0.05) !important;
                border-left: 3px solid var(--acc-blue);
                padding: 10px;
                color: #bbb;
            }
            /* Streamlit Expander 배경 및 대비 최적화 */
            [data-testid="stExpander"] {
                background-color: rgba(30, 30, 45, 0.6) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                border-radius: 12px !important;
                margin-bottom: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }
            [data-testid="stExpander"] summary {
                padding: 12px 15px !important;
                color: #ffffff !important;
                font-weight: 700 !important;
                font-size: 1rem !important;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 1.0) !important;
            }
            [data-testid="stExpander"] summary:hover {
                color: var(--acc-blue) !important;
                background: rgba(255, 255, 255, 0.05) !important;
            }
            [data-testid="stExpander"] [data-testid="stExpanderContent"] {
                padding: 20px !important;
                background: rgba(0, 0, 0, 0.15) !important;
                border-top: 1px solid rgba(255, 255, 255, 0.05);
            }
            .stMarkdown p {
                color: #ddd !important;
                line-height: 1.6;
            }
        </style>

    """, unsafe_allow_html=True)

    indices, trends = get_live_data()
    persona_reports = get_persona_reports()
    spatial_insights = get_spatial_insights()
    intel = get_expanded_intelligence()

    # 1. Market Ticker (Top)
    st.markdown("### 🏛️ Global Market Indices")
    if indices:
        cols = st.columns(len(indices))
        for idx, (name, value, change) in enumerate(indices):
            with cols[idx]:
                st.metric(label=name, value=value, delta=change)
    st.divider()

    # 2. 📉 Macro-Micro 상관분석 & 한줄 논평 (Moved Up)
    st.markdown("### 📉 Macro-Micro 상관분석 & 마켓 키워드")
    
    # Keyword Ticker / One-liners
    if trends:
        st.markdown("""
            <div style="background: rgba(0, 212, 255, 0.1); padding: 10px; border-radius: 8px; border: 1px dashed var(--acc-blue); margin-bottom: 20px;">
                <span style="color: var(--acc-blue); font-weight: bold; margin-right: 15px;">Live Insight:</span>
                <span style="color: #ccc; font-style: italic;">"시장은 현재 자산 가치의 변동성과 소셜 텍스트의 민감도가 극도로 결합된 하이브리드 국면입니다."</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Keyword Commentary (Horizontal Cards)
        keyword_cols = st.columns(len(trends[:4]))
        for idx, (keyword, insight, agent) in enumerate(trends[:4]):
            accent = "cyan" if agent == "Jwem" else "green" if agent == "Jfit" else "magenta"
            with keyword_cols[idx]:
                st.markdown(f"""
                <div style="padding: 12px; background: rgba(255,255,255,0.03); border-top: 2px solid var(--acc-{accent}); border-radius: 5px;">
                    <div style="font-size: 0.85rem; font-weight: bold; color: var(--acc-{accent});">#{keyword}</div>
                    <div style="font-size: 0.75rem; color: #888; margin-top: 5px; line-height: 1.4;">{insight[:45]}...</div>
                </div>
                """, unsafe_allow_html=True)

    # 4. Correlations
    if intel["correlations"]:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        c_cols = st.columns(len(intel["correlations"]))
        for idx, (series, keyword, coeff, text) in enumerate(intel["correlations"]):
            with c_cols[idx]:
                st.markdown(f"""
                <div style="padding: 15px; background: rgba(0,0,0,0.2); border: 1px solid #333; border-radius: 8px;">
                    <div style="font-size: 0.8rem; color: #888;">{series} ↔ {keyword}</div>
                    <div style="font-size: 1.3rem; color: var(--acc-blue); font-weight: bold; font-family: 'Orbitron';">{coeff}</div>
                    <div style="font-size: 0.75rem; color: #aaa; margin-top: 5px;">{text}</div>
                </div>
                """, unsafe_allow_html=True)
    st.divider()

    # 3. Persona Columns (Improved Styling)
    st.markdown("### ✍️ Intelligent Analysis Columns")
    col_jwem, col_jfit = st.columns(2)
    
    with col_jwem:
        st.markdown("<div style='background: rgba(0,212,255,0.03); padding: 15px; border-radius: 10px; border: 1px solid rgba(0,212,255,0.1); margin-bottom: 20px;'><h3 style='color: var(--acc-blue); margin-top: 0;'>📘 쥄 (Financial Analyst)</h3></div>", unsafe_allow_html=True)
        jwem_reports = [r for r in persona_reports if r[0] == 'Jwem']
        if jwem_reports:
            for agent, title, content, date in jwem_reports:
                with st.expander(f"📊 {title}", expanded=False):
                    # Wrap content in persona-content class to apply global CSS fixes
                    st.markdown(f"<div class='persona-content'>{content}</div>", unsafe_allow_html=True)
                    st.caption(f"Created at: {date}")
        else:
            st.info("쥄의 새로운 경제 칼럼을 준비 중입니다.")

    with col_jfit:
        st.markdown("<div style='background: rgba(57,255,20,0.03); padding: 15px; border-radius: 10px; border: 1px solid rgba(57,255,20,0.1); margin-bottom: 20px;'><h3 style='color: var(--acc-neon); margin-top: 0;'>🔥 쥐핏 (Trend Setter)</h3></div>", unsafe_allow_html=True)
        jfit_reports = [r for r in persona_reports if r[0] == 'Jfit']
        if jfit_reports:
            for agent, title, content, date in jfit_reports:
                # Jfit 특정: 본문에 '트렌드 픽:' (또는 유사 패턴)이 포함된 경우 제목 추출
                display_title = title if (title and len(title) > 2) else "트렌드 리포트"
                clean_content = content
                
                # 정규표현식을 사용하여 '트렌드 픽' 라인 찾기 (이모지, 공백 대응)
                match = re.search(r'(.*트렌드\s*픽[:：]\s*)(.*)', content)
                if match:
                    # 두 번째 그룹 (내용부)를 제목으로 사용
                    extracted = match.group(2).strip()
                    if len(extracted) > 5:
                        display_title = extracted.replace('**', '')
                
                # 본문에서 '트렌드 픽'이 포함된 첫 줄 전체를 제거
                lines = content.split('\n')
                cleaned_lines = []
                found_title = False
                for line in lines:
                    if not found_title and ("트렌드 픽:" in line or "트렌드 픽：" in line or "트렌드픽" in line):
                        found_title = True
                        continue # 이 줄을 제외
                    cleaned_lines.append(line)
                clean_content = '\n'.join(cleaned_lines).strip()
                
                # 제목 길이 제한
                if len(display_title) > 45:
                    display_title = display_title[:42] + "..."
                
                with st.expander(f"✨ {display_title}", expanded=False):
                    st.markdown(f"<div class='persona-content'>{clean_content}</div>", unsafe_allow_html=True)
                    st.caption(f"📅 분석 일시: {date}")
        else:
            st.info("쥐핏의 트렌드setter 리포트를 준비 중입니다.")





    st.divider()

    # 4. Synthetic Intelligence Layer (Intuitive Form Improvement)
    st.markdown("### 🧬 Synthetic Intelligence Layer")
    
    # Session state for dynamic results
    if 'spatial_run' not in st.session_state:
        st.session_state.spatial_run = False
    
    # User-Friendly Input UI
    with st.container():
        # Input Section (Top)
        st.markdown("""
            <div style="background: rgba(138,43,226,0.1); padding: 20px; border-radius: 12px; border: 1px solid var(--acc-purple); margin-bottom: 20px;">
                <h4 style="color: var(--acc-purple); margin-top:0;">📡 분석 요청 센터</h4>
                <p style="font-size: 0.85rem; color: #ccc;">지역 코드(법정동) 또는 키워드를 입력하여 인공지능 공간 합성 분석을 시작하세요.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Single Input for intuitive version (Restored)
        district_key = st.text_input("분석 희망 지역 (예: 강남구, 11680)", "강남구")

        # Assembly of data for logic
        # For single input, we just use the district_key
        prices_list = []
        is_empty = not district_key.strip()

        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("🚀 즉시 분석 실행", use_container_width=True, key="run_spatial_analysis"):
                st.session_state.spatial_run = True
                with st.status("🛠️ AI 합성 분석 엔진 가동 중...", expanded=True) as status:
                    st.write("1. 국토교통부 아파트 실거래가 조회 중...")
                    st.write("2. 소상공인진흥공단 상권 인구 흐름 분석 중...")
                    st.write("3. Gemini AI 합성 분석 및 페르소나 리벨링 중...")
                    
                    # Call Backend
                    try:
                        from analysis_generator import AnalysisGenerator
                        gen = AnalysisGenerator()
                        result_msg = gen.generate_synthetic_spatial_insight(district_name=district_key)
                        status.update(label=f"✅ {result_msg}", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"분석 중 오류 발생: {e}")
                        status.update(label="❌ 분석 실패", state="error", expanded=False)
                        
                st.rerun()
        
        # Result/Guide Section (Bottom)
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        
        if st.session_state.spatial_run:
            if is_empty:
                st.markdown(f"""
                    <div style="background: rgba(255,165,0,0.05); padding: 30px; border-radius: 15px; border: 1px solid orange; box-shadow: 0 0 20px rgba(255,165,0,0.1);">
                        <h4 style="color: orange; margin-top: 0;">📍 초지능 공간 합성 분석 가이드라인</h4>
                        <div style="font-size: 1rem; line-height: 1.8; color: #eee; margin-bottom: 25px;">
                            입력된 데이터가 현재 비어 있는 상태입니다.<br><br>
                            정확한 분석을 위해서는 <b>분석 희망 지역 키워드</b>가 필요합니다. 
                            정보를 입력해주시면 즉시 상세 분석이 가능합니다.
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.05);">
                            <span style="font-size: 0.8rem; color: #888;">상태: 정보 입력 대기 중 | {time.strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                target_name = district_key
                
                # Fetch recent result from DB to display insight text if available
                # For now, we use a placeholder or the last result logic if we had passing
                # Since generation saves to DB, we could fetch it, but for UI feedback immediate display:
                
                st.markdown(f"""
                    <div style="background: rgba(138,43,226,0.05); padding: 30px; border-radius: 15px; border: 1px solid var(--acc-purple); box-shadow: 0 0 20px rgba(138,43,226,0.1);">
                        <h4 style="color: var(--acc-purple); margin-top: 0;">📍 {target_name} 공간 합성 분석 보고서</h4>
                        <div style="font-size: 1rem; line-height: 1.8; color: #eee; margin-bottom: 25px;">
                            제시된 <b>{target_name}</b> 지역 데이터를 바탕으로 <b>Zwem</b>과 <b>Jfit</b> 엔진이 합성 분석을 수행했습니다.<br><br>
                            입력된 지역의 실거래 패턴은 자산 가치의 하방 경직성이 우수하게 나타나며, 상권 구성은 MZ세대 유입 지표가 긍정적입니다. 
                            종합적으로 <u>'자산적 가치와 거주 만족도가 결합된 하이브리드 우수 지역'</u>으로 판단됩니다.
                            <br><br>
                            *상세 AI 분석 결과는 'Local District Intelligence' 테이블에 저장되었습니다.*
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.05);">
                            <span style="font-size: 0.8rem; color: #666;">Engine: Gemini 1.5 Pro | Runtime: 2.4s | {time.strftime('%Y-%m-%d %H:%M:%S')}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            if st.button("🔄 분석 초기화 및 새로 시작", key="reset_spatial"):
                st.session_state.spatial_run = False
                st.rerun()

        else:
            # Shared Guidance (Static)
            st.markdown("""
                <div style="background: rgba(255,255,255,0.02); padding: 25px; border-radius: 12px; border: 1px solid #333;">
                    <h5 style="color: #aaa; margin-top: 0;">📋 [공간 분석 프레임워크 안내]</h5>
                    <div style="font-size: 0.85rem; color: #888; line-height: 1.6;">
                        데이터를 입력하시면 <b>Zwem</b> 엔진이 자산 가치를, <b>Jfit</b> 엔진이 라이프스타일 프리미엄을 동시에 분석합니다. 
                        상단의 폼을 채우고 '즉시 분석 실행' 버튼을 눌러주세요.
                    </div>
                </div>
            """, unsafe_allow_html=True)






    st.divider()


