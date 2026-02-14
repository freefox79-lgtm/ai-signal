"""
나무위키식 하이퍼링크 생성

[[엔티티]] 형식으로 자동 링크 생성
GraphRAG 지식 그래프와 연동
"""

import re
from typing import List, Dict
from agents.graphrag.knowledge_graph import get_knowledge_graph
from agents.llm.ollama_client import get_ollama_client

class HyperlinkGenerator:
    """하이퍼링크 생성기"""
    
    def __init__(self):
        self.kg = get_knowledge_graph()
        self.ollama = get_ollama_client()
    
    def extract_entities(self, text: str) -> List[str]:
        """텍스트에서 엔티티 추출 (Ollama NER)"""
        
        prompt = f"""다음 텍스트에서 중요한 엔티티(인물, 기업, 기술, 개념 등)를 추출하세요.
각 엔티티를 쉼표로 구분하여 나열하세요. 엔티티만 출력하고 다른 설명은 하지 마세요.

텍스트: {text}

엔티티:"""
        
        response = self.ollama.generate(prompt, model="mistral:7b", temperature=0.3)
        
        # 엔티티 파싱
        entities = [e.strip() for e in response.split(',') if e.strip()]
        return entities[:10]  # 최대 10개
    
    def generate_hyperlinks(
        self, 
        text: str, 
        auto_link: bool = True,
        create_missing: bool = True
    ) -> str:
        """하이퍼링크 생성"""
        
        if auto_link:
            # 자동 엔티티 추출
            entities = self.extract_entities(text)
        else:
            # 기존 [[엔티티]] 패턴 추출
            entities = re.findall(r'\[\[([^\]]+)\]\]', text)
        
        # 각 엔티티를 하이퍼링크로 변환
        for entity in entities:
            # 지식 그래프에서 엔티티 확인
            related = self.kg.find_related_entities(entity, top_k=1, threshold=0.9)
            
            if related and related[0]['similarity'] > 0.9:
                # 엔티티가 존재하면 파란 링크 생성
                link = f'<a href="/wiki/{entity}" class="wiki-link" title="{related[0]["entity_type"]}">[[{entity}]]</a>'
            else:
                if create_missing:
                    # 엔티티가 없으면 지식 그래프에 추가
                    self.kg.add_entity(entity, entity_type="auto_detected")
                
                # 빨간 링크 (미작성 문서)
                link = f'<a href="/wiki/{entity}" class="wiki-link-red" title="문서 없음">[[{entity}]]</a>'
            
            # 텍스트에서 엔티티를 링크로 교체 (첫 번째 발생만)
            text = text.replace(entity, link, 1)
        
        return text
    
    def generate_related_links(
        self, 
        entity: str, 
        max_links: int = 5
    ) -> List[Dict]:
        """관련 문서 링크 생성"""
        
        related = self.kg.find_related_entities(entity, top_k=max_links)
        
        links = []
        for item in related:
            links.append({
                'entity': item['entity'],
                'type': item['entity_type'],
                'similarity': item['similarity'],
                'url': f"/wiki/{item['entity']}"
            })
        
        return links
    
    def generate_backlinks(self, entity: str) -> List[str]:
        """역링크 생성 (이 문서를 참조하는 문서들)"""
        
        # 관계 그래프에서 역방향 링크 조회
        graph = self.kg.get_entity_graph(entity, max_depth=1)
        
        backlinks = []
        for edge in graph['edges']:
            if edge['target'] == entity:
                backlinks.append(edge['source'])
        
        return backlinks
    
    def generate_toc(self, text: str) -> str:
        """목차 생성 (나무위키 스타일)"""
        
        # 헤딩 추출
        headings = re.findall(r'^(#{1,6})\s+(.+)$', text, re.MULTILINE)
        
        if not headings:
            return ""
        
        toc = ['<div class="toc">', '<h2>목차</h2>', '<ul>']
        
        for level, title in headings:
            depth = len(level)
            anchor = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-')
            
            indent = '  ' * (depth - 1)
            toc.append(f'{indent}<li><a href="#{anchor}">{title}</a></li>')
        
        toc.append('</ul>')
        toc.append('</div>')
        
        return '\n'.join(toc)


# 싱글톤 인스턴스
_hyperlink_generator = None

def get_hyperlink_generator() -> HyperlinkGenerator:
    """하이퍼링크 생성기 싱글톤"""
    global _hyperlink_generator
    if _hyperlink_generator is None:
        _hyperlink_generator = HyperlinkGenerator()
    return _hyperlink_generator
