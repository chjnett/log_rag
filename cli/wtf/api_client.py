"""
API 클라이언트 모듈
백엔드 API와 통신함
"""

import requests
import os
from typing import Optional


class APIClient:
    def __init__(self):
        """API 클라이언트 초기화"""
        self.base_url = os.getenv('WTF_API_URL', 'http://localhost:8000')
        self.timeout = 30

    def analyze_error(
        self,
        command: str,
        error_log: str,
        code_context: Optional[dict] = None
    ) -> dict:
        """
        에러를 백엔드로 전송해서 분석함

        Args:
            command: 실행된 명령어
            error_log: 에러 로그 출력
            code_context: 선택적 코드 컨텍스트 dict

        Returns:
            백엔드의 분석 결과

        Raises:
            API 요청 실패 시 Exception
        """
        url = f"{self.base_url}/api/analyze"

        payload = {
            "command": command,
            "error_log": error_log,
        }

        if code_context:
            payload["code_context"] = code_context

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.ConnectionError:
            raise Exception("백엔드에 연결할 수 없음. 실행 중인지 확인해봐")
        except requests.exceptions.Timeout:
            raise Exception("요청 시간 초과")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP 에러: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"예상치 못한 에러: {str(e)}")
