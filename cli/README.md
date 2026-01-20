# CLI-Mate CLI 도구

AI 기반 에러 분석 CLI 래퍼입니다.

## 설치

```bash
# 개발 모드
pip install -e .

# 프로덕션 모드
pip install .
```

## 사용법

```bash
# 모든 명령어 앞에 'wtf'를 붙여서 실행
wtf python test.py
wtf npm run build
wtf go test ./...

# 에러 발생 시 자동으로:
# 1. 에러 로그 캡처
# 2. 코드 컨텍스트 추출
# 3. AI 분석을 위해 백엔드로 전송
# 4. 분석 결과 표시
```

## 설정

프로젝트 루트에 `.env` 파일 생성:

```bash
WTF_API_URL=http://localhost:8000
```

## 기능

- 실시간 명령어 출력 (stdout)
- 자동 에러 감지 (0이 아닌 종료 코드)
- Traceback 파싱 (Python, Node.js, Java)
- 코드 컨텍스트 추출 (±10줄)
- 민감 정보 마스킹
- AI 기반 에러 분석
