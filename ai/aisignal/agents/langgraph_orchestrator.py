"""
LangGraph-based Agent Orchestrator

Main orchestrator using LangGraph for state-based agent workflow.
Replaces the sequential pipeline with a conditional graph.
"""

from langgraph.graph import StateGraph, END
from agents.agent_state import AgentState
from agents.langgraph_nodes import AgentNodes
from agents.langgraph_router import (
    route_by_category,
    should_continue_to_jwem,
    should_continue_to_jfit
)
from datetime import datetime
from langchain_core.messages import HumanMessage


class LangGraphOrchestrator:
    """LangGraph-based agent orchestrator with conditional routing"""
    
    def __init__(self):
        self.nodes = AgentNodes()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """
        Build the agent workflow graph
        
        Returns:
            Compiled LangGraph workflow
        """
        print("[LANGGRAPH] Building agent workflow graph...")
        
        # Initialize graph with AgentState
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("jfit", self.nodes.jfit_node)
        workflow.add_node("jwem", self.nodes.jwem_node)
        workflow.add_node("combine", self.nodes.combine_node)
        
        # Set entry point with conditional routing
        workflow.set_conditional_entry_point(
            route_by_category,
            {
                "jfit": "jfit",
                "jwem": "jwem",
                "both": "jfit"  # Start with Jfit for "both"
            }
        )
        
        # Add conditional edges from Jfit
        workflow.add_conditional_edges(
            "jfit",
            should_continue_to_jwem,
            {
                "jwem": "jwem",
                "combine": "combine"
            }
        )
        
        # Add conditional edges from Jwem
        workflow.add_conditional_edges(
            "jwem",
            should_continue_to_jfit,
            {
                "jfit": "jfit",
                "combine": "combine"
            }
        )
        
        # Combine always ends
        workflow.add_edge("combine", END)
        
        # Compile graph
        compiled_graph = workflow.compile()
        
        print("[LANGGRAPH] Graph compiled successfully")
        return compiled_graph
    
    def process_signal(self, query: str, category: str = "GENERAL", max_iterations: int = 3):
        """
        Process signal request through LangGraph workflow
        
        Args:
            query: User query/request
            category: Signal category (TREND, FINANCE, MEME, GENERAL)
            max_iterations: Maximum iterations to prevent infinite loops
            
        Returns:
            Final state with combined signals
        """
        print(f"\n[LANGGRAPH] Processing signal: '{query}' (category: {category})")
        
        # Initialize state
        initial_state: AgentState = {
            "query": query,
            "category": category,
            "jfit_trends": [],
            "jwem_analysis": {},
            "messages": [HumanMessage(content=query)],
            "next_agent": "",
            "iteration_count": 0,
            "max_iterations": max_iterations,
            "final_signals": [],
            "confidence_score": 0.0,
            "timestamp": datetime.now().isoformat(),
            "error": None
        }
        
        # Run graph
        try:
            result = self.graph.invoke(initial_state)
            
            print(f"\n[LANGGRAPH] Workflow complete:")
            print(f"  - Iterations: {result.get('iteration_count', 0)}")
            print(f"  - Final signals: {len(result.get('final_signals', []))}")
            print(f"  - Confidence: {result.get('confidence_score', 0):.1%}")
            print(f"  - Error: {result.get('error', 'None')}")
            
            return result
            
        except Exception as e:
            print(f"[LANGGRAPH ERROR] Workflow failed: {e}")
            initial_state['error'] = str(e)
            return initial_state
    
    def visualize_graph(self, output_path="agent_workflow.png"):
        """
        Generate graph visualization
        
        Args:
            output_path: Path to save visualization
        """
        try:
            # Try to generate mermaid diagram
            mermaid_code = self.graph.get_graph().draw_mermaid()
            print(f"\n[LANGGRAPH] Mermaid diagram:\n{mermaid_code}")
            
            # Try to save as PNG (requires graphviz)
            try:
                from IPython.display import Image, display
                png_data = self.graph.get_graph().draw_mermaid_png()
                
                with open(output_path, 'wb') as f:
                    f.write(png_data)
                
                print(f"[LANGGRAPH] Graph saved to {output_path}")
                
            except ImportError:
                print("[LANGGRAPH] Install IPython and graphviz for PNG export")
                print("  brew install graphviz")
                print("  pip install ipython")
                
        except Exception as e:
            print(f"[LANGGRAPH] Visualization failed: {e}")


# Example usage
if __name__ == "__main__":
    # Test the orchestrator
    orch = LangGraphOrchestrator()
    
    # Test 1: Trend query (should route to Jfit only)
    print("\n" + "="*60)
    print("TEST 1: Trend Query")
    print("="*60)
    result1 = orch.process_signal("최신 K-Meme 트렌드", category="TREND")
    print(f"Result: {len(result1['final_signals'])} signals")
    
    # Test 2: Finance query (should route to Jwem, then maybe Jfit)
    print("\n" + "="*60)
    print("TEST 2: Finance Query")
    print("="*60)
    result2 = orch.process_signal("비트코인 가격 분석", category="FINANCE")
    print(f"Result: {len(result2['final_signals'])} signals")
    
    # Test 3: General query (should route to both)
    print("\n" + "="*60)
    print("TEST 3: General Query")
    print("="*60)
    result3 = orch.process_signal("AI Signal 주식 트렌드", category="GENERAL")
    print(f"Result: {len(result3['final_signals'])} signals")
    
    # Visualize graph
    print("\n" + "="*60)
    print("GRAPH VISUALIZATION")
    print("="*60)
    orch.visualize_graph()
