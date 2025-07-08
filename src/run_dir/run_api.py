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
from agent.weights import get_routing_statistics, load_routing_history, get_default_agent_weights

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

class WeightUpdateRequest(BaseModel):
    weights: Dict[str, float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "weights": {
                    "축구_에이전트": 1.2,
                    "농구_에이전트": 1.0,
                    "야구_에이전트": 0.8,
                    "테니스_에이전트": 1.1
                }
            }
        }

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🏃 운동 추천 멀티 에이전트 API",
        "version": "1.0.0",
        "description": "Vertex AI Gemini 기반 운동 추천 시스템",
        "endpoints": {
            "/sports-agent-route": "POST - 운동 추천 라우팅",
            "/query": "POST - 호환성 엔드포인트",
            "/routing-stats": "GET - 라우팅 통계 조회",
            "/routing-history": "GET - 최근 라우팅 이력 조회 (limit 파라미터 가능)",
            "/routing-history": "DELETE - 라우팅 이력 초기화",
            "/health": "GET - 헬스체크",
            "/agent-weights": "GET - 현재 에이전트 가중치 조회",
            "/agent-weights": "POST - 에이전트 가중치 업데이트"
        },
        "new_features": [
            "✨ 실제 선택 이력이 패턴에 반영됩니다",
            "📊 /routing-stats로 통계를 확인하세요",
            "📝 /routing-history로 이력을 확인하세요",
            "⚖️ /agent-weights로 가중치를 조회/수정하세요 (관리자용)"
        ]
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

@app.get("/routing-stats")
async def get_routing_stats():
    """라우팅 통계 조회"""
    try:
        stats = get_routing_statistics()
        return {
            "success": True,
            "statistics": stats,
            "message": f"총 {stats['total_requests']}번의 라우팅 기록"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")

@app.get("/routing-history")
async def get_routing_history_endpoint(limit: int = 10):
    """최근 라우팅 이력 조회"""
    try:
        history = load_routing_history()
        
        # 최신 순으로 제한된 개수만 반환
        recent_history = history[-limit:] if history else []
        recent_history.reverse()  # 최신 순으로 정렬
        
        return {
            "success": True,
            "history": recent_history,
            "total_count": len(history),
            "showing": len(recent_history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력 조회 실패: {str(e)}")

@app.delete("/routing-history")
async def clear_routing_history():
    """라우팅 이력 초기화"""
    try:
        import os
        from agent.weights import ROUTING_HISTORY_FILE
        
        if os.path.exists(ROUTING_HISTORY_FILE):
            os.remove(ROUTING_HISTORY_FILE)
            return {"success": True, "message": "라우팅 이력이 초기화되었습니다."}
        else:
            return {"success": True, "message": "이미 이력이 비어있습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력 초기화 실패: {str(e)}")

@app.get("/agent-weights")
async def get_agent_weights():
    """현재 에이전트 가중치 조회"""
    try:
        weights = get_default_agent_weights()
        return {
            "success": True,
            "weights": weights,
            "message": "현재 에이전트 가중치"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가중치 조회 실패: {str(e)}")

@app.post("/agent-weights")
async def update_agent_weights(request: WeightUpdateRequest):
    """에이전트 가중치 업데이트 (환경변수 업데이트)"""
    try:
        import os
        from dotenv import set_key
        
        # 유효한 에이전트 목록
        valid_agents = ["축구_에이전트", "농구_에이전트", "야구_에이전트", "테니스_에이전트"]
        
        # 입력 검증
        for agent, weight in request.weights.items():
            if agent not in valid_agents:
                raise HTTPException(status_code=400, detail=f"유효하지 않은 에이전트: {agent}")
            if not isinstance(weight, (int, float)) or weight <= 0:
                raise HTTPException(status_code=400, detail=f"가중치는 양수여야 합니다: {agent}={weight}")
        
        # .env 파일 경로
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        
        # 환경변수 업데이트
        updated_weights = {}
        for agent, weight in request.weights.items():
            env_key = f"WEIGHT_{agent}"
            set_key(env_file, env_key, str(weight))
            os.environ[env_key] = str(weight)  # 현재 세션에도 반영
            updated_weights[agent] = weight
        
        return {
            "success": True,
            "updated_weights": updated_weights,
            "message": f"{len(updated_weights)}개 에이전트의 가중치가 업데이트되었습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가중치 업데이트 실패: {str(e)}")

if __name__ == "__main__":
    print("🏃 운동 추천 멀티 에이전트 API 서버를 시작합니다...")
    print(get_welcome_message())
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )