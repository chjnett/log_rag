from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api import analyze

app = FastAPI(
    title="CLI-Mate API",
    description="AI-Powered Error Analysis and Knowledge Base",
    version="1.0.0"
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 시작 시 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    init_db()

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cli-mate-backend"}

# 라우터 포함
app.include_router(analyze.router, prefix="/api", tags=["analyze"])

@app.get("/")
async def root():
    return {
        "message": "CLI-Mate API",
        "version": "1.0.0",
        "docs": "/docs"
    }
