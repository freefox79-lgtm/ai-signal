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
            bgcolor="#050505", # 더 어두운 배경
            font_color="#FFFFFF",
            directed=True
        )
        
        # 물리 엔진 설정 (Hierarchical Layout for Flow)
        self.net.set_options("""
        {
          "physics": {
            "enabled": true,
            "hierarchicalRepulsion": {
              "centralGravity": 0.0,
              "springLength": 150,
              "springConstant": 0.01,
              "nodeDistance": 200,
              "damping": 0.09
            },
            "solver": "hierarchicalRepulsion"
          },
          "layout": {
             "hierarchical": {
                "enabled": false,
                "levelSeparation": 150,
                "direction": "LR",
                "sortMethod": "directed"
             }
          },
          "nodes": {
            "font": {
              "size": 16,
              "color": "#FFFFFF",
              "face": "tahoma"
            },
            "borderWidth": 2,
            "shadow": true
          },
          "edges": {
            "color": {
              "color": "#00D4FF",
              "highlight": "#00FF9D",
              "opacity": 0.8
            },
            "smooth": {
              "type": "curvedCW",
              "roundness": 0.2
            },
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 1.2
              }
            }
          }
        }
        """)
        
        # 노드 추가
        for entity in entities:
            # 1. Credibility Check
            credibility = entity.get('metadata', {}).get('credibility', 100)
            
            # 2. Color Logic
            if credibility < 30:
                color = "#FF0055" # Red (Danger)
            elif credibility < 70:
                color = "#FFD700" # Yellow (Warning)
            else:
                color = self._get_node_color(entity.get('entity_type', 'concept'))
            
            # 3. Origin Logic (is_origin flag in metadata)
            is_origin = entity.get('metadata', {}).get('is_origin', False)
            shape = "star" if is_origin else "dot"
            size = 40 if is_origin else (20 + (entity.get('similarity', 1.0) * 10))
            if is_origin:
                color = "#FF4500" # OrangeRed for Origin
                
            self.net.add_node(
                entity['id'],
                label=entity['entity'],
                title=f"""
                {entity['entity_type']}
                Credibility: {credibility}%
                Platform: {entity.get('metadata', {}).get('platform', 'Unknown')}
                """,
                color=color,
                size=size,
                shape=shape,
                borderWidth=4 if is_origin else 1,
                borderWidthSelected=6
            )
        
        # 엣지 추가
        for rel in relationships:
            self.net.add_edge(
                rel['source'],
                rel['target'],
                title=f"{rel.get('type', 'related')} (Time: {rel.get('timestamp', 'N/A')})",
                label=rel.get('type', ''),
                width=3
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
            'company': '#00D4FF',      # Blue
            'technology': '#00FF9D',   # Neon Green
            'concept': '#9D00FF',      # Purple
            'person': '#FF9D00',       # Orange
            'event': '#FF0099',        # Pink
            'platform': '#888888',     # Grey
            'auto_detected': '#555555' 
        }
        return colors.get(entity_type, '#00D4FF')
    
    def render(self, html_content: str, height: int = 600):
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
