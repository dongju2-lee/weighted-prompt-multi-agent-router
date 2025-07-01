"""
음식 추천 멀티 에이전트 API 서버
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

from agent.main import run_food_recommendation_system

app = FastAPI(title="음식 추천 멀티 에이전트 API", version="1.0.0")

class QueryRequest(BaseModel):
    user_query: str
    query: str = None  # 이전 호환성을 위해

@app.post("/food-agent-route")
async def route_food_query(request: QueryRequest) -> Dict[str, Any]:
    """
    음식 추천 에이전트 라우팅 엔드포인트
    """
    try:
        # user_query 또는 query 필드 사용 (이전 호환성)
        query = request.user_query or request.query
        if not query:
            raise HTTPException(status_code=400, detail="user_query 또는 query 필드가 필요합니다.")
        
        result = await run_food_recommendation_system(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 중 오류 발생: {str(e)}")

@app.post("/query")  # 이전 호환성을 위한 엔드포인트
async def route_query_legacy(request: QueryRequest) -> Dict[str, Any]:
    """
    이전 호환성을 위한 엔드포인트
    """
    return await route_food_query(request)

@app.get("/")
async def root():
    return {"message": "음식 추천 멀티 에이전트 API 서버가 실행 중입니다."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🍽️ 음식 추천 멀티 에이전트 API 서버를 시작합니다...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 