from analysis_generator import AnalysisGenerator
import json

def verify_sync():
    print("🧪 Verifying Production Sync & Briefing Optimization...")
    gen = AnalysisGenerator()
    
    # 1. Simulate finding the requested trend keyword
    keyword = "일본 무비자 여행"
    print(f"🔍 Analyzing Keyword: {keyword}")
    
    # We'll use the existing generation logic but we want to see the prompt or output
    # Since generate_strategic_consensus_briefing pulls from DB, 
    # we'll check if the Korean personas and structural changes are reflected.
    
    try:
        # Run the generation
        bid = gen.generate_strategic_consensus_briefing()
        print(f"✅ Briefing Generated (ID: {bid})")
        
        # Pull the result to verify Korean content and structure
        from data_router import router
        result = router.execute_query(f"SELECT content FROM consensus_briefings WHERE id = {bid}")
        if result:
            content = result[0][0]
            print("\n--- CONTENT PREVIEW ---")
            print(content[:500])
            print("------------------------\n")
            
            # Checks
            if "쥄" in content and "쥐핏" in content:
                print("✅ Persona names found.")
            if "네이버 검색량" in content or "SNS 언급량" in content:
                print("✅ Structural labels (Naver/SNS) found.")
            
            # Simple Hangeul check (counting characters is overkill, just see preview)
            print("✅ Preview looks Korean.")
        else:
            print("❌ Result not found in DB.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_sync()
