#!/usr/bin/env python3
"""
백엔드 연동 테스트 스크립트
SQLite, Chroma DB, OpenAI API 연동 상태를 확인합니다.
"""

import os
import sys
import requests
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 색상 코드
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def test_environment_variables():
    """환경 변수 확인"""
    print_header("1. 환경 변수 테스트")

    required_vars = {
        "OPENAI_API_KEY": "OpenAI API 키",
        "DATABASE_URL": "SQLite 데이터베이스 URL",
        "CHROMA_PERSIST_DIRECTORY": "Chroma 저장소 경로"
    }

    all_passed = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # API 키는 일부만 표시
            if "API_KEY" in var:
                masked_value = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
                print_success(f"{description}: {masked_value}")
            else:
                print_success(f"{description}: {value}")
        else:
            print_error(f"{description}: 설정되지 않음")
            all_passed = False

    return all_passed

def test_backend_health():
    """백엔드 헬스 체크"""
    print_header("2. 백엔드 서버 연결 테스트")

    api_url = os.getenv("WTF_API_URL", "http://localhost:8000")

    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"백엔드 서버 정상 동작: {data}")
            return True
        else:
            print_error(f"백엔드 서버 응답 오류: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"백엔드 서버 연결 실패: {api_url}")
        print_warning("docker-compose up -d 명령으로 서버를 시작하세요")
        return False
    except Exception as e:
        print_error(f"예상치 못한 오류: {e}")
        return False

def test_sqlite_connection():
    """SQLite 데이터베이스 연결 테스트"""
    print_header("3. SQLite 데이터베이스 테스트")

    db_url = os.getenv("DATABASE_URL", "sqlite:////data/sqlite/errors.db")
    db_path = db_url.replace("sqlite:///", "")

    # Docker 볼륨 경로는 컨테이너 내부에서만 접근 가능
    if db_path.startswith("/data/"):
        print_warning(f"Docker 볼륨 경로: {db_path}")
        print_warning("컨테이너 내부에서만 직접 접근 가능")
        print("  확인 방법: docker exec -it cli-mate-backend ls -la /data/sqlite/")
        return None

    # 로컬 파일 시스템 경로인 경우
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 테이블 존재 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='errors'")
            result = cursor.fetchone()

            if result:
                print_success(f"SQLite 데이터베이스 연결 성공: {db_path}")

                # 레코드 수 확인
                cursor.execute("SELECT COUNT(*) FROM errors")
                count = cursor.fetchone()[0]
                print_success(f"저장된 에러 레코드: {count}개")
            else:
                print_warning("errors 테이블이 생성되지 않음")

            conn.close()
            return True
        except Exception as e:
            print_error(f"SQLite 연결 오류: {e}")
            return False
    else:
        print_warning(f"데이터베이스 파일 없음: {db_path}")
        print_warning("첫 실행 시 자동으로 생성됩니다")
        return None

def test_chroma_connection():
    """Chroma DB 연결 테스트"""
    print_header("4. Chroma DB 테스트")

    chroma_dir = os.getenv("CHROMA_PERSIST_DIRECTORY", "/data/chroma")

    # Docker 볼륨 경로
    if chroma_dir.startswith("/data/"):
        print_warning(f"Docker 볼륨 경로: {chroma_dir}")
        print_warning("컨테이너 내부에서만 직접 접근 가능")
        print("  확인 방법: docker exec -it cli-mate-backend ls -la /data/chroma/")
        return None

    # 로컬 파일 시스템 경로인 경우
    if os.path.exists(chroma_dir):
        try:
            import chromadb
            from chromadb.config import Settings

            client = chromadb.PersistentClient(
                path=chroma_dir,
                settings=Settings(anonymized_telemetry=False)
            )

            # 컬렉션 확인
            collections = client.list_collections()
            print_success(f"Chroma DB 연결 성공: {chroma_dir}")

            if collections:
                for collection in collections:
                    count = collection.count()
                    print_success(f"컬렉션 '{collection.name}': {count}개 임베딩 저장됨")
            else:
                print_warning("컬렉션이 아직 생성되지 않음")

            return True
        except ImportError:
            print_error("chromadb 패키지가 설치되지 않음")
            print("  설치: pip install chromadb")
            return False
        except Exception as e:
            print_error(f"Chroma DB 연결 오류: {e}")
            return False
    else:
        print_warning(f"Chroma 디렉토리 없음: {chroma_dir}")
        print_warning("첫 실행 시 자동으로 생성됩니다")
        return None

def test_openai_api():
    """OpenAI API 연결 테스트"""
    print_header("5. OpenAI API 테스트")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print_error("OPENAI_API_KEY가 설정되지 않음")
        return False

    try:
        import openai

        client = openai.OpenAI(api_key=api_key)

        # 간단한 임베딩 테스트
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="테스트 문자열"
        )

        if response.data:
            print_success("OpenAI API 연결 성공")
            print_success(f"임베딩 생성 완료 (차원: {len(response.data[0].embedding)})")
            return True
        else:
            print_error("OpenAI API 응답 오류")
            return False

    except ImportError:
        print_error("openai 패키지가 설치되지 않음")
        print("  설치: pip install openai")
        return False
    except Exception as e:
        error_msg = str(e)
        if "Incorrect API key" in error_msg or "invalid_api_key" in error_msg:
            print_error("API 키가 올바르지 않음")
            print("  https://platform.openai.com/api-keys 에서 새 키 발급")
        elif "insufficient_quota" in error_msg:
            print_error("API 사용 한도 초과 또는 결제 정보 없음")
            print("  https://platform.openai.com/settings/organization/billing 에서 결제 정보 등록")
        else:
            print_error(f"OpenAI API 오류: {e}")
        return False

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print_header("6. API 엔드포인트 테스트")

    api_url = os.getenv("WTF_API_URL", "http://localhost:8000")

    try:
        # GET /errors 테스트
        response = requests.get(f"{api_url}/errors", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"GET /errors: {data.get('total', 0)}개 에러 조회")
        else:
            print_error(f"GET /errors 실패: {response.status_code}")

        # API 문서 확인
        response = requests.get(f"{api_url}/docs", timeout=5)
        if response.status_code == 200:
            print_success(f"API 문서 접근 가능: {api_url}/docs")

        return True
    except Exception as e:
        print_error(f"API 엔드포인트 테스트 실패: {e}")
        return False

