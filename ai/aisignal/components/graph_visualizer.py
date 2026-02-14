"""
Graph Visualizer Component
Pyvis를 사용한 인터랙티브 지식 그래프 시각화
"""

from pyvis.network import Network
from typing import List, Dict
import streamlit.components.v1 as components
import tempfile
import os

class GraphVisualizer:
    """지식 그래프 시각화"""
    
    def __init__(self):
        self.net = None
    
    def create_graph(
        self,
        entities: List[Dict],
        relationships: List[Dict],
        height: str = "500px",
        width: str = "100%"
    ) -> str:
        """그래프 생성"""
        
        # Pyvis 네트워크 생성
        self.net = Network(
            height=height,
            width=width,
            bgcolor="#000000",
            font_color="#FFFFFF",
            directed=True
        )
        
        # 물리 엔진 설정 (부드러운 애니메이션)
        self.net.set_options("""
        {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -8000,
              "centralGravity": 0.3,
              "springLength": 95,
              "springConstant": 0.04,
              "damping": 0.09
            }
          },
          "nodes": {
            "font": {
              "size": 14,
              "color": "#FFFFFF"
            }
          },
          "edges": {
            "color": {
              "color": "#00D4FF",
              "highlight": "#00FF9D"
            },
            "smooth": {
              "type": "continuous"
            }
          }
        }
        """)
        
        # 노드 추가
        for entity in entities:
            color = self._get_node_color(entity.get('entity_type', 'concept'))
            self.net.add_node(
                entity['id'],
                label=entity['entity'],
                title=f"{entity['entity_type']} (유사도: {entity.get('similarity', 1.0):.2%})",
                color=color,
                size=20 + (entity.get('similarity', 1.0) * 20)
            )
        
        # 엣지 추가
        for rel in relationships:
            self.net.add_edge(
                rel['source'],
                rel['target'],
                title=rel.get('type', 'related'),
                label=rel.get('type', ''),
                width=2
            )
        
        # HTML 생성
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
            self.net.save_graph(f.name)
            with open(f.name, 'r', encoding='utf-8') as html_file:
                html_content = html_file.read()
            os.unlink(f.name)
        
        return html_content
    
    def _get_node_color(self, entity_type: str) -> str:
        """엔티티 타입별 색상"""
        colors = {
            'company': '#00D4FF',      # 파란색
            'technology': '#00FF9D',   # 녹색
            'concept': '#9D00FF',      # 보라색
            'person': '#FF9D00',       # 주황색
            'event': '#FF0099',        # 핑크색
            'auto_detected': '#888888' # 회색
        }
        return colors.get(entity_type, '#00D4FF')
    
    def render(self, html_content: str, height: int = 500):
        """Streamlit에서 렌더링"""
        components.html(html_content, height=height, scrolling=False)


# 싱글톤 인스턴스
_graph_visualizer = None

def get_graph_visualizer() -> GraphVisualizer:
    """그래프 시각화 싱글톤"""
    global _graph_visualizer
    if _graph_visualizer is None:
        _graph_visualizer = GraphVisualizer()
    return _graph_visualizer
