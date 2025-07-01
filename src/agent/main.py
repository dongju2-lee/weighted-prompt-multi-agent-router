"""
음식 추천 멀티 에이전트 시스템 메인 모듈
"""
import asyncio
from typing import Dict, Any
from .graph import create_food_recommendation_graph
from .nodes import AgentState

async def run_food_recommendation_system(user_query: str) -> Dict[str, Any]:
    """
    음식 추천 멀티 에이전트 시스템 실행
    """
    app = create_food_recommendation_graph()
    
    # 초기 상태 설정
    initial_state: AgentState = {
        "messages": [],
        "user_query": user_query,
        "selected_agent": "",
        "routing_info": {},
        "final_response": {}
    }
    
    # 그래프 실행
    result = await app.ainvoke(initial_state)
    
    return {
        "user_query": user_query,
        "selected_agent": result.get("selected_agent"),
        "routing_info": result.get("routing_info", {}),
        "final_response": result.get("final_response", {}),
        "status": "success"
    }

if __name__ == "__main__":
    async def main():
        # 테스트 실행
        test_query = "음식 추천해줘"
        result = await run_food_recommendation_system(test_query)
        print(f"결과: {result}")
    
    asyncio.run(main()) 