def test_docker_status():
    """Docker 컨테이너 상태 확인"""
    print_header("7. Docker 컨테이너 상태")

    try:
        import subprocess

        result = subprocess.run(
            ["docker-compose", "ps"],
            capture_output=True,
            text=True,
            cwd="/mnt/c/workspace2/error_log"
        )

        if result.returncode == 0:
            print(result.stdout)

            if "cli-mate-backend" in result.stdout and "Up" in result.stdout:
                print_success("백엔드 컨테이너 실행 중")
            else:
                print_warning("백엔드 컨테이너가 실행 중이지 않음")
                print("  시작: docker-compose up -d")

            return True
        else:
            print_warning("docker-compose 명령 실패")
            return False

    except FileNotFoundError:
        print_warning("docker-compose가 설치되지 않음")
        return False
    except Exception as e:
        print_error(f"Docker 상태 확인 실패: {e}")
        return False

def main():
    print(f"\n{BLUE}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║  CLI-Mate 백엔드 연동 테스트                              ║{RESET}")
    print(f"{BLUE}╚══════════════════════════════════════════════════════════╝{RESET}")

    results = {}

    # 모든 테스트 실행
    results['env'] = test_environment_variables()
    results['docker'] = test_docker_status()
    results['backend'] = test_backend_health()
    results['sqlite'] = test_sqlite_connection()
    results['chroma'] = test_chroma_connection()
    results['openai'] = test_openai_api()

    if results['backend']:
        results['api'] = test_api_endpoints()

    # 결과 요약
    print_header("테스트 결과 요약")

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)

    print(f"\n총 테스트: {total}개")
    print_success(f"성공: {passed}개")
    if failed > 0:
        print_error(f"실패: {failed}개")
    if skipped > 0:
        print_warning(f"건너뜀: {skipped}개")

    # 최종 상태
    print()
    if failed == 0 and passed > 0:
        print_success("✨ 모든 필수 테스트 통과! 백엔드 연동 준비 완료!")
        return 0
    elif results.get('backend') and results.get('openai'):
        print_success("✓ 백엔드 서버와 OpenAI API 연결 성공")
        print_warning("⚠ 일부 데이터베이스 테스트는 Docker 내부에서만 확인 가능합니다")
        return 0
    else:
        print_error("❌ 일부 테스트 실패. 위 오류 메시지를 확인하세요")
        return 1

if __name__ == "__main__":
    sys.exit(main())
