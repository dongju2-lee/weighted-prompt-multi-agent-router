"""
LangGraph 그래프 정의 모듈 (음식 추천 에이전트 버전)
"""
from langgraph.graph import StateGraph
from .nodes import (
    AgentState,
    supervisor_node,
    refrigerator_node,
    restaurant_node,
    recipe_node,
    health_node,
    decide_next_agent
)

# Langfuse observe decorator import
try:
    from langfuse import observe
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    def observe(**kwargs):
        """Fallback decorator when Langfuse is not available"""
        def decorator(func):
            return func
        return decorator


def create_food_recommendation_graph():
    """
    음식 추천 멀티 에이전트 그래프 생성
    """
    # StateGraph 생성
    graph = StateGraph(AgentState)
    
    # 노드 추가
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("refrigerator_agent", refrigerator_node)
    graph.add_node("restaurant_agent", restaurant_node)
    graph.add_node("recipe_agent", recipe_node)
    graph.add_node("health_agent", health_node)
    
    # 엣지 추가
    graph.set_entry_point("supervisor")
    
    # 슈퍼바이저에서 각 에이전트로의 조건부 엣지
    graph.add_conditional_edges(
        "supervisor",
        decide_next_agent,
        {
            "refrigerator_agent": "refrigerator_agent",
            "restaurant_agent": "restaurant_agent", 
            "recipe_agent": "recipe_agent",
            "health_agent": "health_agent"
        }
    )
    
    # 각 에이전트에서 END로
    graph.add_edge("refrigerator_agent", "__end__")
    graph.add_edge("restaurant_agent", "__end__")
    graph.add_edge("recipe_agent", "__end__")
    graph.add_edge("health_agent", "__end__")
    
    return graph.compile()


@observe(name="multi_agent_system") if LANGFUSE_AVAILABLE else lambda x: x
async def run_multi_agent_system_async(user_query: str):
    """
    비동기 멀티 에이전트 시스템 실행
    """
    app = create_food_recommendation_graph()
    
    # 초기 상태 설정
    initial_state = {
        "messages": [],
        "user_query": user_query,
        "selected_agent": None,
        "routing_info": {},
        "final_response": {}
    }
    
    try:
        # 그래프 비동기 실행
        result = await app.ainvoke(initial_state)
        return result
        
    except Exception as e:
        print(f"❌ 시스템 실행 중 오류 발생: {e}")
        return {
            "error": str(e),
            "final_response": {
                "agent": "오류",
                "response": "시스템 오류가 발생했습니다. 다시 시도해주세요.",
                "confidence": 0.0
            }
        }


@observe(name="multi_agent_system_sync") if LANGFUSE_AVAILABLE else lambda x: x
def run_multi_agent_system(user_query: str):
    """
    동기 호환성을 위한 래퍼 함수 (기존 코드와의 호환성)
    """
    import asyncio
    
    try:
        # 이벤트 루프가 이미 실행 중인 경우 (Jupyter 등)
        loop = asyncio.get_running_loop()
        # 새로운 스레드에서 실행
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, run_multi_agent_system_async(user_query))
            return future.result()
    except RuntimeError:
        # 이벤트 루프가 없는 경우
        return asyncio.run(run_multi_agent_system_async(user_query)) 