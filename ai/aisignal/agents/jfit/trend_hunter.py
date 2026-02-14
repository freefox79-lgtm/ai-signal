import os
import json
import subprocess
import random
from agents.security.agent_security import AgentSecurityMiddleware
from agents.llm.ollama_client import get_ollama_client
from dotenv import load_dotenv

load_dotenv(".env.local")

class JfitTrendHunter:
    """
    쥐핏 (Jfit) - 창의적 악동
    
    페르소나:
    - 밈(MEME)과 위트 중심
    - 트렌드 해석에 도파민 주입
    - 짤방 추천 및 유저 인터랙션 유도
    
    보안:
    - 프롬프트 인젝션 방어
    - 개인정보 보호
    - 악의적 쿼리 차단
    """
    
    PERSONA = {
        "name": "쥐핏 (Jfit)",
        "archetype": "창의적 악동 (Pathos)",
        "traits": ["창의성", "유머", "바이럴", "감성 자극", "보안"],
        "communication_style": "위트 있고 재미있는 밈 중심 해석",
        "emoji": "🎭"
    }
    
    def __init__(self):
        self.security = AgentSecurityMiddleware()  # 🔒 보안 미들웨어
        self.ollama = get_ollama_client()  # 🤖 Ollama 로컬 LLM

    def hunt_trends(self, query="K-Meme", user_id="default"):
        """
        트렌드 수집 (보안 검증 포함)
        
        Args:
            query: 검색 쿼리
            user_id: 사용자 ID (rate limiting용)
            
        Returns:
            트렌드 리스트 또는 보안 에러
        """
        # 🔒 쿼리 보안 검증
        return self.security.secure_execute(
            self._hunt_trends_internal,
            query,
            user_id=user_id
        )
    
    def _hunt_trends_internal(self, query):
        """내부 트렌드 수집 로직 (Stealth Crawler 사용)"""
        print(f"[JFIT 🎭] Hunting trends for: {query}")
        
        trends = []
        
        try:
            # X (Twitter) 수집
            x_trends = self._call_stealth_crawler('x', query)
            if x_trends:
                trends.extend(x_trends)
            
            # Instagram 수집
            insta_trends = self._call_stealth_crawler('instagram', query)
            if insta_trends:
                trends.extend(insta_trends)
            
            # 커뮤니티 수집 (더쿠, 루리웹, 클리앙, DCInside, FMKorea)
            community_trends = self._call_stealth_crawler('community', query)
            if community_trends:
                trends.extend(community_trends)
            
            # 쇼핑 수집 (Hypebeast, Kream)
            shopping_trends = self._call_stealth_crawler('shopping', query)
            if shopping_trends:
                trends.extend(shopping_trends)
            
            print(f"[JFIT 🎭] Collected {len(trends)} real trends from Stealth Crawler")
            
        except Exception as e:
            print(f"[JFIT 🎭] Crawler error: {e}, using fallback")
            return self._get_fallback_trends(query)
        
        return trends if trends else self._get_fallback_trends(query)
    
    def _call_stealth_crawler(self, platform: str, query: str) -> list:
        """Stealth Crawler 호출 (subprocess)"""
        crawler_path = os.path.join(
            os.path.dirname(__file__),
            "../../stealth-crawler/index.js"
        )
        
        try:
            result = subprocess.run(
                ['node', crawler_path, platform, query],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                # 점수 추가 (간단한 로직)
                for item in data:
                    item['score'] = random.randint(75, 95)
                return data
            else:
                print(f"[JFIT] Crawler error for {platform}: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print(f"[JFIT] Crawler timeout for {platform}")
            return []
        except Exception as e:
            print(f"[JFIT] Crawler exception: {e}")
            return []
    
    def _get_fallback_trends(self, query: str) -> list:
        """Fallback 트렌드 (Mock Data)"""
        from datetime import datetime
        return [
            {
                "platform": "DCInside",
                "content": f"'{query}' 관련 밈 급격히 확산 중",
                "score": 92,
                "source": "Fallback Engine",
                "timestamp": datetime.now().isoformat()
            },
            {
                "platform": "X",
                "content": f"#{query} trending in Tech category",
                "score": 88,
                "source": "Fallback Engine",
                "timestamp": datetime.now().isoformat()
            }
        ]

    def generate_meme_prompt(self, trend_data):
        """Converts trend data into a creative prompt for meme generation."""
        return f"Create a cyberpunk meme about: {trend_data[0]['content']}"
    
    def inject_dopamine(self, boring_data):
        """
        지루한 데이터에 도파민 주입 (Ollama AI 창의성)
        
        Args:
            boring_data: dict or str with boring analysis
            
        Returns:
            dict: {
                "original": str,
                "dopamine_version": str,
                "meme_suggestions": list,
                "engagement_score": float
            }
        """
        print("[JFIT 🎭] Injecting dopamine into boring data...")
        
        original = str(boring_data)
        
        # Ollama로 창의적 재작성
        prompt = f"""다음 지루한 데이터를 재미있고 바이럴한 문구로 재작성하세요.
밈, 이모지, 위트를 최대한 활용하세요. 한국어 인터넷 문화를 반영하세요.

지루한 데이터:
{original[:500]}

재미있는 버전:"""
        
        try:
            dopamine_version = self.ollama.generate(
                prompt,
                model="llama3.2:3b",
                temperature=0.9,  # 창의성 높게
                max_tokens=200
            ).strip()
            
            print(f"[JFIT 🎭] AI Dopamine: {dopamine_version[:50]}...")
            
        except Exception as e:
            print(f"[JFIT 🎭] Ollama error, using fallback: {e}")
            # Fallback: 간단한 템플릿
            if isinstance(boring_data, dict):
                sentiment = boring_data.get('market_sentiment', 'neutral')
                if sentiment == 'bullish':
                    dopamine_version = f"🚀 달까지 가즈아! 🌙"
                elif sentiment == 'bearish':
                    dopamine_version = f"😱 곰이 나타났다! 🐻"
                else:
                    dopamine_version = f"😐 심심한 하루네요 zzZ"
            else:
                dopamine_version = f"🎉 {original[:100]} (근데 이거 재미없음 ㅋㅋ)"
        
        # Meme suggestions
        meme_suggestions = [
            "stonks_meme.jpg",
            "this_is_fine.gif",
            "money_printer_go_brr.png"
        ]
        
        engagement_score = random.uniform(0.75, 0.98)
        
        result = {
            "original": original,
            "dopamine_version": dopamine_version,
            "meme_suggestions": meme_suggestions,
            "engagement_score": engagement_score
        }
        
        print(f"[JFIT 🎭] Dopamine injected! Engagement score: {engagement_score:.0%}")
        
        return result
    
    def recommend_meme(self, trend_context):
        """
        트렌드에 맞는 짤방 추천
        
        Args:
            trend_context: dict with trend information
            
        Returns:
            dict: {
                "meme_url": str,
                "meme_caption": str,
                "relevance_score": float
            }
        """
        print(f"[JFIT 🎭] Recommending meme for: {trend_context.get('content', '')[:30]}...")
        
        content = trend_context.get('content', '').lower()
        
        # Meme selection logic
        if '급상승' in content or 'trending' in content:
            meme_url = "https://i.imgur.com/stonks.jpg"
            meme_caption = "📈 STONKS! 이거 대박 예감!"
            relevance_score = 0.95
        elif '하락' in content or 'down' in content:
            meme_url = "https://i.imgur.com/not_stonks.jpg"
            meme_caption = "📉 NOT STONKS... 이건 좀..."
            relevance_score = 0.90
        else:
            meme_url = "https://i.imgur.com/thinking.jpg"
            meme_caption = "🤔 흠... 이거 어떻게 생각함?"
            relevance_score = 0.75
        
        recommendation = {
            "meme_url": meme_url,
            "meme_caption": meme_caption,
            "relevance_score": relevance_score
        }
        
        print(f"[JFIT 🎭] Meme recommended: {meme_caption} (relevance: {relevance_score:.0%})")
        
        return recommendation
    
    def create_viral_headline(self, data):
        """
        바이럴 가능성 높은 헤드라인 생성
        
        Args:
            data: dict with content to create headline from
            
        Returns:
            list[str]: 3가지 헤드라인 옵션
        """
        print("[JFIT 🎭] Creating viral headlines...")
        
        content = str(data.get('content', '')) if isinstance(data, dict) else str(data)
        
        # Generate 3 viral headline options
        headlines = [
            f"🔥 충격! {content[:20]}... 이거 실화냐?",
            f"💥 지금 난리남: {content[:20]}... (클릭 주의)",
            f"🚨 속보! {content[:20]}... 모두 주목!"
        ]
        
        print(f"[JFIT 🎭] Generated {len(headlines)} viral headlines")
        
        return headlines

if __name__ == "__main__":
    jfit = JfitTrendHunter()
    trends = jfit.hunt_trends()
    print(json.dumps(trends, indent=2))

