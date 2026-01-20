# Troubleshooting Guide

## 백엔드 연동 오류 해결 (2026-01-20)

### 증상
```
❌ 백엔드 연동 실패
✗ 포트 8000 닫힘 (서버 실행 안 됨)
```

백엔드 컨테이너가 `unhealthy` 상태로 표시되며 서버가 정상 시작되지 않음.

---

## 오류 1: openai + httpx 호환성 문제

### 에러 메시지
```
TypeError: AsyncClient.__init__() got an unexpected keyword argument 'proxies'
```

### 원인
- `openai==1.10.0` 라이브러리가 내부적으로 httpx를 사용
- 최신 httpx 버전에서 `proxies` 파라미터가 deprecated/제거됨
- 의존성 버전 충돌 발생

### 해결
`backend/requirements.txt`에 httpx 버전 고정:
```
httpx==0.27.0
```

---

## 오류 2: chromadb + numpy 호환성 문제

### 에러 메시지
```
AttributeError: `np.float_` was removed in the NumPy 2.0 release. Use `np.float64` instead.
```

### 원인
- `chromadb==0.4.22`가 `np.float_` 타입을 사용
- NumPy 2.0에서 해당 타입이 제거됨

### 해결
`backend/requirements.txt`에 numpy 버전 제한:
```
numpy<2.0
```

---

## 수정된 requirements.txt

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
openai==1.10.0
httpx==0.27.0
chromadb==0.4.22
numpy<2.0
python-dotenv==1.0.0
aiosqlite==0.19.0
```

---

## Docker 재빌드 명령어

```bash
# 1. 이미지 재빌드 (캐시 없이)
docker-compose build backend --no-cache

# 2. 컨테이너 재시작
docker-compose up -d backend

# 3. 로그 확인
docker-compose logs -f backend

# 4. 상태 확인
docker-compose ps

# 5. 헬스체크
curl http://localhost:8000/health
```

---

## 유용한 디버깅 명령어

```bash
# 전체 로그 확인
docker-compose logs --tail=100

# 특정 서비스 로그 실시간 확인
docker-compose logs -f backend

# 컨테이너 내부 접속
docker-compose exec backend /bin/bash

# 컨테이너 재시작
docker-compose restart backend

# 전체 재시작 (이미지 재빌드 포함)
docker-compose up -d --build
```

---

## 정상 동작 확인

```bash
$ docker-compose ps
NAME                STATUS
cli-mate-backend    Up (healthy)
cli-mate-frontend   Up

$ curl http://localhost:8000/health
{"status":"healthy","service":"cli-mate-backend"}
```
