"""
노드 정의 모듈 (운동 추천 에이전트 버전)
"""
import asyncio
from typing import Dict, Any, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from .agents import soccer_agent, basketball_agent, baseball_agent, tennis_agent
from .weights import get_mock_routing_data, get_default_agent_weights, apply_weights_and_normalize
from .prompts import generate_supervisor_prompt
from .utils import initialize_gemini_model, extract_agent_name


class AgentState(TypedDict):
    """에이전트 상태 클래스"""
    messages: Annotated[list, add_messages]
    user_query: str
    selected_agent: str
    agent_response: Dict[str, Any]
    routing_info: Dict[str, Any]


async def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    슈퍼바이저 노드: Gemini를 통해 적절한 에이전트 선택
    """
    try:
        # 과거 패턴 데이터 생성
        base_ratios, total_traces = get_mock_routing_data(state["user_query"])
        
        # 가중치 적용
        agent_weights = get_default_agent_weights()
        normalized_ratios = apply_weights_and_normalize(base_ratios, agent_weights)
        
        # 슈퍼바이저 프롬프트 생성
        supervisor_prompt = generate_supervisor_prompt(
            state["user_query"], 
            normalized_ratios, 
            total_traces
        )
        
        # 매번 프롬프트 출력
        print(f"\n{'='*60}")
        print("🔍 SUPERVISOR PROMPT")
        print(f"{'='*60}")
        print(supervisor_prompt)
        print(f"{'='*60}")
        
        # Gemini 모델 호출
        model = initialize_gemini_model()
        
        # 비동기 처리를 위해 executor 사용
        loop = asyncio.get_event_loop()
        gemini_response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(supervisor_prompt).text
        )
        
        # 에이전트 이름 추출
        selected_agent = extract_agent_name(gemini_response)
        
        # 라우팅 정보
        routing_info = {
            "normalized_ratios": normalized_ratios,
            "total_traces": total_traces,
            "gemini_response": gemini_response,
            "agent_weights": agent_weights
        }
        
        print(f"\n🤖 Gemini 슈퍼바이저 분석:")
        print(f"   선택된 에이전트: {selected_agent}")
        print(f"   참고 데이터: {total_traces}회")
        
        return {
            "selected_agent": selected_agent,
            "routing_info": routing_info
        }
        
    except Exception as e:
        print(f"❌ 슈퍼바이저 노드 오류: {e}")
        # 기본 에이전트로 폴백
        return {
            "selected_agent": "축구_에이전트",
            "routing_info": {"error": str(e)}
        }


async def soccer_node(state: AgentState) -> Dict[str, Any]:
    """축구 에이전트 노드"""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            soccer_agent,
            state["user_query"]
        )
        return {"agent_response": response}
    except Exception as e:
        print(f"❌ 축구 에이전트 오류: {e}")
        return {
            "agent_response": {
                "agent": "축구_에이전트",
                "answer": "죄송합니다. 축구 추천 중 오류가 발생했습니다.",
                "detail": "시스템 오류로 인해 정상적인 추천을 제공할 수 없습니다."
            }
        }


async def basketball_node(state: AgentState) -> Dict[str, Any]:
    """농구 에이전트 노드"""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            basketball_agent,
            state["user_query"]
        )
        return {"agent_response": response}
    except Exception as e:
        print(f"❌ 농구 에이전트 오류: {e}")
    return {
            "agent_response": {
                "agent": "농구_에이전트",
                "answer": "죄송합니다. 농구 추천 중 오류가 발생했습니다.",
                "detail": "시스템 오류로 인해 정상적인 추천을 제공할 수 없습니다."
        }
    }


async def baseball_node(state: AgentState) -> Dict[str, Any]:
    """야구 에이전트 노드"""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            baseball_agent,
            state["user_query"]
        )
        return {"agent_response": response}
    except Exception as e:
        print(f"❌ 야구 에이전트 오류: {e}")
    return {
            "agent_response": {
                "agent": "야구_에이전트",
                "answer": "죄송합니다. 야구 추천 중 오류가 발생했습니다.",
                "detail": "시스템 오류로 인해 정상적인 추천을 제공할 수 없습니다."
        }
    }


async def tennis_node(state: AgentState) -> Dict[str, Any]:
    """테니스 에이전트 노드"""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            tennis_agent,
            state["user_query"]
        )
        return {"agent_response": response}
    except Exception as e:
        print(f"❌ 테니스 에이전트 오류: {e}")
    return {
            "agent_response": {
                "agent": "테니스_에이전트",
                "answer": "죄송합니다. 테니스 추천 중 오류가 발생했습니다.",
                "detail": "시스템 오류로 인해 정상적인 추천을 제공할 수 없습니다."
        }
    }


def should_continue(state: AgentState) -> str:
    """
    다음 노드 결정 함수
    """
    selected_agent = state["selected_agent"]
    
    if selected_agent == "축구_에이전트":
        return "soccer"
    elif selected_agent == "농구_에이전트":
        return "basketball"
    elif selected_agent == "야구_에이전트":
        return "baseball"
    elif selected_agent == "테니스_에이전트":
        return "tennis"
    else:
        # 기본값
        return "soccer"


# 노드 매핑
NODE_MAPPING = {
    "supervisor": supervisor_node,
    "soccer": soccer_node,
    "basketball": basketball_node,
    "baseball": baseball_node,
    "tennis": tennis_node
} 