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

    # 2. 백엔드 서버 체크
    print("\n2️⃣  백엔드 서버 확인...")
    try:
        import urllib.request
        api_url = os.getenv("WTF_API_URL", "http://localhost:8000")

        req = urllib.request.Request(f"{api_url}/health")
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            print(f"   ✓ 서버 응답: {data}")
            print(f"   ✓ 백엔드 정상 동작 중!\n")
            return True

    except urllib.error.URLError:
        print(f"   ✗ 서버 연결 실패: {api_url}")
        print("   💡 docker-compose up -d 명령으로 서버를 시작하세요\n")
        return False
    except Exception as e:
        print(f"   ✗ 오류: {e}\n")
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
