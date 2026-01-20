FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CLI 패키지 설치
COPY . .
RUN pip install -e .

# 환경 변수
ENV WTF_API_URL=http://backend:8000

# 기본 명령어
ENTRYPOINT ["wtf"]
CMD ["--help"]
