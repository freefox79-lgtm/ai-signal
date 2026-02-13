import streamlit as st
from components.ui_elements import render_cyber_card

def show():
    # 🎯 MOD-T 네온 헤더
    st.markdown("""
        <div style="background: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-blue); margin-bottom: 30px;">
            <h2 style="color: var(--acc-blue); margin: 0; text-shadow: 0 0 10px var(--acc-blue);">🧠 MOD-T: 트윈 인텔리전스 분석</h2>
            <p style="color: #888; margin: 5px 0 0 0;">페르소나: 쥄 (로고스) & 쥐핏 (파토스) | 상태: 동기화됨</p>
        </div>
    """, unsafe_allow_html=True)

    # 🚀 분할 뷰 설정
    col_jwem, col_jfit = st.columns(2)
    
    with col_jwem:
        st.markdown("""
            <div style='background: rgba(0, 212, 255, 0.1); padding: 10px; border-radius: 10px; border-bottom: 2px solid var(--acc-blue); margin-bottom: 20px;'>
                <h3 style='color: var(--acc-blue); margin: 0;'>📘 쥄: 논리적 깊이</h3>
            </div>
        """, unsafe_allow_html=True)
        
        render_cyber_card("글로벌 매크로 분석", "미 국채 수익률 상승 중. 기술주 밸류에이션 모델에 미치는 영향은 5% 조정 리스크를 시사합니다.", "blue")
        render_cyber_card("알고리즘 시그널", "코스피 200 지수가 345.2에서 강력한 피보나치 지지를 보이고 있습니다. 분할 매수를 권장합니다.", "blue")
        render_cyber_card("공급망 노드", "TSMC 2nm 수율이 80% 이상으로 보고되었습니다. 차세대 가전제품에 낙관적입니다.", "blue")

    with col_jfit:
        st.markdown("""
            <div style='background: rgba(57, 255, 20, 0.1); padding: 10px; border-radius: 10px; border-bottom: 2px solid var(--acc-neon); margin-bottom: 20px;'>
                <h3 style='color: var(--acc-neon); margin: 0;'>🔥 쥐핏: 하이프 & 바이럴</h3>
            </div>
        """, unsafe_allow_html=True)
        
        render_cyber_card("S-Tier 밈 경보", "동남아시아에서 고양이 테마 토큰 트렌딩 중. 1시간 만에 거래량 450% 증가! 탑승할래 아니면 계속 가난할래? ㅋㅋㅋ", "green")
        render_cyber_card("바이럴 패션 싱크", "나이키와 사이버펑크 2077 콜라보 루머. 리셀 시장 벌써 후끈함! 렛츠기릿!", "green")
        render_cyber_card("숏폼 메타", "틱톡에서 15초짜리 AI 생성 댄스 영상이 새로운 노다지임. 가즈아~!", "green")

    st.divider()
    
    # 🎯 크로스 페르소나 합성
    st.markdown("### 🧬 하이브리드 합성 리포트")
    st.markdown("""
        <div class="glass-card" style="border: 1px solid var(--acc-purple);">
            <p style="color: var(--acc-purple); font-weight: bold;">[로고스 + 파토스 수렴]</p>
            <p>쥄은 기술적 타당성을 확인했고, 쥐핏은 바이럴 잠재력을 확인했습니다. 섹터: <b>AI 기반 엔터테인먼트</b>. 
            권장 사항: 인프라 노드 강력 매수, 개별 토큰은 신중한 진입 권장.</p>
        </div>
    """, unsafe_allow_html=True)
