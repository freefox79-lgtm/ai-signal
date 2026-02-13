import streamlit as st

def show():
    # 🎯 MOD-O 네온 헤더
    st.markdown("""
        <div style="background: rgba(157, 0, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-purple); margin-bottom: 30px;">
            <h2 style="color: var(--acc-purple); margin: 0; text-shadow: 0 0 10px var(--acc-purple);">🔮 MOD-O: 오라클 예측</h2>
            <p style="color: #888; margin: 5px 0 0 0;">섹터: 확률 마켓 | 상태: 퀀텀 싱크</p>
        </div>
    """, unsafe_allow_html=True)

    tab_market, tab_leaders = st.tabs(["📊 활성 마켓", "🏆 탑 예측자"])
    
    with tab_market:
        st.write("### 🛰️ 라이브 예측 노드")
        
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

    with tab_leaders:
        st.write("### 💎 엘리트 예측자")
        st.table([
            {"순위": "01", "사용자": "CyberShaman_99", "정확도": "96.4%", "포인트": "12,450", "트렌드": "🚀"},
            {"순위": "02", "사용자": "NeonVortex", "정확도": "89.2%", "포인트": "8,120", "트렌드": "📈"},
            {"순위": "03", "사용자": "LogicProphet", "정확도": "88.7%", "포인트": "7,900", "트렌드": "📉"},
            {"순위": "04", "사용자": "MemeGod_X", "정확도": "84.1%", "포인트": "5,300", "트렌드": "🚀"},
        ])
        
        st.divider()
        st.caption("리더보드는 GraphRAG 검증에 따라 매일 UTC 00:00에 업데이트됩니다.")
