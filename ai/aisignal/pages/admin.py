"""
관리자 대시보드 - 확장성 모니터링
"""

import streamlit as st
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scaling_monitor import ScalingMonitor
from components.cyberpunk_theme import apply_cyberpunk_theme


def render_admin_page():
    """관리자 페이지 렌더링"""
    
    # Cyberpunk 테마 적용
    apply_cyberpunk_theme()
    
    st.title("🔧 관리자 대시보드")
    st.markdown("---")
    
    # 확장성 모니터링
    st.header("📊 확장성 모니터링")
    
    monitor = ScalingMonitor()
    
    # 현재 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = monitor.get_system_metrics()
    
    with col1:
        st.metric(
            "사용자 수",
            f"{metrics['users']:,}명",
            delta=None
        )
    
    with col2:
        cpu_color = "🟢" if metrics['cpu_percent'] < 70 else "🟡" if metrics['cpu_percent'] < 85 else "🔴"
        st.metric(
            "CPU 사용률",
            f"{cpu_color} {metrics['cpu_percent']:.1f}%"
        )
    
    with col3:
        mem_color = "🟢" if metrics['memory_percent'] < 70 else "🟡" if metrics['memory_percent'] < 85 else "🔴"
        st.metric(
            "메모리 사용률",
            f"{mem_color} {metrics['memory_percent']:.1f}%"
        )
    
    with col4:
        st.metric(
            "현재 단계",
            monitor.current_stage.upper()
        )
    
    st.markdown("---")
    
    # 확장 제안
    st.header("🎯 확장 제안")
    
    recommendations = monitor.check_scaling_needs()
    
    if not recommendations:
        st.success("✅ 현재 인프라로 충분합니다!")
    else:
        for rec in recommendations:
            level_color = {
                "warning": "warning",
                "critical": "error",
                "urgent": "error"
            }
            
            with st.expander(f"{rec.title} ({rec.level.upper()})", expanded=True):
                st.markdown(f"**설명**: {rec.description}")
                st.markdown(f"**예상 비용**: {rec.estimated_cost}")
                st.markdown(f"**타임라인**: {rec.timeline}")
                
                st.markdown("**권장 조치**:")
                for action in rec.actions:
                    st.markdown(f"- {action}")
    
    st.markdown("---")
    
    # 보고서 생성
    if st.button("📄 보고서 생성", type="primary"):
        report = monitor.generate_report()
        st.download_button(
            label="📥 보고서 다운로드",
            data=report,
            file_name=f"scaling_report_{metrics['timestamp']}.md",
            mime="text/markdown"
        )
        st.success("보고서가 생성되었습니다!")
    
    # 자동 모니터링 설정
    st.markdown("---")
    st.header("⚙️ 자동 모니터링 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        auto_monitor = st.checkbox("자동 모니터링 활성화", value=True)
        if auto_monitor:
            st.info("📊 1시간마다 자동으로 메트릭을 수집합니다.")
    
    with col2:
        alert_email = st.text_input("알림 이메일", placeholder="admin@aisignal.com")
        if alert_email:
            st.success(f"✉️ {alert_email}로 알림을 전송합니다.")


if __name__ == "__main__":
    render_admin_page()
