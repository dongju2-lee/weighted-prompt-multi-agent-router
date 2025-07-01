"""
LangGraph 워크플로우 정의 (운동 추천 에이전트 버전)
"""
from langgraph.graph import StateGraph, END
from .nodes import (
    AgentState,
    supervisor_node,
    soccer_node,
    basketball_node,
    baseball_node,
    tennis_node,
    should_continue
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


def create_sports_agent_graph():
    """운동 추천 멀티 에이전트 그래프 생성"""
    
    # StateGraph 생성 (AgentState 타입 지정)
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("soccer", soccer_node)
    workflow.add_node("basketball", basketball_node)
    workflow.add_node("baseball", baseball_node)
    workflow.add_node("tennis", tennis_node)
    
    # 시작점 설정
    workflow.set_entry_point("supervisor")
    
    # 조건부 엣지 추가 (슈퍼바이저 → 각 에이전트)
    workflow.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "soccer": "soccer",
            "basketball": "basketball",
            "baseball": "baseball",
            "tennis": "tennis"
        }
    )
    
    # 각 에이전트에서 END로 가는 엣지
    workflow.add_edge("soccer", END)
    workflow.add_edge("basketball", END)
    workflow.add_edge("baseball", END)
    workflow.add_edge("tennis", END)
    
    # 그래프 컴파일
    app = workflow.compile()
    
    return app


@observe(name="multi_agent_system") if LANGFUSE_AVAILABLE else lambda x: x
async def run_sports_agent_workflow(user_query: str):
    """운동 추천 워크플로우 실행"""
    try:
        # 그래프 생성
        app = create_sports_agent_graph()
        
        # 초기 상태 설정 (딕셔너리로 설정)
        initial_state = {
            "messages": [],
            "user_query": user_query,
            "selected_agent": "",
            "agent_response": {},
            "routing_info": {}
        }
        
        # 워크플로우 실행
        result = await app.ainvoke(initial_state)
        
        return {
            "success": True,
            "user_query": user_query,
            "selected_agent": result["selected_agent"],
            "agent_response": result["agent_response"],
            "routing_info": result["routing_info"]
        }
        
    except Exception as e:
        print(f"❌ 워크플로우 실행 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "user_query": user_query
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
            future = executor.submit(asyncio.run, run_sports_agent_workflow(user_query))
            return future.result()
    except RuntimeError:
        # 이벤트 루프가 없는 경우
        return asyncio.run(run_sports_agent_workflow(user_query)) 