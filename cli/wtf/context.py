"""
코드 컨텍스트 추출 모듈
에러 라인 주변의 소스 코드를 읽어옴
"""

import os
from typing import Optional


class ContextExtractor:
    def __init__(self, context_lines: int = 10):
        """
        컨텍스트 추출기 초기화

        Args:
            context_lines: 에러 라인 앞뒤로 포함할 라인 수
        """
        self.context_lines = context_lines

    def extract(self, file_path: str, line_number: int) -> Optional[dict]:
        """
        에러 라인 주변의 코드 컨텍스트를 추출함

        Args:
            file_path: 소스 파일 경로
            line_number: 에러가 발생한 라인 번호

        Returns:
            file_path, line_number, code_snippet, language를 담은 dict
        """
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 시작과 끝 라인 계산
            start_line = max(1, line_number - self.context_lines)
            end_line = min(len(lines), line_number + self.context_lines)

            # 스니펫 추출
            snippet_lines = []
            for i in range(start_line - 1, end_line):
                line_prefix = ">>> " if (i + 1) == line_number else "    "
                snippet_lines.append(f"{line_prefix}{i + 1:4d} | {lines[i].rstrip()}")

            # 파일 확장자에서 언어 감지
            language = self._detect_language(file_path)

            return {
                'file_path': file_path,
                'line_number': line_number,
                'code_snippet': '\n'.join(snippet_lines),
                'language': language
            }

        except Exception as e:
            return None

    def _detect_language(self, file_path: str) -> str:
        """파일 확장자에서 프로그래밍 언어를 감지함"""
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php',
        }
        return language_map.get(ext, 'text')
