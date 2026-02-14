"""GraphRAG module initialization"""

from agents.graphrag.knowledge_graph import KnowledgeGraph, get_knowledge_graph
from agents.graphrag.hyperlink_generator import HyperlinkGenerator, get_hyperlink_generator

__all__ = [
    'KnowledgeGraph',
    'get_knowledge_graph',
    'HyperlinkGenerator',
    'get_hyperlink_generator'
]
