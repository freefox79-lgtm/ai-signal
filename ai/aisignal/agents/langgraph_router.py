"""
Routing Logic for LangGraph Agent Workflow

Defines conditional routing functions that determine which agent to execute next.
"""

from agents.agent_state import AgentState


def route_by_category(state: AgentState) -> str:
    """
    Route to appropriate agent based on signal category
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name: 'jfit', 'jwem', or 'both'
    """
    category = state.get('category', 'GENERAL')
    
    print(f"[ROUTER] Routing category: {category}")
    
    if category in ['TREND', 'MEME']:
        print("[ROUTER] → Jfit (trend/meme focus)")
        return 'jfit'
    elif category == 'FINANCE':
        print("[ROUTER] → Jwem (finance focus)")
        return 'jwem'
    else:
        print("[ROUTER] → Both agents (general query)")
        return 'both'


def should_continue_to_jwem(state: AgentState) -> str:
    """
    Decide if Jwem analysis is needed after Jfit
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name: 'jwem' or 'combine'
    """
    
    # Check iteration limit
    iteration_count = state.get('iteration_count', 0)
    max_iterations = state.get('max_iterations', 3)
    
    if iteration_count >= max_iterations:
        print(f"[ROUTER] Max iterations ({max_iterations}) reached → combine")
        return 'combine'
    
    # Check if error occurred
    if state.get('error'):
        print("[ROUTER] Error detected → combine")
        return 'combine'
    
    # Check if Jfit found finance-related trends
    trends = state.get('jfit_trends', [])
    finance_keywords = ['주식', '코인', '투자', '금리', '비트코인', 'stock', 'crypto', 'bitcoin', 'btc', 'eth']
    
    for trend in trends:
        content = trend.get('content', '').lower()
        if any(keyword in content for keyword in finance_keywords):
            print(f"[ROUTER] Finance keywords detected in trends → Jwem")
            return 'jwem'
    
    print("[ROUTER] No finance context needed → combine")
    return 'combine'


def should_continue_to_jfit(state: AgentState) -> str:
    """
    Decide if Jfit analysis is needed after Jwem
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name: 'jfit' or 'combine'
    """
    
    # Check iteration limit
    iteration_count = state.get('iteration_count', 0)
    max_iterations = state.get('max_iterations', 3)
    
    if iteration_count >= max_iterations:
        print(f"[ROUTER] Max iterations ({max_iterations}) reached → combine")
        return 'combine'
    
    # Check if error occurred
    if state.get('error'):
        print("[ROUTER] Error detected → combine")
        return 'combine'
    
    # If Jwem already ran and we have trends, combine
    if state.get('jfit_trends'):
        print("[ROUTER] Trends already available → combine")
        return 'combine'
    
    # Check if query suggests need for trend context
    query = state.get('query', '').lower()
    trend_keywords = ['트렌드', '밈', '유행', '인기', 'trend', 'meme', 'viral', 'popular']
    
    if any(keyword in query for keyword in trend_keywords):
        print("[ROUTER] Trend context needed → Jfit")
        return 'jfit'
    
    print("[ROUTER] No trend context needed → combine")
    return 'combine'
