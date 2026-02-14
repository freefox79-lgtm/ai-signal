import streamlit as st
from agents.graphrag.knowledge_graph import KnowledgeGraph
from agents.graphrag.hyperlink_generator import HyperlinkGenerator
from components.graph_visualizer import GraphVisualizer
import traceback

def show():
    # Initialize
    try:
        kg = KnowledgeGraph()
        hg = HyperlinkGenerator()
        gv = GraphVisualizer()
    except Exception as e:
        st.error(f"GraphRAG 초기화 실패: {e}")
        st.info("데이터베이스 연결을 확인하세요.")
        return
    
    # 🎯 MOD-W 네온 헤더
    st.markdown("""
        <div style="background: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-blue); margin-bottom: 30px;">
            <h2 style="color: var(--acc-blue); margin: 0; text-shadow: 0 0 10px var(--acc-blue);">🌐 MOD-W: GRAPHRAG 지식 지도</h2>
            <p style="color: #888; margin: 5px 0 0 0;">섹터: 지식 합성 | 상태: 활성화</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 📊 그래프 통계
    try:
        stats = kg.get_graph_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("노드", f"{stats.get('node_count', 0):,}")
        with col2:
            st.metric("엣지", f"{stats.get('edge_count', 0):,}")
        with col3:
            st.metric("엔티티 타입", f"{stats.get('type_count', 0):,}")
    except Exception as e:
        st.warning(f"통계 로드 실패: {e}")
    
    st.divider()
    
    # 🔍 노드 검색
    st.markdown("### 🔍 지식 노드 검색")
    query = st.text_input("", placeholder="검색할 노드를 입력하세요 (예: '반도체', 'SK 하이닉스')...", label_visibility="collapsed")
    
    if query:
        with st.spinner("검색 중..."):
            try:
                # 관련 엔티티 검색
                results = kg.find_related_entities(query, top_k=10, threshold=0.5)
                
                if results:
                    st.success(f"**{len(results)}개**의 관련 노드를 찾았습니다.")
                    
                    # 검색 결과 표시
                    for i, entity in enumerate(results, 1):
                        with st.expander(f"{i}. **{entity['entity']}** ({entity['entity_type']}) - 유사도: {entity['similarity']:.2%}"):
                            st.write(f"**타입**: {entity['entity_type']}")
                            st.write(f"**유사도**: {entity['similarity']:.2%}")
                            if entity.get('metadata'):
                                st.json(entity['metadata'])
                    
                    # 그래프 시각화
                    st.markdown("### 🕸️ 관계 그래프")
                    try:
                        # 관계 가져오기
                        relationships = kg.get_entity_relationships(query, max_depth=1)
                        
                        # 그래프 생성
                        html_content = gv.create_graph(results[:5], relationships)
                        gv.render(html_content, height=500)
                    except Exception as e:
                        st.warning(f"그래프 시각화 실패: {e}")
                        st.info("관계 데이터가 부족합니다.")
                else:
                    st.info("검색 결과가 없습니다. 다른 키워드를 시도해보세요.")
            except Exception as e:
                st.error(f"검색 실패: {e}")
                st.code(traceback.format_exc())
    else:
        # 플레이스홀더 그래프
        st.markdown("""
            <div class="glass-card" style="height: 500px; position: relative; overflow: hidden; border: 1px dashed var(--acc-blue); background: radial-gradient(circle, rgba(0,212,255,0.05) 0%, rgba(0,0,0,1) 100%);">
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                    <h2 style="color: var(--acc-blue); opacity: 0.5; letter-spacing: 10px;" class="neon-text">검색어를 입력하세요</h2>
                    <p style="color: #555;">[ 지식 그래프 시각화 대기 중 ]</p>
                </div>
                <!-- 목 노드 -->
                <div style="position: absolute; top: 20%; left: 30%; width: 10px; height: 10px; background: var(--acc-blue); border-radius: 50%; box-shadow: 0 0 10px var(--acc-blue);"></div>
                <div style="position: absolute; top: 60%; left: 70%; width: 10px; height: 10px; background: var(--acc-green); border-radius: 50%; box-shadow: 0 0 10px var(--acc-green);"></div>
                <div style="position: absolute; top: 40%; left: 50%; width: 15px; height: 15px; background: var(--acc-purple); border-radius: 50%; box-shadow: 0 0 15px var(--acc-purple);"></div>
            </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # 📚 최근 합성 데이터
    st.write("### 📖 최근 지식 합성 내역")
    
    try:
        recent_entities = kg.get_recent_entities(limit=4)
        
        if recent_entities:
            cols = st.columns(2)
            for i, entity in enumerate(recent_entities):
                with cols[i % 2]:
                    st.markdown(f"""
                        <div class="glass-card">
                            <h5 style="color: var(--acc-green);">[노드] {entity['entity']}</h5>
                            <p style="font-size: 0.9rem; color: #888;">타입: {entity['entity_type']} | 생성: {entity.get('created_at', 'N/A')}</p>
                            <p>{entity.get('metadata', {}).get('description', '설명 없음')}</p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            # 플레이스홀더
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("""
                    <div class="glass-card">
                        <h5 style="color: var(--acc-green);">[노드 싱크] HBM3e 제조 공정</h5>
                        <p style="font-size: 0.9rem; color: #888;">합성 시간: 2시간 전 | 신뢰도: 94%</p>
                        <p>SK 하이닉스 수율과 엔비디아 B200 타임라인 간의 연결 관계가 수립되었습니다. 시장 영향: 치명적.</p>
                    </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown("""
                    <div class="glass-card">
                        <h5 style="color: var(--acc-blue);">[이벤트 GRAG] 미국 대선 변동성</h5>
                        <p style="font-size: 0.9rem; color: #888;">합성 시간: 5시간 전 | 신뢰도: 82%</p>
                        <p>경합 주 정서와 친환경 에너지 주식 선물 간의 상관관계가 매핑되었습니다. 권장 조치: 헤지.</p>
                    </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"최근 데이터 로드 실패: {e}")
