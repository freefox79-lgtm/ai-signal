import streamlit as st

def show():
    # 🎯 핫이슈 네온 헤더
    st.markdown("""
        <div style="background: rgba(157, 0, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-purple); margin-bottom: 30px;">
            <h2 style="color: var(--acc-purple); margin: 0; text-shadow: 0 0 10px var(--acc-purple);">🔥 핫이슈: 지능형 시장 신호와 예측</h2>
            <p style="color: #888; margin: 5px 0 0 0;">실시간 고위험/고수익 시그널 및 미래 예측 데이터 분석 | 상태: 퀀텀 싱크</p>
        </div>
    """, unsafe_allow_html=True)

    # Sub-tab Navigation (Radio as Description Boxes)
    st.markdown("""
    <style>
        /* Hide default radio style */
        .stRadio > div {
            flex-direction: row;
            justify-content: center;
            gap: 20px;
        }
        .stRadio label {
            background: rgba(30, 20, 50, 0.6);
            border: 1px solid rgba(157, 0, 255, 0.3);
            border-radius: 15px;
            padding: 15px 30px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            width: 300px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .stRadio label:hover {
            background: rgba(157, 0, 255, 0.1);
            border-color: var(--acc-purple);
            transform: translateY(-2px);
        }
        /* Selected State */
        .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            display: none; /* Hide default radio circle */
        }
    </style>
    """, unsafe_allow_html=True)

    # Custom "Description Box" Sub-menu
    selected_oracle_tab = st.radio(
        "Oracle Section Selection",
        ["📊 활성 마켓 (Active Market)", "🏆 탑 예측자 (Elite Predictors)"],
        horizontal=True,
        label_visibility="collapsed",
        key="oracle_radio"
    )

    st.markdown("---")
    
    # 📊 활성 마켓 (Market) Content
    if "활성 마켓" in selected_oracle_tab:
        st.markdown("""
        <div style="background: rgba(157, 0, 255, 0.05); padding: 20px; border-radius: 10px; border: 1px solid var(--acc-purple); margin-bottom: 30px; text-align: center;">
            <h3 style="color: var(--acc-purple); margin: 0;">🛰️ 라이브 예측 노드 (Live Nodes)</h3>
            <p style="color: #ccc; margin-top: 5px;">High Risk/Reward Signals | Real-time Market Prediction</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 마켓 카드 1
        st.markdown("""
            <div class="glass-card" style="border-left: 4px solid var(--acc-green);">
                <div style="display: flex; justify-content: space-between;">
                    <h4 style="margin:0;">AI 에이전트가 2026년까지 웹 트래픽의 50%를 점유할까요?</h4>
                    <span class="neon-badge badge-green">HOT</span>
                </div>
                <p style="color: #888; margin: 10px 0;">확률: <b>68.4%</b> | 총 거래량: <b>42.5K SIGNAL</b></p>
                <div style="display: flex; gap: 10px;">
                    <button style="flex:1; background: var(--acc-green); color: black; border:none; padding: 10px; border-radius: 5px; font-weight: bold; cursor: pointer;">BET YES</button>
                    <button style="flex:1; background: rgba(255, 255, 255, 0.1); color: white; border:1px solid #444; padding: 10px; border-radius: 5px; cursor: pointer;">BET NO</button>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 마켓 카드 2
        st.markdown("""
            <div class="glass-card" style="border-left: 4px solid var(--acc-blue); margin-top: 20px;">
                <div style="display: flex; justify-content: space-between;">
                    <h4 style="margin:0;">미 연준이 2026년 3월에 금리를 인하할까요?</h4>
                    <span class="neon-badge badge-blue">매크로</span>
                </div>
                <p style="color: #888; margin: 10px 0;">확률: <b>32.1%</b> | 총 거래량: <b>128K SIGNAL</b></p>
                <div style="display: flex; gap: 10px;">
                    <button style="flex:1; background: rgba(255, 255, 255, 0.1); color: white; border:1px solid #444; padding: 10px; border-radius: 5px; cursor: pointer;">BET YES</button>
                    <button style="flex:1; background: var(--acc-blue); color: black; border:none; padding: 10px; border-radius: 5px; font-weight: bold; cursor: pointer;">BET NO</button>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 🏆 탑 예측자 (Leaders) Content
    elif "탑 예측자" in selected_oracle_tab:
        st.markdown("""
        <div style="background: rgba(255, 215, 0, 0.05); padding: 20px; border-radius: 10px; border: 1px solid #FFD700; margin-bottom: 30px; text-align: center;">
            <h3 style="color: #FFD700; margin: 0;">💎 엘리트 예측자 (Elite Predictors)</h3>
            <p style="color: #ccc; margin-top: 5px;">Top Accuracy Rankers | Reputation Leaderboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.table([
            {"순위": "01", "사용자": "CyberShaman_99", "정확도": "96.4%", "포인트": "12,450", "트렌드": "🚀"},
            {"순위": "02", "사용자": "NeonVortex", "정확도": "89.2%", "포인트": "8,120", "트렌드": "📈"},
            {"순위": "03", "사용자": "LogicProphet", "정확도": "88.7%", "포인트": "7,900", "트렌드": "📉"},
            {"순위": "04", "사용자": "MemeGod_X", "정확도": "84.1%", "포인트": "5,300", "트렌드": "🚀"},
        ])
        
        st.divider()
        st.caption("리더보드는 GraphRAG 검증에 따라 매일 UTC 00:00에 업데이트됩니다.")
