#!/bin/bash

# AI Signal 맥미니 최적화 배포 스크립트
# Ultimate 2026 Stack 구현

set -e

echo "🚀 AI Signal 맥미니 최적화 배포 시작"
echo "=========================================="
echo ""

# 환경 변수 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사하세요."
    exit 1
fi

echo "✅ 환경 변수 확인 완료"
echo ""

# Docker Compose 시작
echo "🐳 Docker Compose 시작..."
docker-compose up -d

echo ""
echo "⏳ 서비스 시작 대기 중..."
sleep 10

# 서비스 상태 확인
echo ""
echo "📊 서비스 상태 확인:"
docker-compose ps

# PostgreSQL 마이그레이션
echo ""
echo "🗄️  PostgreSQL 마이그레이션 실행..."

# 데이터베이스 준비 대기
until docker exec aisignal-postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo "   PostgreSQL 준비 대기..."
    sleep 2
done

echo "   ✅ PostgreSQL 준비 완료"

# pgvector 마이그레이션 실행
echo "   📥 pgvector 마이그레이션..."
docker exec -i aisignal-postgres psql -U postgres -d aisignal < migrations/003_enable_pgvector.sql

echo "   ✅ 마이그레이션 완료"

# Ollama 모델 다운로드
echo ""
echo "🤖 Ollama 모델 다운로드..."
chmod +x scripts/setup_ollama.sh
./scripts/setup_ollama.sh

# Python 의존성 설치
echo ""
echo "📦 Python 의존성 설치..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "   ✅ 의존성 설치 완료"

# 서비스 URL 출력
echo ""
echo "=========================================="
echo "✅ 배포 완료!"
echo "=========================================="
echo ""
echo "🌐 서비스 URL:"
echo "   - AI Signal App:     http://localhost:8501"
echo "   - n8n Workflow:      http://localhost:5678"
echo "   - Ollama API:        http://localhost:11434"
echo "   - PostgreSQL:        localhost:5432"
echo "   - Redis:             localhost:6379"
echo ""
echo "🔑 기본 인증 정보:"
echo "   - n8n: admin / changeme (변경 권장)"
echo ""
echo "📊 상태 확인:"
echo "   docker-compose ps"
echo ""
echo "🛑 중지:"
echo "   docker-compose down"
echo ""
echo "🎉 Happy Coding!"
