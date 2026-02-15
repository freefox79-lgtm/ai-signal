import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# 모듈 경로 문제 해결을 위해 루트 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.graphrag.knowledge_graph import KnowledgeGraph
from agents.graphrag.hyperlink_generator import HyperlinkGenerator
from components.graph_visualizer import GraphVisualizer
from db_utils import get_db_connection
import traceback

def get_origin_data():
    """DB에서 이슈 확산 데이터를 가져옵니다."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # MockCursor는 query에 'origin_tracking'이 포함되면 데이터를 반환함
            cur.execute("SELECT * FROM origin_tracking") 
            data = cur.fetchall()
            return data
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return []

def show():
    # GraphRAG 컴포넌트 초기화
    try:
        gv = GraphVisualizer()
    except Exception as e:
        st.error(f"GraphRAG 초기화 실패: {e}")
        return
    
    # 🎯 이슈근원지 네온 헤더
    st.markdown("""
        <div style="background: rgba(0, 212, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--acc-blue); margin-bottom: 30px;">
            <h2 style="color: var(--acc-blue); margin: 0; text-shadow: 0 0 10px var(--acc-blue);">🔍 이슈근원지: GraphRAG 지식 아카이브</h2>
            <p style="color: #888; margin: 5px 0 0 0;">데이터 소스 관계 맵핑 및 엔티티 추적 시스템 | 상태: 활성화</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 🔍 노드 검색 (Origin Tracking Focus)
    st.markdown("### 🔍 이슈 키워드 추적")
    # Default query to show the mock data scenario
    c1, c2 = st.columns([4, 1], gap="small", vertical_alignment="bottom")
    with c1:
        query_input = st.text_input("", value="딥페이크 유포 경로", placeholder="추적할 이슈 키워드를 입력하세요...", label_visibility="collapsed")
    with c2:
        st.markdown("""
        <style>
        div.stButton > button:first-child {
            width: 100%;
            height: 46px; /* Match standard input height */
            background: linear-gradient(90deg, #ff0055 0%, #ff5500 100%);
            color: white;
            border: none;
            font-weight: bold;
            font-size: 1.1rem;
            box-shadow: 0 0 15px rgba(255, 0, 85, 0.5);
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(255, 0, 85, 0.8);
            border: 1px solid white;
        }
        </style>
        """, unsafe_allow_html=True)
        search_click = st.button("🚀 추적 실행", type="primary", use_container_width=True)

    query = query_input if query_input else ""
    
    if query:
        with st.spinner(f"'{query}'의 근원지를 추적 중입니다..."):
            
            # 1. 데이터 가져오기
            raw_data = get_origin_data()
            
            if not raw_data:
                st.warning("추적할 데이터가 없습니다.")
                return

            # 2. 데이터 가공 (Nodes & Edges)
            nodes = {}
            edges = []
            
            # 타임스탬프 파싱 및 노드/엣지 구성
            for row in raw_data:
                # row: (id, source, target, type, confidence, timestamp, metadata)
                source = row[1]
                target = row[2]
                rel_type = row[3]
                timestamp = row[5]
                metadata = row[6]
                
                # Source Node
                if source not in nodes:
                    nodes[source] = {
                        "id": source, 
                        "entity": source, 
                        "entity_type": "person" if "User" in source else ("platform" if "Web" in source else "social"), 
                        "metadata": metadata, # contains credibility
                        "first_seen": timestamp
                    }
                else:
                    # Update earliest time if needed
                    if timestamp < nodes[source]["first_seen"]:
                        nodes[source]["first_seen"] = timestamp

                # Target Node (Metadata might be missing for target in this simple structure, so infer or set default)
                if target not in nodes:
                    # Simple inference for mock
                    t_type = "person" if "Influencer" in target else ("platform" if "Web" in target or "Media" in target else "community")
                    t_cred = 50 
                    if "Media" in target: t_cred = 95
                    elif "Web" in target: t_cred = 80
                    elif "Community" in target: t_cred = 40
                    
                    nodes[target] = {
                        "id": target, 
                        "entity": target, 
                        "entity_type": t_type, 
                        "metadata": {"credibility": t_cred, "platform": "Unknown"},
                        "first_seen": timestamp 
                    }
                
                edges.append({
                    "source": source,
                    "target": target,
                    "type": rel_type,
                    "timestamp": timestamp
                })

            # 3. Origin Identification (Earliest Timestamp)
            sorted_nodes = sorted(nodes.values(), key=lambda x: x['first_seen'])
            if sorted_nodes:
                origin_node = sorted_nodes[0]
                origin_node['metadata']['is_origin'] = True
                
                # Origin Display
                st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid #FF4500; margin-bottom: 20px;">
                    <h3 style="color: #FF4500; margin: 0;">🚨 최초 발원지 식별됨 (Origin Detected)</h3>
                    <div style="display: flex; justify-content: space-between; align_items: center; margin-top: 10px;">
                        <div>
                            <p style="font-size: 1.2rem; font-weight: bold; margin: 0;">{origin_node['entity']}</p>
                            <p style="color: #888; margin: 0;">발견 시각: {origin_node['first_seen']}</p>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 0.9rem; color: #888;">신뢰도 점수 (Credibility)</span>
                            <h2 style="margin: 0; color: #FF0055;">{origin_node['metadata']['credibility']}% (위험)</h2>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 4. Graph Visualization
            node_list = list(nodes.values())
            try:
                html_content = gv.create_graph(node_list, edges, height="600px")
                gv.render(html_content, height=600)
            except Exception as e:
                st.error(f"시각화 오류: {e}")

            # 5. Timeline View (Diffusion Log)
            st.markdown("### ⏱️ 확산 타임라인 (Diffusion Timeline)")
            sorted_edges = sorted(edges, key=lambda x: x['timestamp'])
            
            for edge in sorted_edges:
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px; padding: 10px; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                    <div style="width: 150px; color: #aaa; font-size: 0.9rem;">{edge['timestamp'].split('T')[1]}</div>
                    <div style="flex-grow: 1;">
                        <span style="color: var(--acc-blue); font-weight: bold;">{edge['source']}</span>
                        <span style="margin: 0 10px; color: #555;">➡️</span>
                        <span style="color: #ccc;">{edge['type']}</span>
                        <span style="margin: 0 10px; color: #555;">➡️</span>
                        <span style="color: var(--acc-green); font-weight: bold;">{edge['target']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    else:
        # Default Placeholder
        st.info("좌측 상단의 검색창에 추적할 키워드를 입력하세요.")

