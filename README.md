# CLI-Mate 🤖

> 개발자를 위한 AI 기반 에러 분석 및 지식 베이스

CLI-Mate는 터미널에서 발생하는 에러를 실시간으로 캡처하고, AI가 분석하여 해결책을 제시하는 개발자 도구입니다. 모든 에러는 자동으로 지식 베이스에 저장되어, 과거 유사 사례를 기반으로 더 나은 해결책을 제안합니다.

## ✨ 주요 기능

- 🔍 **실시간 에러 캡처**: 명령어 실행 중 발생하는 에러를 자동으로 감지
- 🧠 **AI 분석**: GPT-4o-mini를 활용한 에러 원인 분석 및 해결책 제시
- 📚 **RAG 기반 추천**: ChromaDB를 통한 과거 유사 에러 검색 및 추천
- 💾 **지식 베이스**: 모든 에러를 자동으로 저장하여 개인 트러블슈팅 DB 구축
- 🌐 **웹 대시보드**: Next.js 기반 직관적인 에러 관리 인터페이스
- 🔒 **민감 정보 보호**: API 키, 토큰 등 자동 마스킹

## 🚀 빠른 시작

### 사전 요구사항

- Docker & Docker Compose
- Python 3.10+
- OpenAI API Key

### 1. 저장소 복제

```bash
git clone <repository-url>
cd cli-mate
```

### 2. 환경 설정

```bash
# 환경 변수 템플릿 복사
cp .env.example .env

# .env 파일을 편집하여 OpenAI API 키 추가
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. 서비스 시작

```bash
# Docker Compose로 백엔드와 프론트엔드 시작
docker-compose up -d

# 서비스가 준비될 때까지 대기
# 백엔드: http://localhost:8000
# 프론트엔드: http://localhost:3000
```

### 4. CLI 도구 설치

```bash
# 개발 모드로 설치
cd cli
pip install -e .
```

### 5. 테스트

```bash
# 에러가 발생하는 명령어 실행
wtf python -c "print(undefined_variable)"

# CLI-Mate가 자동으로:
# 1. 에러를 캡처
# 2. AI로 분석
# 3. 분석 결과 표시
# 4. 지식 베이스에 저장
```

## 📖 사용 방법

### CLI 사용법

```bash
# 모든 명령어 앞에 'wtf'를 붙여서 실행
wtf python test.py
wtf npm run build
wtf go test ./...

# CLI가 자동으로:
# - 명령어를 정상적으로 실행
# - 에러 발생 시 캡처 및 분석
# - 터미널에 AI 분석 결과 표시
# - 지식 베이스에 저장
```

### 웹 대시보드

[http://localhost:3000](http://localhost:3000)에 접속하면:
- 캡처된 모든 에러 확인
- 상세한 AI 분석 결과 보기
- 과거 유사 사례 탐색
- 태그별 검색 및 필터링

## 🏗️ 아키텍처

```
┌─────────────┐
│  터미널     │  wtf python test.py
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  CLI (Python 패키지)        │
│  - 에러 캡처                │
│  - Traceback 파싱           │
│  - 코드 컨텍스트 추출       │
└──────┬──────────────────────┘
       │ HTTP POST
       ▼
┌─────────────────────────────┐
│  백엔드 (FastAPI)           │
│  - ChromaDB (RAG 검색)      │
│  - GPT-4o-mini (분석)       │
│  - SQLite (저장)            │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  프론트엔드 (Next.js)       │
│  - 에러 대시보드            │
│  - 상세 분석 뷰             │
└─────────────────────────────┘
```

## 🛠️ 개발

### 프로젝트 구조

```
cli-mate/
├── cli/                    # Python CLI package
│   ├── wtf/
│   │   ├── main.py        # CLI entry point
│   │   ├── executor.py    # Command execution
│   │   ├── parser.py      # Traceback parsing
│   │   ├── context.py     # Code context extraction
│   │   ├── sanitizer.py   # Sensitive data masking
│   │   └── api_client.py  # Backend communication
│   └── setup.py
│
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── main.py       # FastAPI app
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config & database
│   │   └── services/     # RAG, AI, vector store
│   └── Dockerfile
│
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/         # Pages
│   │   ├── components/  # React components
│   │   └── lib/         # API client
│   └── Dockerfile
│
└── docker-compose.yml
```

### 개별 서비스 실행

```bash
# 백엔드만 실행
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 프론트엔드만 실행
cd frontend
npm install
npm run dev

# CLI (로컬 개발)
cd cli
pip install -e .
```

### 테스트 실행

```bash
# 샘플 에러로 CLI 테스트
wtf python -c "import non_existent_module"

# 백엔드 API 테스트
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"command": "test", "error_log": "Error message"}'
```

## 🔧 설정

### 환경 변수

모든 사용 가능한 설정 옵션은 [.env.example](.env.example)을 참고하세요.

주요 설정:
- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `WTF_API_URL`: 백엔드 URL (기본값: http://localhost:8000)
- `SIMILARITY_THRESHOLD`: RAG 유사도 임계값 (기본값: 0.8)

### CLI 설정

프로젝트 디렉토리에 `.env` 파일 생성:

```bash
WTF_API_URL=http://localhost:8000
```

## 📊 지원 언어

현재 최적화된 언어:
- ✅ Python (전체 traceback 파싱)
- ✅ Node.js/JavaScript (기본 지원)
- ✅ Java (기본 지원)

더 많은 언어 지원 예정!

## 🎯 로드맵

### Phase 1: MVP ✅
- [x] 에러 캡처 CLI 래퍼
- [x] FastAPI 백엔드 및 기본 API
- [x] SQLite 데이터베이스
- [x] Docker Compose 설정

### Phase 2: AI & RAG (진행 중)
- [x] OpenAI API 통합
- [x] ChromaDB 벡터 스토어
- [x] RAG 파이프라인
- [ ] 프롬프트 엔지니어링 개선

### Phase 3: 프론트엔드
- [x] Next.js 기본 설정
- [ ] 에러 목록 대시보드
- [ ] 에러 상세 페이지
- [ ] 코드 하이라이팅
- [ ] 유사 에러 섹션

### Phase 4: 프로덕션
- [ ] Terraform AWS 인프라
- [ ] GitHub Actions CI/CD
- [ ] 성능 최적화
- [ ] 문서화

## 🛠️ 문제 해결

Docker 서비스 시작 오류나 의존성 충돌 문제가 발생하면:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 상세 트러블슈팅 가이드
- [GETTING_STARTED.md](GETTING_STARTED.md) - 단계별 설정 가이드

## 🤝 기여하기

기여는 언제나 환영합니다! Pull Request를 자유롭게 제출해 주세요.

## 📝 라이선스

MIT License

## 🙏 감사의 말

- OpenAI의 GPT-4o-mini
- ChromaDB 벡터 데이터베이스
- FastAPI 웹 프레임워크
- Next.js 프론트엔드 프레임워크

---

같은 에러를 두 번 디버깅하는 것을 싫어하는 개발자들을 위해 ❤️를 담아 만들었습니다.
