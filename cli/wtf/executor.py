"""
명령어 실행 모듈
명령어를 실행하고 stdout/stderr를 캡처함
"""

import subprocess
import sys


class CommandExecutor:
    def run(self, command: str) -> dict:
        """
        명령어를 실행하고 출력을 캡처함

        Args:
            command: 실행할 명령어 문자열

        Returns:
            exit_code, stdout, stderr를 담은 dict
        """
        try:
            # stdout을 실시간으로 출력하면서 명령어 실행
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # stdout과 stderr 캡처
            stdout_lines = []
            stderr_lines = []

            # stdout을 실시간으로 읽기
            if process.stdout:
                for line in process.stdout:
                    sys.stdout.write(line)
                    sys.stdout.flush()
                    stdout_lines.append(line)

            # 프로세스 완료 대기하고 stderr 받기
            _, stderr = process.communicate()
            if stderr:
                sys.stderr.write(stderr)
                sys.stderr.flush()
                stderr_lines.append(stderr)

            return {
                'exit_code': process.returncode,
                'stdout': ''.join(stdout_lines),
                'stderr': ''.join(stderr_lines)
            }

        except Exception as e:
            return {
                'exit_code': 1,
                'stdout': '',
                'stderr': str(e)
            }
