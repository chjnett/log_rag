"""
Traceback 파서 모듈
에러 로그에서 파일 경로와 라인 번호를 추출함
"""

import re
from typing import Optional


class TracebackParser:
    def parse(self, error_log: str) -> dict:
        """
        traceback을 파싱해서 파일 경로와 라인 번호를 추출함

        지원하는 형식:
        - Python: File "path/to/file.py", line 42
        - Node.js: at /path/to/file.js:42:10
        - Java: at ClassName.method(FileName.java:42)

        Returns:
            file_path, line_number, language를 담은 dict
        """
        # Python 패턴
        python_pattern = r'File "([^"]+)", line (\d+)'
        match = re.search(python_pattern, error_log)
        if match:
            return {
                'file_path': match.group(1),
                'line_number': int(match.group(2)),
                'language': 'python'
            }

        # Node.js 패턴
        node_pattern = r'at .+ \(([^:]+):(\d+):\d+\)'
        match = re.search(node_pattern, error_log)
        if match:
            return {
                'file_path': match.group(1),
                'line_number': int(match.group(2)),
                'language': 'javascript'
            }

        # Node.js 대체 패턴
        node_pattern2 = r'at ([^:]+):(\d+):\d+'
        match = re.search(node_pattern2, error_log)
        if match and not match.group(1).startswith('Object.'):
            return {
                'file_path': match.group(1),
                'line_number': int(match.group(2)),
                'language': 'javascript'
            }

        # Java 패턴
        java_pattern = r'at .+\(([^:]+):(\d+)\)'
        match = re.search(java_pattern, error_log)
        if match:
            return {
                'file_path': match.group(1),
                'line_number': int(match.group(2)),
                'language': 'java'
            }

        # traceback을 찾지 못함
        return {
            'file_path': None,
            'line_number': None,
            'language': 'unknown'
        }
