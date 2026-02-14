"""
Agent State Schema for LangGraph Workflow

Defines the shared state structure that flows through all agent nodes.
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage
import operator
from datetime import datetime


class AgentState(TypedDict):
    """
    Shared state for LangGraph agent workflow.
    
    This state is passed between all nodes in the graph and accumulates
    information as it flows through the workflow.
    """
    
    # Input
    query: str
    """User's original query/request"""
    
    category: Literal["TREND", "FINANCE", "MEME", "GENERAL"]
    """Signal category for routing decisions"""
    
    # Agent outputs
    jfit_trends: list[dict]
    """Trends discovered by Jfit agent"""
    
    jwem_analysis: dict
    """Financial/logic analysis from Jwem agent"""
    
    # Workflow control
    messages: Annotated[Sequence[BaseMessage], operator.add]
    """Message history (accumulated via operator.add)"""
    
    next_agent: str
    """Next agent to route to (used by conditional edges)"""
    
    iteration_count: int
    """Current iteration number (for cycle detection)"""
    
    max_iterations: int
    """Maximum allowed iterations (default: 3)"""
    
    # Results
    final_signals: list[dict]
    """Combined insights from all agents"""
    
    confidence_score: float
    """Overall confidence in the results (0.0 - 1.0)"""
    
    # Metadata
    timestamp: str
    """ISO format timestamp of when processing started"""
    
    error: str | None
    """Error message if any step failed"""
    
    # Cross-validation fields
    fact_check_results: list[dict]
    """Jwem's fact check results for Jfit's trends"""
    
    jwem_analysis_enhanced: dict
    """Jfit's dopamine-injected version of Jwem's analysis"""
    
    final_report: dict
    """Consensus report from both agents"""
    
    validation_complete: bool
    """Whether cross-validation is complete"""
    
    consensus_score: float
    """Agreement level between agents (0.0 - 1.0)"""
