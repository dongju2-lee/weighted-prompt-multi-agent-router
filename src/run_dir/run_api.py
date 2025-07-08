"""
FastAPI 기반 운동 추천 멀티 에이전트 API 서버
"""
import sys
import os
# run_dir에서 실행할 때 상위 디렉토리(src)를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # run_dir 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # src 추가

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from agent.graph import run_sports_agent_workflow
from agent.utils import validate_environment
from agent.prompts import get_welcome_message

# 환경 변수 검증
if not validate_environment():
    sys.exit(1)

app = FastAPI(
    title="🏃 운동 추천 멀티 에이전트 API",
    description="Vertex AI Gemini 기반 운동 추천 멀티 에이전트 시스템",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str
    user_query: str = None  # 이전 버전 호환성

class QueryResponse(BaseModel):
    success: bool
    user_query: str
    selected_agent: str = None
    agent_response: Dict[str, Any] = None
    routing_info: Dict[str, Any] = None
    error: str = None

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🏃 운동 추천 멀티 에이전트 API",
        "version": "1.0.0",
        "description": "Vertex AI Gemini 기반 운동 추천 시스템",
        "endpoints": {
            "/sports-agent-route": "POST - 운동 추천 라우팅",
            "/query": "POST - 호환성 엔드포인트"
        }
    }

@app.post("/sports-agent-route", response_model=QueryResponse)
async def sports_agent_route(request: QueryRequest):
    """운동 추천 에이전트 라우팅"""
    try:
        # 쿼리 추출 (이전 버전 호환성)
        user_query = request.query or request.user_query
        
        if not user_query:
            raise HTTPException(status_code=400, detail="query 또는 user_query 필드가 필요합니다.")
        
        print(f"\n🏃 운동 추천 요청: {user_query}")
        
        # 멀티 에이전트 워크플로우 실행
        result = await run_sports_agent_workflow(user_query)
        
        if result.get("success"):
            return QueryResponse(
            success=True,
                user_query=user_query,
                selected_agent=result["selected_agent"],
                agent_response=result["agent_response"],
                routing_info=result["routing_info"]
            )
        else:
            return QueryResponse(
                success=False,
                user_query=user_query,
                error=result.get("error", "알 수 없는 오류")
            )
            
    except Exception as e:
        print(f"❌ API 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """호환성을 위한 기존 엔드포인트"""
    return await sports_agent_route(request)

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "service": "sports-agent-api"}

if __name__ == "__main__":
    print("🏃 운동 추천 멀티 에이전트 API 서버를 시작합니다...")
    print(get_welcome_message())
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )