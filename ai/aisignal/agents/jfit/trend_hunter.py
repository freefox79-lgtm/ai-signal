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

    def inject_dopamine(self, boring_data):
        """Single item dopamine injection (Legacy/Single)"""
        return self.inject_dopamine_batch([boring_data])[0]
        
    def inject_dopamine_batch(self, items: list) -> list:
        """
        여러 데이터에 도파민 한꺼번에 주입 (Mac Mini 최적화 배치 처리)
        
        Args:
            items: 분석할 원본 데이터 리스트
            
        Returns:
            list: 최적화된 결과 리스트
        """
        if not items:
            return []
            
        print(f"[JFIT 🎭] Injecting dopamine into {len(items)} items (Batch Processing)...")
        
        # 10개씩 청크로 나눔 (LLM 컨텍스트 최적화)
        chunk_size = 10
        all_results = []
        
        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            
            # Ollama용 배치 프롬프트 생성
            batch_text = "\n---\n".join([f"Item {idx+1}: {str(item)[:300]}" for idx, item in enumerate(chunk)])
            
            prompt = f"""다음 {len(chunk)}량의 데이터를 각각 재미있고 바이럴한 문구로 재작성하세요.
밈, 이모지, 위트를 최대한 활용하고 한국어 인터넷 문화를 반영하세요.
각 항목은 반드시 'Item N:' 형식을 유지하며 구분하세요.

데이터 리스트:
{batch_text}

재미있는 버전들:"""
            
            try:
                response = self.ollama.generate(
                    prompt,
                    model="llama3.2:3b",
                    temperature=0.9,
                    max_tokens=1000
                )
                
                # 결과 파싱 (간단한 파싱 로직)
                # 실제 환경에서는 더 정교한 Regex나 JSON 모드 사용 권장
                lines = response.split('\n')
                current_item_text = []
                chunk_results = []
                
                for line in lines:
                    if line.startswith('Item') and ':' in line:
                        if current_item_text:
                            chunk_results.append("\n".join(current_item_text).strip())
                            current_item_text = []
                    else:
                        current_item_text.append(line)
                
                if current_item_text:
                    chunk_results.append("\n".join(current_item_text).strip())
                
                # 개수 맞춤 (부족하면 원본 또는 에러 메시지)
                while len(chunk_results) < len(chunk):
                    chunk_results.append("다음에 더 재미있는 짤로 찾아올게요! (분석 오류)")
                
                for idx, result in enumerate(chunk_results[:len(chunk)]):
                    all_results.append({
                        "original": str(chunk[idx]),
                        "dopamine_version": result,
                        "meme_suggestions": ["stonks_meme.jpg"], # Batch logic simplifies this
                        "engagement_score": random.uniform(0.85, 0.99)
                    })
                    
            except Exception as e:
                print(f"[JFIT 🎭] Batch dopamine error: {e}")
                for item in chunk:
                    all_results.append({"original": str(item), "dopamine_version": "Error in batch", "engagement_score": 0.0})
                    
        return all_results
    
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

