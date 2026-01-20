# CLI-Mate 시작하기 (Docker 기반)

## 📋 사전 요구사항

- [ ] Docker 및 Docker Compose 설치됨
- [ ] OpenAI API 키 준비됨

> CLI 도구 사용 시에만 Python 3.10+ 필요

## 🚀 단계별 설정

### 1단계: 환경 설정

```bash
# 템플릿에서 .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env  # 또는 VSCode, vim 등
```

`.env` 파일에 OpenAI API 키 추가:
```env
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
```

### 2단계: Docker 서비스 시작

```bash
# 이미지 빌드 및 서비스 시작
docker-compose up -d --build

# 서비스 상태 확인
docker-compose ps
```

예상 출력:
```
NAME                  STATUS
cli-mate-backend      Up (healthy)
cli-mate-frontend     Up
```

### 3단계: 서비스 확인

```bash
# 백엔드 헬스 체크
curl http://localhost:8000/health
# 예상: {"status":"healthy","service":"cli-mate-backend"}

# 브라우저에서 확인
# - 백엔드 API 문서: http://localhost:8000/docs
# - 프론트엔드: http://localhost:3000
```

### 4단계: CLI 도구 사용

**방법 A: Docker로 실행 (권장)**

```bash
# CLI 이미지 빌드
docker-compose build cli

# CLI 실행 (백엔드가 healthy 상태여야 함)
docker-compose run --rm cli python -c "print(undefined_variable)"

# 도움말 확인
docker-compose run --rm cli --help
```

**방법 B: 로컬 설치**

```bash
cd cli
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
wtf --help
```

### 5단계: 테스트

**방법 1: Docker CLI**
```bash
docker-compose run --rm cli python -c "print(undefined_variable)"
```

**방법 2: 로컬 CLI**
```bash
wtf python -c "print(undefined_variable)"
```

**방법 3: API 직접 호출**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python test.py",
    "error_log": "NameError: name '\''undefined_variable'\'' is not defined",
    "language": "python"
  }'
```

---

## 🐳 Docker 명령어 가이드

### 서비스 관리

```bash
# 시작
docker-compose up -d

# 중지
docker-compose down

# 재시작
docker-compose restart

# 상태 확인
docker-compose ps
```

### 로그 확인

```bash
# 전체 로그
docker-compose logs -f

# 백엔드 로그만
docker-compose logs -f backend

# 최근 50줄
docker-compose logs --tail=50 backend
```

### 이미지 재빌드

```bash
# 특정 서비스 재빌드
docker-compose build backend --no-cache

# 재빌드 후 시작
docker-compose up -d --build
```

### 컨테이너 접속

```bash
# 백엔드 컨테이너 쉘 접속
docker-compose exec backend /bin/bash

# 프론트엔드 컨테이너 쉘 접속
docker-compose exec frontend /bin/sh
```

### 데이터 관리

```bash
# 볼륨 포함 전체 삭제 (주의: DB 데이터 삭제됨)
docker-compose down -v

# 볼륨 확인
docker volume ls | grep error_log
```

---

## 🛠️ 문제 해결

> 자세한 가이드: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### 백엔드가 unhealthy 상태

```bash
# 로그 확인
docker-compose logs backend
```

**오류 1:** `TypeError: AsyncClient.__init__() got an unexpected keyword argument 'proxies'`
**오류 2:** `AttributeError: np.float_ was removed in NumPy 2.0`

**해결:** `backend/requirements.txt` 확인:
```txt
httpx==0.27.0
numpy<2.0
```

재빌드:
```bash
docker-compose build backend --no-cache
docker-compose up -d backend
```

### OpenAI API 에러

```bash
# API 키 확인
cat .env | grep OPENAI_API_KEY

# 환경 변수 적용을 위해 재시작
docker-compose restart backend
```

### 포트 충돌

```bash
# 사용 중인 포트 확인
lsof -i :8000
lsof -i :3000

