from typing import Optional, Dict, List
from app.services.vector_store import VectorStore
from app.services.ai import AIService
from app.core.config import settings

vector_store = VectorStore()
ai_service = AIService()


async def analyze_error(
    error_log: str,
    code_context: Optional[Dict] = None
) -> Dict:
    """
    RAG 파이프라인으로 에러를 분석함

    1. ChromaDB에서 과거 유사 에러 검색
    2. 유사 사례들로 컨텍스트 구성
    3. GPT-4o-mini 호출해서 분석
    4. ChromaDB에 임베딩 저장

    Returns:
        case_name, root_cause, solution, tags, similar_cases, vector_id를 담은 Dict
    """

    # 유사한 에러 검색
    similar_cases = await vector_store.search_similar(
        error_log=error_log,
        threshold=settings.similarity_threshold,
        limit=settings.max_similar_cases
    )

    # 컨텍스트로 프롬프트 구성
    prompt = _build_analysis_prompt(
        error_log=error_log,
        code_context=code_context,
        similar_cases=similar_cases
    )

    # AI 분석 받기
    analysis = await ai_service.analyze_error(prompt)

    # 미래 유사도 검색을 위해 임베딩 저장
    vector_id = await vector_store.add_error(
        error_log=error_log,
        metadata={
            "case_name": analysis["case_name"],
            "tags": analysis["tags"]
        }
    )

    analysis["vector_id"] = vector_id
    analysis["similar_cases"] = [
        {
            "id": case["id"],
            "case_name": case["case_name"],
            "similarity": case["similarity"]
        }
        for case in similar_cases
    ]

    return analysis


def _build_analysis_prompt(
    error_log: str,
    code_context: Optional[Dict],
    similar_cases: List[Dict]
) -> str:
    """AI 분석용 종합 프롬프트를 만듦"""

    prompt_parts = [
        "너는 숙련된 시니어 개발자다. 아래 정보를 바탕으로 에러를 분석해라.\n"
    ]

    # 유사 사례가 있으면 추가
    if similar_cases:
        prompt_parts.append("## 과거 유사 에러 해결 사례\n")
        for i, case in enumerate(similar_cases, 1):
            prompt_parts.append(f"### 사례 {i}: {case['case_name']}\n")
            prompt_parts.append(f"원인: {case.get('root_cause', 'N/A')}\n")
            prompt_parts.append(f"해결: {case.get('solution', 'N/A')}\n\n")

    # 현재 에러 추가
    prompt_parts.append("## 현재 에러 로그\n")
    prompt_parts.append(f"```\n{error_log}\n```\n\n")

    # 코드 컨텍스트가 있으면 추가
    if code_context:
        prompt_parts.append("## 에러 발생 지점 소스 코드\n")
        prompt_parts.append(f"파일: {code_context.get('file_path', 'unknown')}\n")
        prompt_parts.append(f"라인: {code_context.get('line_number', 'unknown')}\n")
        prompt_parts.append(f"```{code_context.get('language', 'python')}\n")
        prompt_parts.append(f"{code_context.get('code_snippet', '')}\n```\n\n")

    # 출력 형식 지시사항 추가
    prompt_parts.append("""
위 정보를 바탕으로 에러를 분석하고 다음 JSON 형식으로 응답해라:
{
  "case_name": "직관적인 에러 이름 (예: NameError: undefined variable 'x')",
  "root_cause": "에러의 근본 원인 분석 (2-3문장)",
  "solution": "해결 방법 (코드 예시 포함, 마크다운 형식)",
  "tags": ["언어 또는 프레임워크", "에러 타입"]
}

반드시 JSON 형식으로만 응답하고, 다른 설명은 추가하지 마라.
""")

    return "".join(prompt_parts)
