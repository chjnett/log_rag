import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from app.core.config import settings as app_settings
from app.services.ai import AIService
import uuid
import os


class VectorStore:
    def __init__(self):
        # chroma 디렉토리 존재하는지 확인
        os.makedirs(app_settings.chroma_persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=app_settings.chroma_persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="error_embeddings",
            metadata={"hnsw:space": "cosine"}
        )
        self.ai_service = AIService()

    async def add_error(
        self,
        error_log: str,
        metadata: Dict
    ) -> str:
        """
        벡터 스토어에 에러를 추가함

        Returns:
            vector_id (str)
        """
        try:
            # 임베딩 가져오기
            embedding = await self.ai_service.get_embedding(error_log)

            # ID 생성
            vector_id = str(uuid.uuid4())

            # 컬렉션에 추가
            self.collection.add(
                ids=[vector_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[error_log[:1000]]  # 잘린 에러 로그 저장
            )

            return vector_id

        except Exception as e:
            print(f"벡터 스토어 추가 실패: {e}")
            return None

    async def search_similar(
        self,
        error_log: str,
        threshold: float = 0.8,
        limit: int = 3
    ) -> List[Dict]:
        """
        유사한 에러를 검색함

        Returns:
            id, case_name, root_cause, solution, similarity를 담은 dict 리스트
        """
        try:
            # 쿼리용 임베딩 가져오기
            embedding = await self.ai_service.get_embedding(error_log)

            # 컬렉션에서 검색
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=limit
            )

            similar_cases = []

            if results['ids'] and results['ids'][0]:
                for i, error_id in enumerate(results['ids'][0]):
                    # 거리에서 유사도 계산
                    # ChromaDB는 코사인 거리를 반환하므로 유사도로 변환
                    distance = results['distances'][0][i]
                    similarity = 1 - distance

                    # 임계값 이상인 것만 포함
                    if similarity >= threshold:
                        metadata = results['metadatas'][0][i]
                        similar_cases.append({
                            "id": error_id,
                            "case_name": metadata.get("case_name", "Unknown"),
                            "root_cause": metadata.get("root_cause", "N/A"),
                            "solution": metadata.get("solution", "N/A"),
                            "similarity": round(similarity, 2)
                        })

            return similar_cases

        except Exception as e:
            print(f"유사 에러 검색 실패: {e}")
            return []
