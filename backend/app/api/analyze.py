from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.database import get_db, ErrorLog
from app.services.rag import analyze_error
import uuid
import json

router = APIRouter()


class CodeContext(BaseModel):
    file_path: str
    line_number: int
    code_snippet: str
    language: str = "python"


class AnalyzeRequest(BaseModel):
    command: str
    error_log: str
    code_context: Optional[CodeContext] = None


class SimilarCase(BaseModel):
    id: str
    case_name: str
    similarity: float


class AnalyzeResponse(BaseModel):
    id: str
    case_name: str
    root_cause: str
    solution: str
    tags: List[str]
    similar_cases: List[SimilarCase]


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_error_endpoint(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    AI로 에러 로그를 분석하고 데이터베이스에 저장함
    """
    try:
        # 고유 ID 생성
        error_id = str(uuid.uuid4())

        # RAG로 에러 분석
        analysis = await analyze_error(
            error_log=request.error_log,
            code_context=request.code_context.dict() if request.code_context else None
        )

        # 데이터베이스에 저장
        error_record = ErrorLog(
            id=error_id,
            case_name=analysis["case_name"],
            command=request.command,
            error_log=request.error_log,
            code_snippet=request.code_context.code_snippet if request.code_context else None,
            file_path=request.code_context.file_path if request.code_context else None,
            line_number=request.code_context.line_number if request.code_context else None,
            ai_solution=analysis["solution"],
            root_cause=analysis["root_cause"],
            tags=json.dumps(analysis["tags"]),
            vector_id=analysis.get("vector_id")
        )

        db.add(error_record)
        db.commit()

        return AnalyzeResponse(
            id=error_id,
            case_name=analysis["case_name"],
            root_cause=analysis["root_cause"],
            solution=analysis["solution"],
            tags=analysis["tags"],
            similar_cases=analysis.get("similar_cases", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors")
async def get_errors(
    page: int = 1,
    limit: int = 20,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    페이지네이션과 함께 에러 목록을 가져옴
    """
    query = db.query(ErrorLog)

    if tag:
        query = query.filter(ErrorLog.tags.contains(tag))

    total = query.count()
    errors = query.order_by(ErrorLog.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "errors": [
            {
                "id": e.id,
                "case_name": e.case_name,
                "command": e.command,
                "tags": json.loads(e.tags) if e.tags else [],
                "created_at": e.created_at.isoformat()
            }
            for e in errors
        ]
    }


@router.get("/errors/{error_id}")
async def get_error_detail(
    error_id: str,
    db: Session = Depends(get_db)
):
    """
    에러의 상세 정보를 가져옴
    """
    error = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()

    if not error:
        raise HTTPException(status_code=404, detail="에러를 찾을 수 없음")

    return {
        "id": error.id,
        "case_name": error.case_name,
        "command": error.command,
        "error_log": error.error_log,
        "code_snippet": error.code_snippet,
        "file_path": error.file_path,
        "line_number": error.line_number,
        "ai_solution": error.ai_solution,
        "root_cause": error.root_cause,
        "tags": json.loads(error.tags) if error.tags else [],
        "created_at": error.created_at.isoformat()
    }
