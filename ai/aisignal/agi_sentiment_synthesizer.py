import os
import pandas as pd
from db_utils import get_db_connection
from telegram_notifier import TelegramNotifier

def synthesize_agi_sentiment(issue_id):
    """
    특정 이슈에 대해 내부/외부 AGI의 투표 결과를 합성하여 요약 생성 및 전송
    """
    conn = get_db_connection()
    notifier = TelegramNotifier()
    
    try:
        with conn.cursor() as cur:
            # 1. 이슈 기본 정보 조회
            cur.execute("SELECT title, category FROM issues WHERE id = %s", (issue_id,))
            issue_res = cur.fetchone()
            if not issue_res:
                print(f"❌ 이슈 ID {issue_id}를 찾을 수 없습니다.")
                return
            title, category = issue_res
            
            # 2. 내부 에이전트 투표 조회 (Jwem, Jfit, Stealth)
            cur.execute("""
                SELECT agent_name, vote_selection, confidence_score, logic_rationale 
                FROM agent_issue_votes 
                WHERE issue_id = %s AND agent_type = 'INTERNAL' AND is_latest = TRUE
            """, (issue_id,))
            internal_votes = cur.fetchall()
            
            # 3. 외부 AGI 투표 조회 (Moltbot, Open-Cro 등)
            cur.execute("""
                SELECT agent_name, vote_selection, confidence_score, logic_rationale 
                FROM agent_issue_votes 
                WHERE issue_id = %s AND agent_type = 'EXTERNAL' AND is_latest = TRUE
            """, (issue_id,))
            external_votes = cur.fetchall()
            
        # 데이터 처리 및 합성 로직
        if not internal_votes and not external_votes:
            print("⚠️ 투표 데이터가 부족합니다.")
            return

        # 내부 요약 계산
        int_pros = sum(1 for v in internal_votes if v[1] == 'PROS')
        int_total = len(internal_votes)
        int_res = "찬성 우세" if int_pros > int_total/2 else "반대/신중"
        int_conf = int(sum(v[2] for v in internal_votes) / int_total) if int_total > 0 else 0
        
        # 외부 요약 계산
        ext_pros = sum(1 for v in external_votes if v[1] == 'PROS')
        ext_total = len(external_votes)
        ext_res = "찬성 우세" if ext_pros > ext_total/2 else "반대/신중"
        ext_agree = "강력한 합의" if (ext_pros == ext_total or ext_pros == 0) and ext_total > 1 else "의견 분분"
        
        # 인사이트 합성 (LLM이 수행하는 영역이나 여기서는 논리적 규칙으로 모사)
        synthesis = ""
        if int_res == ext_res:
            synthesis = f"내부 요원과 외부 AGI 모두 {int_res} 의견으로 일치된 신호를 보냅니다. 신뢰도가 매우 높습니다."
        else:
            synthesis = f"내부 분석은 {int_res}이나, 외부 AGI({external_votes[0][0]} 등)는 {ext_res}으로 나타납니다. 관점의 차이에 주의하세요."

        summary_data = {
            "internal_result": int_res,
            "internal_confidence": int_conf,
            "external_result": ext_res,
            "external_agreement": ext_agree,
            "synthesis_insight": synthesis
        }
        
        # 텔레그램 전송
        notifier.send_agi_summary(title, summary_data)
        
    except Exception as e:
        print(f"❌ 합성 중 에러 발생: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # 테스트: 1번 이슈에 대해 합성 수행
    # 실제 운영 시에는 새로운 투표가 쌓이거나 크론탭에 의해 호출될 수 있음
    synthesize_agi_sentiment(1)
