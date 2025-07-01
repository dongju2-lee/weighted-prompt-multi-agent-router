"""
LangGraph 노드 정의 모듈 (음식 추천 에이전트 버전)
"""
import asyncio
import os
import time
from typing import Dict, Any, Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from .utils import initialize_gemini_model, extract_agent_name, initialize_langfuse
from .weights import get_mock_routing_data, apply_weights_and_normalize, get_default_agent_weights
from .prompts import generate_supervisor_prompt
from .agents import (
    refrigerator_recipe_agent,
    restaurant_recommendation_agent,
    recipe_search_agent,
    health_food_consulting_agent
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


class AgentState(TypedDict):
    """
    에이전트 상태 정의
    """
    messages: Annotated[list, add_messages]
    user_query: str
    selected_agent: str
    routing_info: Dict[str, Any]
    final_response: Dict[str, Any]


@observe(name="supervisor_routing") if LANGFUSE_AVAILABLE else lambda x: x
async def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """
    과거 패턴을 참고해서 Gemini가 직접 라우팅을 결정하는 슈퍼바이저 노드 (음식 추천 에이전트)
    """
    user_query = state["user_query"]
    
    try:
        # 1. 과거 패턴 분석
        base_ratios, total_traces = get_mock_routing_data(user_query)
        
        # 2. 가중치 적용
        agent_weights = get_default_agent_weights()
        normalized_ratios = apply_weights_and_normalize(base_ratios, agent_weights)
        
        # 3. Gemini에게 과거 패턴 정보를 제공하고 직접 라우팅 결정하게 함
        supervisor_prompt = generate_supervisor_prompt(user_query, normalized_ratios, total_traces)
        model = initialize_gemini_model()
        
        # Vertex AI 직접 호출
        response = await asyncio.get_event_loop().run_in_executor(
            None, model.generate_content, supervisor_prompt
        )
        gemini_response = response.text
        selected_agent = extract_agent_name(gemini_response)
        
        routing_info = {
            "routing_method": "Vertex_AI_Gemini_라우팅",
            "gemini_response": gemini_response,
            "normalized_ratios": normalized_ratios,
            "total_traces": total_traces,
            "supervisor_prompt": supervisor_prompt,  # 프롬프트 포함
            "gemini_selected_agent": selected_agent
        }
        
        return {
            "selected_agent": selected_agent,
            "routing_info": routing_info
        }
        
    except Exception as e:
        print(f"❌ Supervisor 노드 오류: {e}")
        return {
            "selected_agent": "냉장고_재료_에이전트",  # 기본값
            "routing_info": {
                "routing_method": "오류_기본값",
                "error": str(e)
            }
        }


@observe(name="refrigerator_agent") if LANGFUSE_AVAILABLE else lambda x: x
async def refrigerator_node(state: AgentState) -> Dict[str, Any]:
    """냉장고 재료 에이전트 노드"""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, refrigerator_recipe_agent, state["user_query"])
    return {"final_response": response}


@observe(name="restaurant_agent") if LANGFUSE_AVAILABLE else lambda x: x
async def restaurant_node(state: AgentState) -> Dict[str, Any]:
    """음식점 추천 에이전트 노드"""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, restaurant_recommendation_agent, state["user_query"])
    return {"final_response": response}


@observe(name="recipe_agent") if LANGFUSE_AVAILABLE else lambda x: x
async def recipe_node(state: AgentState) -> Dict[str, Any]:
    """레시피 검색 에이전트 노드"""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, recipe_search_agent, state["user_query"])
    return {"final_response": response}


@observe(name="health_agent") if LANGFUSE_AVAILABLE else lambda x: x
async def health_node(state: AgentState) -> Dict[str, Any]:
    """건강식 컨설팅 에이전트 노드"""
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, health_food_consulting_agent, state["user_query"])
    return {"final_response": response}


# 라우팅 조건 함수들
def route_to_refrigerator(state: AgentState) -> bool:
    return state["selected_agent"] == "냉장고_재료_에이전트"

def route_to_restaurant(state: AgentState) -> bool:
    return state["selected_agent"] == "음식점_추천_에이전트"

def route_to_recipe(state: AgentState) -> bool:
    return state["selected_agent"] == "레시피_검색_에이전트"

def route_to_health(state: AgentState) -> bool:
    return state["selected_agent"] == "건강식_컨설팅_에이전트"


def decide_next_agent(state: AgentState) -> str:
    """다음 실행할 에이전트 결정 (동기 함수 유지)"""
    selected_agent = state.get("selected_agent")
    
    # 에이전트 이름을 노드 이름으로 매핑
    agent_mapping = {
        "냉장고_재료_에이전트": "refrigerator_agent",
        "음식점_추천_에이전트": "restaurant_agent",
        "레시피_검색_에이전트": "recipe_agent",
        "건강식_컨설팅_에이전트": "health_agent"
    }
    
    return agent_mapping.get(selected_agent, "refrigerator_agent") 