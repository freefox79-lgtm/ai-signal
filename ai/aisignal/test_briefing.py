import os
from analysis_generator import AnalysisGenerator

def test_briefing_generation():
    print("🚀 Testing Strategic Consensus Briefing Generation...")
    try:
        gen = AnalysisGenerator()
        briefing_id = gen.generate_strategic_consensus_briefing()
        print(f"✅ Success! Briefing ID: {briefing_id}")
        
        # Verify result in DB
        from data_router import router
        result = router.execute_query(f"SELECT title, content FROM consensus_briefings WHERE id = {briefing_id}")
        if result:
            print(f"Title: {result[0][0]}")
            print("Content Preview:")
            print(result[0][1][:200] + "...")
        else:
            print("❌ Briefing not found in DB.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_briefing_generation()
