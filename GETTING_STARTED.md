# CLI-Mate 시작하기

## 📋 사전 요구사항 체크리스트

- [ ] Docker 및 Docker Compose 설치됨
- [ ] Python 3.10 이상 설치됨
- [ ] OpenAI API 키 준비됨
- [ ] Git (선택사항, 버전 관리용)

## 🚀 단계별 설정

### 1단계: 환경 설정

```bash
# 템플릿에서 .env 파일 생성
cp .env.example .env

# .env 파일을 편집하여 OpenAI API 키 추가
# 텍스트 에디터 사용 (nano, vim, VSCode 등)
nano .env
```

실제 OpenAI API 키를 추가:
```bash
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
```

### 2단계: Docker 서비스 시작

```bash
# 백엔드와 프론트엔드 서비스 시작
docker-compose up -d

# 서비스가 실행 중인지 확인
docker-compose ps

# 예상 출력:
# NAME                  STATUS
# cli-mate-backend      Up (healthy)
# cli-mate-frontend     Up
```

### 3단계: 서비스 확인

```bash
# 백엔드 헬스 체크
curl http://localhost:8000/health

# 예상: {"status":"healthy","service":"cli-mate-backend"}

# 백엔드 문서 확인
open http://localhost:8000/docs  # 또는 브라우저에서 접속

# 프론트엔드 확인
open http://localhost:3000  # 또는 브라우저에서 접속
```

### 4단계: CLI 도구 설치

```bash
# CLI 디렉토리로 이동
cd cli

# 개발 모드로 설치 (편집 가능)
pip install -e .

# 설치 확인
wtf --help
```

### 5단계: 시스템 테스트

```bash
# 간단한 Python 에러로 테스트
wtf python -c "print(undefined_variable)"

# 예상 흐름:
# 1. 에러 캡처됨
# 2. AI가 에러 분석
# 3. 터미널에 분석 결과 표시
# 4. 데이터베이스에 에러 저장
# 5. 웹 뷰 링크 표시
```

## 🎯 예상 결과

`wtf <command>`를 실행하고 에러가 발생하면:

1. **터미널 출력:**
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
   ```python
   undefined_variable = "some value"
   print(undefined_variable)
   ```

   🏷️  태그: python, NameError

   🌐 상세 보기: http://localhost:3000/errors/abc-123-xyz
   ```

2. **웹 대시보드:**
   - http://localhost:3000 방문
   - 목록에서 에러 확인
   - 클릭하여 상세 분석 보기

## 🛠️ 문제 해결

### 문제: Docker 서비스가 시작되지 않음

```bash
# Docker 로그 확인
docker-compose logs backend
docker-compose logs frontend

# 서비스 재시작
docker-compose down
docker-compose up -d
```

### 문제: OpenAI API 에러

```bash
# API 키가 올바른지 확인
cat .env | grep OPENAI_API_KEY

# 새 환경 변수를 로드하기 위해 백엔드 재시작
docker-compose restart backend
```

### 문제: CLI 명령어를 찾을 수 없음

```bash
# CLI 재설치
cd cli
pip uninstall cli-mate
pip install -e .

# PATH 확인
which wtf
```

### 문제: 백엔드 연결 거부됨

```bash
# 백엔드가 실행 중인지 확인
curl http://localhost:8000/health

# CLI 설정 확인
echo $WTF_API_URL  # http://localhost:8000이어야 함
```

## 📊 서비스 모니터링

### 로그 보기

```bash
# 모든 서비스
docker-compose logs -f

# 백엔드만
docker-compose logs -f backend

# 프론트엔드만
docker-compose logs -f frontend
```

### 서비스 중지

```bash
# 모든 서비스 중지
docker-compose down

# 볼륨까지 삭제하여 중지 (주의: 데이터베이스 삭제됨)
docker-compose down -v
```

### 서비스 재시작

```bash
# 전체 재시작
docker-compose restart

# 백엔드만 재시작
docker-compose restart backend
```

## 🎓 다음 단계

1. **다양한 에러 유형 시도:**
   ```bash
   # Import 에러
   wtf python -c "import non_existent_module"

   # Type 에러
   wtf python -c "x = '5'; print(x + 5)"

   # Index 에러
   wtf python -c "lst = [1,2,3]; print(lst[10])"
   ```

2. **테스트 스크립트 작성:**
   ```python
   # test_error.py
   def divide(a, b):
       return a / b

   result = divide(10, 0)  # ZeroDivisionError
   ```

   실행:
   ```bash
   wtf python test_error.py
   ```

3. **웹 대시보드 탐색:**
   - 모든 에러 확인
   - AI 분석 보기
   - 유사한 과거 사례 확인

4. **아키텍처 검토:**
   - 기술 상세 내용은 [SPEC.md](SPEC.md) 참고
   - 개요는 [README.md](README.md) 참고

## 💡 팁

- **첫 실행은 시간이 더 걸립니다:** Docker 이미지 빌드 및 AI 모델 로드로 인해 첫 에러 분석이 10-15초 소요될 수 있습니다
- **유사 사례 확인:** 몇 개의 에러가 쌓이면 RAG 시스템이 과거 유사 사례를 제안하기 시작합니다
- **코드 컨텍스트:** 최상의 분석을 위해 에러가 읽을 수 있는 파일을 가리키는지 확인하세요
- **API 비용:** GPT-4o-mini는 매우 저렴하지만(~분석당 $0.0015), 사용량을 모니터링하세요

## 🤝 도움이 필요하신가요?

- 로그 확인: `docker-compose logs -f`
- 아키텍처 상세 내용은 SPEC.md 참고
- 백엔드 API 문서 확인: http://localhost:8000/docs

## ✅ 성공 기준

다음이 모두 작동하면 성공입니다:

- [ ] `docker-compose ps`로 두 서비스가 모두 실행 중임을 확인
- [ ] `curl http://localhost:8000/health`가 정상 상태 반환
- [ ] `wtf python -c "print(x)"`가 에러를 캡처하고 분석
- [ ] http://localhost:3000 웹 대시보드에 에러 표시
- [ ] AI가 근본 원인 및 해결책과 함께 분석 제공

---

즐거운 디버깅 되세요! 🎉
