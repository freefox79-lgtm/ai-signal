"""
Cross-Validation Node for Multi-Agent Collaboration

Implements the cross-validation mechanism between Jwem and Jfit agents.
"""

from agents.jwem.market_analyzer import JwemMarketAnalyzer
from agents.jfit.trend_hunter import JfitTrendHunter
from agents.agent_state import AgentState
from langchain_core.messages import AIMessage


class CrossValidationNode:
    """
    Cross-validation between Jwem (논리주의자) and Jfit (창의적 악동)
    
    Process:
    1. Jwem fact-checks Jfit's trends
    2. Jfit injects dopamine into Jwem's analysis
    3. Create consensus report combining both perspectives
    """
    
    def __init__(self):
        self.jwem = JwemMarketAnalyzer()
        self.jfit = JfitTrendHunter()
    
    def validate_node(self, state: AgentState) -> AgentState:
        """
        Perform cross-validation between agents
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with validation results and consensus report
        """
        print("\n[CROSS-VALIDATION] Starting agent cross-validation...")
        
        # Step 1: Jwem fact-checks Jfit's trends
        fact_check_results = []
        if state.get('jfit_trends'):
            print(f"[CROSS-VALIDATION] Jwem fact-checking {len(state['jfit_trends'])} trends...")
            for trend in state['jfit_trends']:
                fact_check = self.jwem.fact_check_trend(trend)
                fact_check_results.append({
                    'trend': trend,
                    'fact_check': fact_check
                })
        
        state['fact_check_results'] = fact_check_results
        
        # Step 2: Jfit injects dopamine into Jwem's analysis
        jwem_analysis_enhanced = {}
        if state.get('jwem_analysis'):
            print("[CROSS-VALIDATION] Jfit injecting dopamine into Jwem's analysis...")
            dopamine_result = self.jfit.inject_dopamine(state['jwem_analysis'])
            jwem_analysis_enhanced = dopamine_result
        
        state['jwem_analysis_enhanced'] = jwem_analysis_enhanced
        
        # Step 3: Create consensus report
        print("[CROSS-VALIDATION] Creating consensus report...")
        final_report = self._create_consensus_report(state)
        state['final_report'] = final_report
        state['validation_complete'] = True
        
        # Calculate consensus score
        consensus_score = self._calculate_consensus_score(fact_check_results)
        state['consensus_score'] = consensus_score
        
        # Add message
        state['messages'] = state.get('messages', []) + [
            AIMessage(content=f"Cross-validation complete: {len(fact_check_results)} trends verified, consensus score: {consensus_score:.0%}")
        ]
        
        print(f"[CROSS-VALIDATION] Complete! Consensus score: {consensus_score:.0%}\n")
        
        return state
    
    def _create_consensus_report(self, state):
        """
        Create consensus report combining both agents' perspectives
        
        Args:
            state: Current agent state
            
        Returns:
            dict: Consensus report with verified data and creative insights
        """
        
        # Get viral headline from Jfit
        jfit_trends = state.get('jfit_trends', [])
        if jfit_trends:
            headlines = self.jfit.create_viral_headline(jfit_trends[0])
            title = headlines[0] if headlines else "AI Signal 분석 리포트"
        else:
            title = "AI Signal 분석 리포트"
        
        # Get optimized summary from Jwem
        jwem_analysis = state.get('jwem_analysis', {})
        if jwem_analysis:
            executive_summary = self.jwem.optimize_report(jwem_analysis)
        else:
            executive_summary = "분석 데이터 없음"
        
        # Collect fact-checked trends
        fact_checked_trends = []
        for result in state.get('fact_check_results', []):
            if result['fact_check']['verified']:
                fact_checked_trends.append({
                    'content': result['trend']['content'],
                    'platform': result['trend']['platform'],
                    'confidence': result['fact_check']['confidence'],
                    'assessment': result['fact_check']['logical_assessment']
                })
        
        # Get logical analysis from Jwem
        logical_analysis = self.jwem.analyze_with_logic(state)
        
        # Get creative insights from Jfit
        creative_insights = []
        dopamine_enhanced = state.get('jwem_analysis_enhanced', {})
        if dopamine_enhanced:
            creative_insights.append(dopamine_enhanced.get('dopamine_version', ''))
        
        # Get meme recommendations
        meme_recommendations = []
        for trend in jfit_trends[:3]:  # Top 3 trends
            meme_rec = self.jfit.recommend_meme(trend)
            meme_recommendations.append(meme_rec)
        
        # Build final report
        report = {
            "title": title,
            "executive_summary": executive_summary,
            "fact_checked_trends": fact_checked_trends,
            "logical_analysis": logical_analysis,
            "creative_insights": creative_insights,
            "meme_recommendations": meme_recommendations,
            "confidence_score": state.get('consensus_score', 0.0),
            "validation_notes": f"Verified by Jwem 📊, Enhanced by Jfit 🎭",
            "agents": {
                "jwem": JwemMarketAnalyzer.PERSONA,
                "jfit": JfitTrendHunter.PERSONA
            }
        }
        
        return report
    
    def _calculate_consensus_score(self, fact_check_results):
        """
        Calculate consensus score based on fact-check results
        
        Args:
            fact_check_results: List of fact-check results
            
        Returns:
            float: Consensus score (0.0 - 1.0)
        """
        if not fact_check_results:
            return 0.0
        
        # Average confidence of verified trends
        verified_confidences = [
            result['fact_check']['confidence']
            for result in fact_check_results
            if result['fact_check']['verified']
        ]
        
        if not verified_confidences:
            return 0.0
        
        return sum(verified_confidences) / len(verified_confidences)
