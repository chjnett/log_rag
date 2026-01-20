# CLI-Mate Project Specification

## 1. Project Overview

**프로젝트명:** CLI-Mate (Developer's AI Error Companion)

**핵심 가치:** 터미널에서 발생한 에러를 실시간으로 캡처하고, 에러가 발생한 소스 코드의 맥락을 포함하여 AI로 분석한 뒤, 개인 지식 베이스에 자동 저장 및 추천하는 개발자 도구

**주요 워크플로우:**
1. 사용자가 `wtf <command>` 실행
2. 에러 발생 시 로그 및 관련 코드 수집
3. 백엔드로 전송
4. RAG 기반 유사 사례 검색
5. AI 분석 (GPT-4o-mini)
6. 웹 대시보드에 게시

---

## 2. Technical Stack

### 2.1 CLI (Python Package)
- **Language:** Python 3.10+
- **Libraries:**
  - `subprocess` - 명령어 실행 및 출력 캡처
  - `requests` - 백엔드 API 통신
  - `re` - Traceback 파싱
  - `python-dotenv` - 환경 변수 관리
  - `click` - CLI 인터페이스
- **Installation:** pip installable package (setuptools)

### 2.2 Backend (FastAPI)
- **Framework:** FastAPI
- **Database:**
  - SQLite (메타데이터 저장)
  - ChromaDB (벡터 DB, 유사 에러 검색용)
- **AI:**
  - OpenAI Python SDK
  - Model: `gpt-4o-mini`
  - Embedding: `text-embedding-3-small`
- **Task Queue:** FastAPI BackgroundTasks
- **Port:** 8000

### 2.3 Frontend (Next.js)
- **Framework:** Next.js 14+ (App Router)
- **UI Library:**
  - Tailwind CSS
  - Shadcn/UI
  - Lucide React (Icons)
- **Code Highlighting:** `react-syntax-highlighter`
- **Port:** 3000

### 2.4 Infrastructure
- **Development:** Docker Compose (로컬 개발)
- **Production:** AWS EC2 (t2.micro), Docker
- **IaC:** Terraform
- **CI/CD:** GitHub Actions

---

## 3. System Architecture

```
┌─────────────┐
│   터미널    │
│ wtf python  │
│   test.py   │
└──────┬──────┘
       │ (에러 발생)
       ▼
┌─────────────────────────────────┐
│  CLI (wtf) - Python Package     │
│  1. stderr 캡처                 │
│  2. Traceback 파싱              │
│  3. 소스 코드 컨텍스트 추출     │
│  4. 민감 정보 마스킹            │
└──────┬──────────────────────────┘
       │ HTTP POST
       ▼
┌─────────────────────────────────┐
│  Backend (FastAPI:8000)         │
│  ┌───────────────────────────┐  │
│  │  /analyze API             │  │
│  └───────┬───────────────────┘  │
│          ▼                       │
│  ┌───────────────────────────┐  │
│  │  RAG Pipeline             │  │
│  │  1. ChromaDB 유사 검색    │  │
│  │  2. GPT-4o-mini 분석      │  │
│  │  3. SQLite 저장           │  │
│  └───────────────────────────┘  │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Frontend (Next.js:3000)        │
│  - 에러 리스트 대시보드         │
│  - 상세 분석 결과 뷰            │
│  - 유사 에러 추천               │
└─────────────────────────────────┘
```

---

## 4. Data Flow

### 4.1 Error Capture Flow
1. 사용자가 `wtf python test.py` 실행
2. CLI가 자식 프로세스로 `python test.py` 실행
3. stdout은 실시간으로 출력, stderr는 버퍼에 저장
4. Exit code != 0인 경우:
   - Traceback에서 파일 경로와 라인 번호 추출
   - 해당 파일의 에러 라인 ±10줄 읽기
   - .env 기반 민감 정보 마스킹
   - 백엔드로 전송

### 4.2 RAG Analysis Flow
1. 에러 로그 수신
2. OpenAI Embedding API로 벡터화
3. ChromaDB에서 유사도 0.8+ 검색 (최대 3개)
4. System Prompt 구성:
   ```
   너는 숙련된 시니어 개발자다.

   [과거 유사 사례]
   {similar_cases}

   [현재 에러]
   {current_error}

   [소스 코드]
   {code_context}

   위 정보를 바탕으로 에러를 분석하고 JSON 형식으로 응답해라:
   {
     "case_name": "직관적인 에러 이름",
     "root_cause": "원인 분석",
     "solution": "해결 방법 (코드 포함)",
     "tags": ["언어", "에러타입"]
   }
   ```
5. GPT-4o-mini 호출
6. 결과를 SQLite + ChromaDB에 저장

---

## 5. Database Schema

### 5.1 SQLite Schema
```sql
CREATE TABLE errors (
    id TEXT PRIMARY KEY,  -- UUID
    case_name TEXT NOT NULL,
    command TEXT NOT NULL,
    error_log TEXT NOT NULL,
    code_snippet TEXT,
    file_path TEXT,
    line_number INTEGER,
    ai_solution TEXT,
    root_cause TEXT,
    tags TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vector_id TEXT  -- ChromaDB document ID
);

CREATE INDEX idx_created_at ON errors(created_at DESC);
CREATE INDEX idx_tags ON errors(tags);
```

### 5.2 ChromaDB Collections
- **Collection Name:** `error_embeddings`
- **Metadata:** `{error_id, case_name, tags}`
- **Distance Metric:** Cosine similarity

---

## 6. Directory Structure

```
cli-mate/
├── cli/                          # Python CLI Package
│   ├── wtf/
│   │   ├── __init__.py
│   │   ├── main.py               # CLI entry point
│   │   ├── executor.py           # 명령어 실행 및 캡처
│   │   ├── parser.py             # Traceback 파싱
│   │   ├── context.py            # 소스 코드 컨텍스트 추출
│   │   ├── sanitizer.py          # 민감 정보 마스킹
│   │   └── api_client.py         # 백엔드 API 통신
│   ├── setup.py
│   ├── requirements.txt
│   └── README.md
│
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── analyze.py        # /analyze endpoint
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py         # 환경 변수
│   │   │   └── database.py       # SQLite 연결
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── rag.py            # RAG 로직
│   │   │   ├── ai.py             # OpenAI 호출
│   │   │   └── vector_store.py   # ChromaDB 관리
│   │   └── models/
│   │       ├── __init__.py
│   │       └── error.py          # SQLAlchemy models
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                     # Next.js Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # 메인 대시보드
│   │   │   ├── errors/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx  # 에러 상세 페이지
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── ErrorCard.tsx
│   │   │   ├── CodeViewer.tsx
│   │   │   └── SimilarErrors.tsx
│   │   └── lib/
│   │       └── api.ts            # API client
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── docker-compose.yml
├── .env.example
├── SPEC.md                       # 이 문서
└── README.md
```

---

## 7. API Specification

### POST /api/analyze
에러 로그와 컨텍스트를 받아 AI 분석 수행

**Request:**
```json
{
  "command": "python test.py",
  "error_log": "Traceback (most recent call last)...",
  "code_context": {
    "file_path": "/path/to/test.py",
    "line_number": 42,
    "code_snippet": "...",
    "language": "python"
  }
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "case_name": "NameError: undefined variable",
  "root_cause": "변수 'x'가 정의되지 않음",
  "solution": "x = 0을 추가하거나 함수 인자로 전달",
  "tags": ["python", "NameError"],
  "similar_cases": [
    {
      "id": "...",
      "case_name": "...",
      "similarity": 0.92
    }
  ]
}
```

### GET /api/errors
에러 목록 조회

**Query Parameters:**
- `page` (default: 1)
- `limit` (default: 20)
- `tag` (optional)

### GET /api/errors/{id}
특정 에러 상세 조회

---

## 8. Security & Privacy

### 8.1 민감 정보 마스킹
CLI에서 전송 전 다음 패턴 마스킹:
- API Keys: `api_key=***`, `token=***`
- 환경 변수: `.env` 파일의 모든 값
- 경로: 사용자 홈 디렉토리 → `~/`
- IP 주소: `xxx.xxx.xxx.xxx`

### 8.2 환경 변수
```bash
# Backend
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///./errors.db
CHROMA_PERSIST_DIRECTORY=/data/chroma

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# CLI
WTF_API_URL=http://localhost:8000
```

---

## 9. Development Setup

### 9.1 Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### 9.2 Quick Start
```bash
# 1. Clone repository
git clone <repo-url>
cd cli-mate

# 2. Environment setup
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Start services
docker-compose up -d

# 4. Install CLI (local development)
cd cli
pip install -e .

# 5. Test
wtf python -c "print(undefined_variable)"
```

---

## 10. Implementation Phases

### Phase 1: MVP (Week 1-2)
- [ ] CLI wrapper 구현 (기본 명령어 실행 및 에러 캡처)
- [ ] FastAPI 기본 구조 및 `/analyze` API
- [ ] SQLite 스키마 및 기본 저장 로직
- [ ] Docker Compose 환경 구성

### Phase 2: AI & RAG (Week 3)
- [ ] OpenAI API 연동 (GPT-4o-mini)
- [ ] ChromaDB 설정 및 벡터 저장
- [ ] RAG 파이프라인 구현
- [ ] 유사 에러 검색 로직

### Phase 3: Frontend (Week 4)
- [ ] Next.js 기본 구조
- [ ] 에러 리스트 대시보드
- [ ] 에러 상세 페이지
- [ ] 코드 하이라이팅

### Phase 4: Production (Week 5-6)
- [ ] Terraform AWS 인프라 구성
- [ ] GitHub Actions CI/CD
- [ ] 성능 최적화
- [ ] 문서화

---

## 11. Testing Strategy

### 11.1 CLI Testing
- Python 에러 시나리오 (NameError, TypeError, ImportError 등)
- Traceback 파싱 정확도
- 민감 정보 마스킹 검증

### 11.2 Backend Testing
- API 엔드포인트 테스트
- RAG 파이프라인 정확도
- DB 저장 및 조회 테스트

### 11.3 Integration Testing
- End-to-end 워크플로우 테스트
- Docker Compose 환경에서의 통합 테스트

---

## 12. Configuration

### Development Environment
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- ChromaDB: Docker Volume (`chroma_data`)
- SQLite: Docker Volume (`sqlite_data`)

### Ports
- FastAPI: 8000
- Next.js: 3000

### Supported Languages (Initial)
- Python (primary focus)
- Future: Node.js, Java, Go

---

## 13. Notes

- ChromaDB 데이터는 Docker Volume에 영구 저장
- SQLite DB 파일도 Docker Volume에 저장
- CLI는 pip로 설치 가능한 패키지로 개발
- 초기 데이터베이스는 빈 상태로 시작
- OpenAI API 키는 반드시 환경 변수로 관리
