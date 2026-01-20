"""
민감정보 처리 모듈
에러 로그와 코드에서 민감한 정보를 제거함
"""

import re
import os
from dotenv import load_dotenv

load_dotenv()


class Sanitizer:
    def __init__(self):
        """마스킹할 패턴들로 sanitizer 초기화"""
        self.patterns = [
            # API 키와 토큰
            (r'(api[_-]?key|token|password|secret)["\s]*[=:]["\s]*([^\s"\']+)', r'\1=***'),
            # 환경 변수 패턴
            (r'([A-Z_]+)["\s]*=["\s]*([^\s"\']+)', self._mask_env_var),
            # IP 주소
            (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'xxx.xxx.xxx.xxx'),
            # 홈 디렉토리 경로
            (re.escape(os.path.expanduser('~')), '~'),
        ]

    def sanitize(self, text: str) -> str:
        """
        텍스트에서 민감한 정보를 제거함

        Args:
            text: 처리할 텍스트

        Returns:
            민감정보가 제거된 텍스트
        """
        result = text

        for pattern, replacement in self.patterns:
            if callable(replacement):
                result = re.sub(pattern, replacement, result)
            else:
                result = re.sub(pattern, replacement, result)

        return result

    def _mask_env_var(self, match):
        """환경 변수가 존재하면 마스킹함"""
        var_name = match.group(1)
        if os.getenv(var_name):
            return f'{var_name}=***'
        return match.group(0)
