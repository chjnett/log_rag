#!/usr/bin/env python3
"""
CLI-Mate: AI 기반 에러 분석 도구

사용법:
    wtf <command>
    wtf python test.py
    wtf npm run build
"""

import click
import sys
from wtf.executor import CommandExecutor
from wtf.parser import TracebackParser
from wtf.context import ContextExtractor
from wtf.sanitizer import Sanitizer
from wtf.api_client import APIClient


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('command', nargs=-1, type=click.UNPROCESSED, required=True)
def cli(command):
    """
    명령어를 실행하고 발생하는 에러를 분석함

    예시:
        wtf python test.py
        wtf npm run build
    """
    cmd_string = ' '.join(command)

    # 컴포넌트 초기화
    executor = CommandExecutor()
    parser = TracebackParser()
    context_extractor = ContextExtractor()
    sanitizer = Sanitizer()
    api_client = APIClient()

    # 명령어 실행
    result = executor.run(cmd_string)

    # stdout은 실시간으로 출력됨 (executor에서 처리)
    # 명령어가 실패했는지 확인
    if result['exit_code'] != 0 and result['stderr']:
        stderr = result['stderr']

        # traceback 파싱
        traceback_info = parser.parse(stderr)

        # 파일과 라인 번호를 찾으면 코드 컨텍스트 추출
        code_context = None
        if traceback_info['file_path'] and traceback_info['line_number']:
            code_context = context_extractor.extract(
                file_path=traceback_info['file_path'],
                line_number=traceback_info['line_number']
            )

        # 민감한 정보 마스킹
        sanitized_error = sanitizer.sanitize(stderr)
        if code_context:
            code_context['code_snippet'] = sanitizer.sanitize(code_context['code_snippet'])

        # 백엔드로 전송해서 분석
        try:
            click.echo("\n🔍 Analyzing error with AI...", err=True)
            analysis = api_client.analyze_error(
                command=cmd_string,
                error_log=sanitized_error,
                code_context=code_context
            )

            # 분석 결과 표시
            click.echo("\n" + "="*50, err=True)
            click.echo(f"📌 {analysis['case_name']}", err=True)
            click.echo("="*50, err=True)
            click.echo(f"\n💡 Root Cause:\n{analysis['root_cause']}\n", err=True)
            click.echo(f"🔧 Solution:\n{analysis['solution']}\n", err=True)
            click.echo(f"🏷️  Tags: {', '.join(analysis['tags'])}", err=True)

            if analysis.get('similar_cases'):
                click.echo(f"\n📚 Found {len(analysis['similar_cases'])} similar past cases", err=True)

            click.echo(f"\n🌐 View details: http://localhost:3000/errors/{analysis['id']}", err=True)

        except Exception as e:
            click.echo(f"\n⚠️  Failed to analyze error: {e}", err=True)

    # 원래 명령어와 동일한 exit code로 종료
    sys.exit(result['exit_code'])


if __name__ == '__main__':
    cli()
