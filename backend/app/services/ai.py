from openai import AsyncOpenAI
from app.core.config import settings
import json
from typing import Dict


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def analyze_error(self, prompt: str) -> Dict:
        """
        GPT-4o-mini를 호출해서 에러를 분석함

        Returns:
            case_name, root_cause, solution, tags를 담은 Dict
        """
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "너는 숙련된 시니어 개발자다. 에러를 분석하고 JSON 형식으로만 응답한다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            analysis = json.loads(content)

            # 필수 필드 검증
            required_fields = ["case_name", "root_cause", "solution", "tags"]
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"필수 필드 누락: {field}")

            return analysis

        except Exception as e:
            # AI 실패 시 대체 응답 반환
            return {
                "case_name": "Error Analysis Failed",
                "root_cause": f"AI 분석 중 오류 발생: {str(e)}",
                "solution": "수동으로 에러 로그를 확인해주세요.",
                "tags": ["error", "ai-failed"]
            }

    async def get_embedding(self, text: str) -> list:
        """
        텍스트의 임베딩 벡터를 가져옴

        Returns:
            임베딩을 나타내는 float 리스트
        """
        try:
            response = await self.client.embeddings.create(
                model=settings.openai_embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"임베딩 가져오기 실패: {str(e)}")
