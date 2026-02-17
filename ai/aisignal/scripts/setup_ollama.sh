#!/bin/bash

# Ollama 모델 설정 스크립트
# Mac Mini M1/M2 최적화

set -e

echo "🚀 Ollama 모델 설정 시작..."
echo ""

# Ollama 컨테이너 시작 대기
echo "⏳ Ollama 서비스 대기 중..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
  echo "   Ollama 시작 대기..."
  sleep 3
done

echo "✅ Ollama 준비 완료!"
echo ""

# 모델 다운로드
echo "📥 모델 다운로드 중..."
echo ""

# 1. Llama 3.2 (3B) - 빠른 응답용
echo "1️⃣  Llama 3.2 (3B) 다운로드..."
docker exec aisignal-ollama ollama pull llama3.2:3b
echo "   ✅ Llama 3.2 완료"
echo ""

# 3. Gemma 3 (12B) - 심층 추론 및 전략 전문가
echo "3️⃣  Gemma 3 (12B) 다운로드..."
docker exec aisignal-ollama ollama pull gemma3:12b
echo "   ✅ Gemma 3 완료"
echo ""

# 4. Nomic Embed Text - 임베딩용 (GraphRAG)
echo "4️⃣  Nomic Embed Text 다운로드..."
docker exec aisignal-ollama ollama pull nomic-embed-text
echo "   ✅ Nomic Embed Text 완료"
echo ""

echo "✅ 모델 다운로드 완료!"
echo ""
echo "📊 설치된 모델 목록:"
docker exec aisignal-ollama ollama list
echo ""
echo "🎉 Ollama 설정 완료!"
echo ""
echo "사용 예시:"
echo "  curl http://localhost:11434/api/generate -d '{\"model\":\"llama3.2:3b\",\"prompt\":\"Hello\"}'"
