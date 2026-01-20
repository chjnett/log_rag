# 📄 PRD: CLI-Mate (AI 기반 에러 지식 베이스)

## 1. 프로젝트 개요

* **목표:** 터미널 에러를 실시간으로 캡처하고, 소스 코드 맥락을 포함하여 AI로 분석한 뒤, 이를 개인 지식 베이스(웹)에 자동 아카이빙하는 개발자 도구
* **핵심 가치:** 에러 로그의 자산화, RAG를 통한 과거 유사 에러 해결법 추천, 디버깅 시간 단축

## 2. 기술 스택

### 2.1. 클라이언트 (CLI)

* **언어:** Python 3.10+
* **라이브러리:** `subprocess` (래퍼 구현), `requests` (API 통신), `re` (Traceback 파싱), `python-dotenv` (민감 정보 필터링)

### 2.2. 백엔드 (API & AI)

* **프레임워크:** FastAPI
* **AI SDK:** OpenAI Python SDK (모델: `gpt-4o-mini`, 임베딩: `text-embedding-3-small`)
* **벡터 DB:** ChromaDB (로컬 모드) - 유사 에러 검색용
* **RDB:** SQLite (AWS Free Tier 성능 최적화용) - 메타데이터 저장용
* **작업 큐:** 필요 시 비동기 처리를 위한 `BackgroundTasks` (FastAPI 내장)

### 2.3. 프론트엔드 (대시보드)

* **프레임워크:** Next.js 14+ (App Router)
* **UI 라이브러리:** Tailwind CSS, Shadcn/UI, Lucide React (아이콘)
* **코드 하이라이팅:** `react-syntax-highlighter` 또는 `shiki`

### 2.4. 인프라 (DevOps)

* **클라우드:** AWS EC2 (t2.micro - Free Tier)
* **컨테이너:** Docker, Docker Compose
* **IaC:** Terraform (VPC, SG, EC2, Elastic IP 설정)
* **CI/CD:** GitHub Actions

---

## 3. 시스템 아키텍처 & 데이터 흐름

1. **실행:** 사용자가 `wtf <command>` 실행
2. **수집 (CLI):** `wtf`가 자식 프로세스를 실행하며 실시간으로 `stdout/stderr` 수집
3. **조건:** Exit Code가 0이 아닐 경우, 로그에서 에러 발생 파일명/라인 번호 추출
4. **컨텍스트 수집:** 해당 소스 코드를 열어 에러 라인 앞뒤 10줄을 읽어 패키징
5. **민감 정보 제거:** `.env` 기반 민감 정보 마스킹 후 서버 전송
6. **RAG 프로세스 (백엔드):**
   * 현재 에러 로그를 벡터화
   * ChromaDB에서 유사도 0.8 이상의 과거 사례 검색
   * `과거 사례 + 현재 코드 + 현재 로그`를 GPT에게 전달
7. **아카이빙:** AI 분석 결과(이름, 원인, 코드 해결책)를 DB에 저장 및 웹 대시보드 업데이트

---

## 4. 핵심 로직 사양

### 4.1. CLI 래퍼 (wtf.py)

```python
# 의사 코드
def run_wrapper(command):
    process = subprocess.Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = process.communicate()
    if process.returncode != 0:
        analyze_and_send(err.decode())

def analyze_and_send(log):
    # 1. Traceback에서 파일 경로와 라인 번호 추출 (정규표현식)
    # 2. 로컬 파일에서 소스 코드 컨텍스트 확보
    # 3. .env 키워드 기반 마스킹 처리
    # 4. POST /analyze {log, code_context, command}
```

### 4.2. RAG 프롬프트 엔지니어링

```text
System: 너는 숙련된 시니어 개발자다. 아래 정보를 바탕으로 에러를 분석해라.
Context: [과거 유사 에러 해결 이력들]
Current Error: [현재 에러 로그]
Current Code: [에러 발생 지점 코드 스니펫]

Output Format (JSON):
{
  "case_name": "직관적인 에러 이름",
  "root_cause": "원인 분석",
  "solution_code": "해결 방법 (코드)",
  "tags": ["언어/프레임워크", "에러유형"]
}
```

---

## 5. 데이터베이스 스키마 (ERD)

### 테이블: `errors`

* `id`: UUID (PK)
* `command`: TEXT (실행한 명령어)
* `error_log`: TEXT (전체 로그)
* `code_snippet`: TEXT (오류 발생 코드)
* `case_name`: VARCHAR (AI가 생성한 이름)
* `solution`: TEXT (AI가 제시한 해결책)
* `created_at`: TIMESTAMP
* `vector_id`: VARCHAR (ChromaDB와 매핑용)

---

## 6. 인프라 청사진 (Terraform)

* **리전:** ap-northeast-2 (서울)
* **네트워킹:** Public Subnet 내 1대의 EC2
* **보안 그룹:**
  * Inbound: 22(SSH), 80(HTTP), 3000(Next.js), 8000(FastAPI)
* **자동화:** `user_data`를 통해 Docker 및 Docker Compose 자동 설치

---

## 7. 구현 로드맵

1. **Phase 1:** CLI 래퍼 (`wtf` 커맨드) & 기본적인 FastAPI 서버 연동
2. **Phase 2:** ChromaDB 연동 및 GPT-4o-mini 기반 RAG 파이프라인 구축
3. **Phase 3:** Next.js 대시보드 (에러 리스트 및 상세 분석 뷰) 개발
4. **Phase 4:** Terraform을 이용한 AWS 배포 및 GitHub Actions CI/CD 설정

---

## 8. 다음 단계

프로젝트를 시작하려면:

1. Phase 1의 핵심인 **CLI 래퍼(`wtf.py`)**와 **FastAPI 백엔드의 수신 API**부터 구현
2. CLI는 Traceback을 분석해서 실제 파일의 코드를 읽어오는 로직을 정교하게 구현
3. 각 단계별로 테스트를 진행하며 점진적으로 기능 추가

---

이 문서를 기반으로 최고의 프로젝트를 만들어보세요!
