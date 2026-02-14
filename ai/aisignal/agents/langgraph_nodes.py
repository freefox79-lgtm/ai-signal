"""
LangGraph Node Wrappers for AI Signal Agents

Wraps Jfit and Jwem agents as LangGraph nodes with proper state management.
"""

from agents.jfit.trend_hunter import JfitTrendHunter
from agents.jwem.market_analyzer import JwemMarketAnalyzer
from agents.agent_state import AgentState
from langchain_core.messages import HumanMessage, AIMessage


class AgentNodes:
    """LangGraph node wrappers for agents"""
    
    def __init__(self):
        self.jfit = JfitTrendHunter()
        self.jwem = JwemMarketAnalyzer()
    
    def jfit_node(self, state: AgentState) -> AgentState:
        """
        Jfit agent node - trend hunting and meme analysis
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Jfit's trend analysis
        """
        print(f"[JFIT NODE] Processing query: {state['query']}")
        
        try:
            # Hunt trends using Jfit
            trends = self.jfit.hunt_trends(state['query'])
            
            # Update state
            state['jfit_trends'] = trends
            state['messages'] = state.get('messages', []) + [
                AIMessage(content=f"Jfit found {len(trends)} trends: {', '.join([t.get('content', '')[:30] for t in trends[:3]])}")
            ]
            state['iteration_count'] = state.get('iteration_count', 0) + 1
            
            print(f"[JFIT NODE] Found {len(trends)} trends")
            
        except Exception as e:
            error_msg = f"Jfit error: {str(e)}"
            state['error'] = error_msg
            state['messages'] = state.get('messages', []) + [
                AIMessage(content=error_msg)
            ]
            print(f"[JFIT NODE ERROR] {error_msg}")
        
        return state
    
    def jwem_node(self, state: AgentState) -> AgentState:
        """
        Jwem agent node - market analysis and fact checking
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Jwem's market analysis
        """
        print(f"[JWEM NODE] Processing query: {state['query']}")
        
        try:
            # Get Jfit trends for context
            jfit_trends = state.get('jfit_trends', [])
            
            # Analyze market data
            market_data = self.jwem.analyze_market_data(context=jfit_trends)
            
            # Assess market risk
            risk_assessment = self.jwem.assess_market_risk(context=jfit_trends)
            
            # Combine analysis
            analysis = {
                "market_data": market_data,
                "risk_assessment": risk_assessment,
                "market_sentiment": market_data.get('sentiment', 'neutral'),
                "risk_analysis": f"Risk: {risk_assessment.get('risk_level', 'unknown')}, VIX: {risk_assessment.get('volatility_index', 0)}",
                "portfolio_status": "market_analyzed",
                "recommendations": risk_assessment.get('recommendations', []),
                "trend_correlation": len(jfit_trends)
            }
            
            state['jwem_analysis'] = analysis
            state['messages'] = state.get('messages', []) + [
                AIMessage(content=f"Jwem market analysis: {market_data.get('sentiment')} sentiment, {risk_assessment.get('risk_level')} risk")
            ]
            state['iteration_count'] = state.get('iteration_count', 0) + 1
            
            print(f"[JWEM NODE] Analysis complete: {analysis['market_sentiment']} sentiment")
            
        except Exception as e:
            error_msg = f"Jwem error: {str(e)}"
            state['error'] = error_msg
            state['messages'] = state.get('messages', []) + [
                AIMessage(content=error_msg)
            ]
            print(f"[JWEM NODE ERROR] {error_msg}")
        
        return state
    
    def combine_node(self, state: AgentState) -> AgentState:
        """
        Cross-Validation & Combine Node
        
        Performs cross-validation between Jwem and Jfit, then combines insights.
        
        Process:
        1. Jwem fact-checks Jfit's trends
        2. Jfit injects dopamine into Jwem's analysis
        3. Create consensus report
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with validated and combined final signals
        """
        print("\n[CROSS-VALIDATION] Starting agent cross-validation...")
        
        # Step 1: Jwem fact-checks Jfit's trends
        fact_check_results = []
        jfit_trends = state.get('jfit_trends', [])
        
        if jfit_trends:
            print(f"[CROSS-VALIDATION] Jwem fact-checking {len(jfit_trends)} trends...")
            for trend in jfit_trends:
                fact_check = self.jwem.fact_check_trend(trend)
                fact_check_results.append({
                    'trend': trend,
                    'fact_check': fact_check
                })
        
        state['fact_check_results'] = fact_check_results
        
        # Step 2: Jfit injects dopamine into Jwem's analysis
        jwem_analysis_enhanced = {}
        jwem_analysis = state.get('jwem_analysis')
        
        if jwem_analysis:
            print("[CROSS-VALIDATION] Jfit injecting dopamine into Jwem's analysis...")
            dopamine_result = self.jfit.inject_dopamine(jwem_analysis)
            jwem_analysis_enhanced = dopamine_result
        
        state['jwem_analysis_enhanced'] = jwem_analysis_enhanced
        
        # Step 3: Calculate consensus score
        if fact_check_results:
            verified_confidences = [
                result['fact_check']['confidence']
                for result in fact_check_results
                if result['fact_check']['verified']
            ]
            consensus_score = sum(verified_confidences) / len(verified_confidences) if verified_confidences else 0.0
        else:
            consensus_score = 0.0
        
        state['consensus_score'] = consensus_score
        state['validation_complete'] = True
        
        # Step 4: Create final signals with validated data
        final_signals = []
        
        # Add fact-checked trends only
        for result in fact_check_results:
            if result['fact_check']['verified']:
                trend = result['trend']
                final_signals.append({
                    'source': 'Jfit 🎭 (Verified by Jwem 📊)',
                    'type': 'trend',
                    'platform': trend.get('platform', 'Unknown'),
                    'content': trend.get('content', ''),
                    'score': trend.get('score', 0),
                    'confidence': result['fact_check']['confidence'],
                    'fact_check': result['fact_check']['logical_assessment']
                })
        
        # Add Jwem analysis with dopamine
        if jwem_analysis:
            final_signals.append({
                'source': 'Jwem 📊 (Enhanced by Jfit 🎭)',
                'type': 'analysis',
                'content': jwem_analysis_enhanced.get('dopamine_version', str(jwem_analysis)),
                'original_content': f"Portfolio: {jwem_analysis.get('portfolio_status', 'unknown')}, "
                                  f"Risk: {jwem_analysis.get('risk_analysis', 'N/A')}, "
                                  f"Sentiment: {jwem_analysis.get('market_sentiment', 'neutral')}",
                'confidence': 0.9,
                'engagement_score': jwem_analysis_enhanced.get('engagement_score', 0.0),
                'meme_suggestions': jwem_analysis_enhanced.get('meme_suggestions', []),
                'details': jwem_analysis
            })
        
        # Step 5: Create consensus report
        if jfit_trends:
            headlines = self.jfit.create_viral_headline(jfit_trends[0])
            title = headlines[0] if headlines else "AI Signal 분석 리포트"
        else:
            title = "AI Signal 분석 리포트"
        
        executive_summary = self.jwem.optimize_report(jwem_analysis) if jwem_analysis else "분석 데이터 없음"
        
        final_report = {
            "title": title,
            "executive_summary": executive_summary,
            "fact_checked_trends": [
                {
                    'content': result['trend']['content'],
                    'platform': result['trend']['platform'],
                    'confidence': result['fact_check']['confidence'],
                    'assessment': result['fact_check']['logical_assessment']
                }
                for result in fact_check_results
                if result['fact_check']['verified']
            ],
            "creative_insights": [jwem_analysis_enhanced.get('dopamine_version', '')] if jwem_analysis_enhanced else [],
            "meme_recommendations": jwem_analysis_enhanced.get('meme_suggestions', []),
            "confidence_score": consensus_score,
            "validation_notes": f"Verified by Jwem 📊, Enhanced by Jfit 🎭",
            "agents": {
                "jwem": JwemMarketAnalyzer.PERSONA,
                "jfit": JfitTrendHunter.PERSONA
            }
        }
        
        state['final_report'] = final_report
        state['final_signals'] = final_signals
        state['confidence_score'] = consensus_score
        state['messages'] = state.get('messages', []) + [
            AIMessage(content=f"Cross-validation complete: {len(fact_check_results)} trends verified, consensus: {consensus_score:.0%}")
        ]
        
        print(f"[CROSS-VALIDATION] Complete! Consensus score: {consensus_score:.0%}")
        print(f"[COMBINE NODE] Generated {len(final_signals)} validated signals\n")
        
        return state

