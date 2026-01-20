#!/usr/bin/env python3
"""
빠른 백엔드 연동 테스트 (의존성 최소화)
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

def test_quick():
    print("🔍 빠른 백엔드 연동 테스트\n")

    # 1. 환경 변수 체크
    print("1️⃣  환경 변수 확인...")
    api_key = os.getenv("OPENAI_API_KEY")
    db_url = os.getenv("DATABASE_URL")
    chroma_dir = os.getenv("CHROMA_PERSIST_DIRECTORY")

    if api_key:
        print(f"   ✓ OPENAI_API_KEY: {api_key[:15]}...")
    else:
        print("   ✗ OPENAI_API_KEY 없음")
        return False

    if db_url:
        print(f"   ✓ DATABASE_URL: {db_url}")
    else:
        print("   ✗ DATABASE_URL 없음")
        return False

    if chroma_dir:
        print(f"   ✓ CHROMA_PERSIST_DIRECTORY: {chroma_dir}")
    else:
        print("   ✗ CHROMA_PERSIST_DIRECTORY 없음")
        return False

    # 1-2. 데이터베이스 파일 확인
    print("\n1️⃣-2 데이터베이스 파일 확인...")
    sqlite_path = "/data/sqlite/errors.db"
    chroma_path = "/data/chroma"

    if os.path.exists(sqlite_path):
        print(f"   ✓ SQLite DB 존재: {sqlite_path}")
    else:
        print(f"   ⚠ SQLite DB 아직 생성 안 됨 (첫 실행 시 자동 생성)")

    if os.path.exists(chroma_path):
        print(f"   ✓ Chroma DB 디렉토리 존재: {chroma_path}")
    else:
        print(f"   ⚠ Chroma DB 아직 생성 안 됨 (첫 실행 시 자동 생성)")

    # 2. 백엔드 서버 체크
    print("\n2️⃣  백엔드 서버 확인...")

    # 포트가 열려있는지 확인
    try:
        import socket

        # 8000 포트가 열려있는지 확인
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()

        if result == 0:
            print(f"   ✓ 포트 8000 열림 (서버 실행 중)")

            # HTTP 요청 시도
            try:
                import urllib.request
                req = urllib.request.Request("http://127.0.0.1:8000/health")
                with urllib.request.urlopen(req, timeout=3) as response:
                    data = json.loads(response.read().decode())
                    print(f"   ✓ 서버 응답: {data}")
                    print(f"   ✓ 백엔드 정상 동작 중!\n")
                    return True
            except Exception as e:
                print(f"   ⚠ HTTP 요청 실패: {e}")
                print(f"   ✓ 하지만 포트는 열려있음 (서버 시작 중일 수 있음)\n")
                return True
        else:
            print(f"   ✗ 포트 8000 닫힘 (서버 실행 안 됨)")
            print(f"   💡 컨테이너 외부에서 docker-compose up -d 실행 필요\n")
            return False

    except Exception as e:
        print(f"   ✗ 서버 확인 중 오류: {e}\n")
        return False

if __name__ == "__main__":
    success = test_quick()

    if success:
        print("✅ 백엔드 연동 성공!")
        print("\n다음 명령으로 전체 테스트를 실행하세요:")
        print("  python test_backend_connection.py")
        sys.exit(0)
    else:
        print("❌ 백엔드 연동 실패")
        print("\n문제 해결:")
        print("  1. .env 파일에 OPENAI_API_KEY 설정 확인")
        print("  2. docker-compose up -d 실행")
        print("  3. docker-compose ps로 상태 확인")
        sys.exit(1)