# 다른 프로세스 종료 후 재시작
docker-compose up -d
```

---

## 🎯 예상 결과

`wtf <command>` 실행 후 에러 발생 시:

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
NameError: name 'undefined_variable' is not defined

🔍 AI로 에러 분석 중...

==================================================
📌 NameError: 정의되지 않은 변수 'undefined_variable'
==================================================

💡 근본 원인:
변수 'undefined_variable'가 정의되지 않았습니다.

🔧 해결책:
변수를 사용하기 전에 먼저 정의해야 합니다:
  undefined_variable = "some value"
  print(undefined_variable)

🏷️  태그: python, NameError

🌐 상세 보기: http://localhost:3000/errors/abc-123-xyz
```

웹 대시보드 (http://localhost:3000):
- 캡처된 에러 목록 확인
- AI 분석 결과 상세 보기
- 유사 과거 사례 탐색

---

## ✅ 성공 기준

- [ ] `docker-compose ps` - 두 서비스 모두 `Up (healthy)` 상태
- [ ] `curl http://localhost:8000/health` - healthy 응답
- [ ] http://localhost:3000 - 웹 대시보드 접속 가능
- [ ] (선택) `wtf python -c "print(x)"` - 에러 캡처 및 분석

---

## 📚 관련 문서

- [README.md](README.md) - 프로젝트 개요
- [SPEC.md](SPEC.md) - 기술 명세
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 문제 해결 가이드

---

## 📊 프로젝트 진행 상황

### Phase 1: MVP ✅ 완료

| 항목 | 상태 | 비고 |
|------|------|------|
| CLI wrapper 구현 | ✅ 완료 | `wtf` 명령어 작동 확인 |
| FastAPI 기본 구조 및 `/analyze` API | ✅ 완료 | |
| SQLite 스키마 및 저장 로직 | ✅ 완료 | |
| Docker Compose 환경 구성 | ✅ 완료 | backend/frontend 실행 중 |

### Phase 2: AI & RAG ✅ 완료

| 항목 | 상태 | 비고 |
|------|------|------|
| OpenAI API 연동 (GPT-4o-mini) | ✅ 완료 | 분석 결과 정상 반환 |
| ChromaDB 설정 및 벡터 저장 | ✅ 완료 | |
| RAG 파이프라인 구현 | ✅ 완료 | |
| 유사 에러 검색 로직 | ✅ 완료 | |
| 프롬프트 엔지니어링 개선 | ⏳ 진행 예정 | |

### Phase 3: Frontend 🚧 진행 중

| 항목 | 상태 | 비고 |
|------|------|------|
| Next.js 기본 설정 | ✅ 완료 | |
| 에러 목록 대시보드 | ❌ 미구현 | 현재 스켈레톤만 있음 |
| 에러 상세 페이지 (`/errors/[id]`) | ❌ 미구현 | 페이지 없음 |
| 코드 하이라이팅 | ❌ 미구현 | |
| 유사 에러 추천 섹션 | ❌ 미구현 | |
| ErrorCard 컴포넌트 | ❌ 미구현 | |
| CodeViewer 컴포넌트 | ❌ 미구현 | |
| SimilarErrors 컴포넌트 | ❌ 미구현 | |

### Phase 4: Production ⏳ 대기 중

| 항목 | 상태 | 비고 |
|------|------|------|
| Terraform AWS 인프라 | ❌ 미구현 | `infra/` 폴더 없음 |
| GitHub Actions CI/CD | ❌ 미구현 | |
| 성능 최적화 | ❌ 미구현 | |
| 문서화 | ⏳ 부분 완료 | |

---

## 🎯 다음 단계 (TODO)

### 우선순위 1: Frontend 개발 (Phase 3)

백엔드 API는 완성되어 있으므로 프론트엔드 구현이 가장 시급합니다.

1. **에러 목록 대시보드** - `GET /api/errors` 호출하여 에러 리스트 표시
2. **에러 상세 페이지** - `src/app/errors/[id]/page.tsx` 생성
3. **컴포넌트 개발** - ErrorCard, CodeViewer, SimilarErrors
4. **코드 하이라이팅** - `react-syntax-highlighter` 또는 `shiki` 적용

### 우선순위 2: 프롬프트 엔지니어링 개선

- AI 분석 결과 품질 향상

### 우선순위 3: Production 배포 (Phase 4)

- Terraform 인프라 코드 작성
- GitHub Actions CI/CD 설정

---

즐거운 디버깅 되세요! 🎉
