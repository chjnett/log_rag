# 📄 PROJECT_SPEC.md: CLI-Mate

## 1. 프로젝트 개요

* **프로젝트명:** CLI-Mate (Developer's AI Error Companion)
* **핵심 가치:** 터미널에서 발생한 에러를 실시간으로 캡처하고, 에러가 발생한 소스 코드의 맥락(Context)을 포함하여 AI로 분석한 뒤, 나만의 트러블슈팅 지식 베이스(웹)에 자동 저장 및 추천
* **주요 워크플로우:** `wtf <command>` 실행 → 에러 발생 시 로그 및 관련 코드 수집 → 백엔드 전송 → RAG 기반 유사 사례 검색 → AI 분석 → 웹 대시보드 게시

---

## 2. 디렉토리 구조

```text
cli-mate/
├── cli/                # Python 기반 CLI 래퍼 (wtf)
│   ├── wtf.py          # 핵심 실행 스크립트
│   └── requirements.txt
├── backend/            # FastAPI 서버 (RAG & AI 분석)
│   ├── app/
│   │   ├── main.py     # API 엔드포인트
│   │   ├── ai_logic.py # GPT-4o-mini & ChromaDB 로직
│   │   └── models.py   # DB 스키마 (SQLAlchemy/SQLite)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/           # Next.js 대시보드
│   ├── src/
│   │   ├── app/        # 대시보드 페이지 및 상세 페이지
│   │   └── components/ # 에러 카드, 코드 뷰어 등
│   ├── Dockerfile
│   └── package.json
└── infra/              # IaC 및 배포 설정
    ├── terraform/      # AWS EC2, SG, VPC 설정
    └── docker-compose.yml
```

---

## 3. 기술 스택 (v1.0)

* **CLI:** Python 3.10+, `subprocess`, `re`, `requests`
* **백엔드:** FastAPI, SQLite (메타데이터), ChromaDB (RAG용 벡터 DB)
* **AI:** OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`)
* **프론트엔드:** Next.js 14+ (App Router), Tailwind CSS, Shadcn/UI
* **클라우드:** AWS EC2 (t2.micro), Docker, Terraform, GitHub Actions

---

## 4. 단계별 구현 가이드

### Phase 1: CLI 수집기 & 기본 API (파이프라인)

* **목표:** 터미널 에러가 백엔드 DB에 저장되는 최소 기능 구현
* **CLI 핵심:**
  * `wtf` 명령어로 자식 프로세스 실행 및 `stderr` 실시간 캡처
  * Traceback에서 `File "path/to/file.py", line XX` 패턴을 정규표현식으로 추출
  * 해당 파일의 XX번 라인 앞뒤 10줄을 읽어 `code_context` 생성
* **API:** `/analyze` POST 엔드포인트 구현 (로그 및 코드 수신 후 SQLite 저장)

### Phase 2: RAG & AI 두뇌 (지능)

* **목표:** 과거 이력을 참고하여 AI가 에러를 분석
* **RAG 로직:**
  1. 에러 로그를 벡터화하여 ChromaDB에 저장
  2. 새 에러 발생 시 ChromaDB에서 유사도 0.8 이상의 과거 사례 3개 검색
  3. `System Prompt`: "너는 시니어 개발자다. [과거 사례]를 참고하여 [현재 로그]와 [소스 코드]를 분석해라."
* **출력:** 에러 이름, 원인 요약, 해결 코드(Markdown)를 JSON으로 생성

### Phase 3: 웹 대시보드 (인터페이스)

* **목표:** 축적된 에러 데이터를 시각화
* **메인 페이지:** 발생 시각순 에러 카드 리스트 (검색 및 언어별 필터링 포함)
* **상세 페이지:**
  * 왼쪽 패널: 에러 로그 원문 (터미널 느낌의 블랙 테마)
  * 오른쪽 패널: AI 분석 결과 및 해결 코드 (Syntax Highlighting)
  * 하단: "유사한 과거 에러 해결 사례" 추천 섹션

### Phase 4: 클라우드 & DevOps (배포)

* **Terraform:** `t2.micro` 인스턴스에 Docker를 자동 설치하는 `user_data` 포함
* **CI/CD:** GitHub Actions를 이용해 `main` 푸시 시 Docker Hub 빌드 및 EC2 자동 배포

---

## 5. 데이터베이스 스키마 (SQLite)

* `errors` 테이블: `id`, `case_name`, `command`, `error_log`, `code_snippet`, `ai_solution`, `tags`, `created_at`

## 6. 보안 (민감 정보 제거)

* CLI에서 전송 전 `.env`에 정의된 민감한 문자열이나 환경변수를 `***`로 치환하는 로직 필수 포함

---
