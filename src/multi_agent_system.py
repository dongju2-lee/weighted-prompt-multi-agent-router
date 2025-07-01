"""
LangGraph 기반 가중치 프롬프트 멀티 에이전트 라우터 시스템
"""
import json
import sys
import os
from typing import Dict, Any, TypedDict, Annotated
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from agents import AGENTS
from weighted_router import simple_supervisor_routing, get_mock_routing_data, apply_weights_and_normalize, generate_supervisor_prompt

# 환경 변수 로드
load_dotenv()


# Vertex AI 모델 초기화
def initialize_gemini_model():
    """Vertex AI Gemini 모델 초기화"""
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_VERTEXAI_LOCATION", "us-central1")
    model_name = os.getenv("SUPERVISOR_MODEL", "gemini-2.0-flash")
    
    if not project_id:
        raise ValueError("GCP_PROJECT_ID 환경변수가 설정되지 않았습니다.")
    
    return ChatVertexAI(
        model_name=model_name,
        project=project_id,
        location=location,
        temperature=0.1,
        max_output_tokens=1024,
    )


class AgentState(TypedDict):
    """에이전트 상태 정의"""
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: str
    user_query: str
    routing_info: Dict[str, Any]
    final_response: Dict[str, Any]


def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """슈퍼바이저 노드 - Gemini 모델을 사용한 가중치 기반 라우팅"""
    user_query = state["user_query"]
    
    # 현재 설정된 가중치 (예시: A/B 테스트나 에이전트 조정)
    agent_weights = {
        "냉장고_재료_에이전트": 0.0,
        "음식점_추천_에이전트": 1.0, 
        "레시피_검색_에이전트": 1.0,
        "건강식_컨설팅_에이전트": 1.0  # 건강식 에이전트를 20% 더 우선
    }
    
    # 과거 패턴 분석 및 가중치 적용
    base_ratios, total_traces = get_mock_routing_data(user_query)
    normalized_ratios = apply_weights_and_normalize(base_ratios, agent_weights)
    
    # Gemini 모델을 사용한 라우팅 결정
    try:
        gemini_model = initialize_gemini_model()
        
        # 가중치 기반 프롬프트 생성
        supervisor_prompt = generate_supervisor_prompt(user_query, normalized_ratios, total_traces)
        
        # Gemini 모델 호출
        response = gemini_model.invoke([HumanMessage(content=supervisor_prompt)])
        
        # 응답에서 에이전트 이름 추출
        selected_agent = extract_agent_name(response.content)
        
        print(f"\n=== Gemini 슈퍼바이저 분석 결과 ===")
        print(f"질문: {user_query}")
        print(f"참고한 과거 데이터: {total_traces}개")
        print("과거 라우팅 패턴:")
        for agent, percentage in normalized_ratios.items():
            mark = "★" if agent == selected_agent else " "
            print(f"  {mark} {agent}: {percentage:.1f}%")
        print(f"Gemini 선택 결과: {selected_agent}")
        print("=" * 40)
        
    except Exception as e:
        print(f"⚠️  Gemini 모델 호출 실패, 대체 라우팅 사용: {e}")
        # 대체 라우팅
        selected_agent = simple_supervisor_routing(user_query, agent_weights)
    
    # 라우팅 정보 저장
    routing_info = {
        "selected_agent": selected_agent,
        "base_ratios": base_ratios,
        "agent_weights": agent_weights,
        "normalized_ratios": normalized_ratios,
        "total_traces": total_traces
    }
    
    return {
        "next_agent": selected_agent,
        "routing_info": routing_info,
        "messages": [AIMessage(content=f"Gemini 슈퍼바이저가 {selected_agent}를 선택했습니다.")]
    }


def extract_agent_name(response_content: str) -> str:
    """Gemini 응답에서 에이전트 이름 추출"""
    available_agents = [
        "냉장고_재료_에이전트",
        "음식점_추천_에이전트", 
        "레시피_검색_에이전트",
        "건강식_컨설팅_에이전트"
    ]
    
    response_lower = response_content.lower()
    
    # 응답에서 에이전트 이름 찾기
    for agent in available_agents:
        if agent in response_content or agent.replace("_", " ") in response_lower:
            return agent
    
    # 키워드 기반 매칭
    if any(word in response_lower for word in ['냉장고', '재료', '집에서']):
        return "냉장고_재료_에이전트"
    elif any(word in response_lower for word in ['음식점', '식당', '외식']):
        return "음식점_추천_에이전트"
    elif any(word in response_lower for word in ['레시피', '요리법', '만드는법']):
        return "레시피_검색_에이전트"
    elif any(word in response_lower for word in ['건강', '다이어트', '영양']):
        return "건강식_컨설팅_에이전트"
    
    # 기본값
    return "냉장고_재료_에이전트"


def refrigerator_agent_node(state: AgentState) -> Dict[str, Any]:
    """냉장고 재료 에이전트 노드"""
    user_query = state["user_query"]
    result = AGENTS["냉장고_재료_에이전트"](user_query)
    
    return {
        "final_response": result,
        "messages": [AIMessage(content=result["response"])]
    }


def restaurant_agent_node(state: AgentState) -> Dict[str, Any]:
    """음식점 추천 에이전트 노드"""
    user_query = state["user_query"]
    result = AGENTS["음식점_추천_에이전트"](user_query)
    
    return {
        "final_response": result,
        "messages": [AIMessage(content=result["response"])]
    }


def recipe_agent_node(state: AgentState) -> Dict[str, Any]:
    """레시피 검색 에이전트 노드"""
    user_query = state["user_query"]
    result = AGENTS["레시피_검색_에이전트"](user_query)
    
    return {
        "final_response": result,
        "messages": [AIMessage(content=result["response"])]
    }


def health_agent_node(state: AgentState) -> Dict[str, Any]:
    """건강식 컨설팅 에이전트 노드"""
    user_query = state["user_query"]
    result = AGENTS["건강식_컨설팅_에이전트"](user_query)
    
    return {
        "final_response": result,
        "messages": [AIMessage(content=result["response"])]
    }


def router(state: AgentState) -> str:
    """라우터 함수 - 다음 실행할 노드 결정"""
    next_agent = state.get("next_agent")
    
    if not next_agent:
        return END
    
    agent_node_mapping = {
        "냉장고_재료_에이전트": "refrigerator_agent",
        "음식점_추천_에이전트": "restaurant_agent", 
        "레시피_검색_에이전트": "recipe_agent",
        "건강식_컨설팅_에이전트": "health_agent"
    }
    
    return agent_node_mapping.get(next_agent, END)


def create_multi_agent_graph():
    """멀티 에이전트 그래프 생성"""
    # StateGraph 생성
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("refrigerator_agent", refrigerator_agent_node)
    workflow.add_node("restaurant_agent", restaurant_agent_node)
    workflow.add_node("recipe_agent", recipe_agent_node)
    workflow.add_node("health_agent", health_agent_node)
    
    # 엣지 설정
    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges("supervisor", router)
    
    # 각 에이전트에서 종료로
    workflow.add_edge("refrigerator_agent", END)
    workflow.add_edge("restaurant_agent", END)
    workflow.add_edge("recipe_agent", END)
    workflow.add_edge("health_agent", END)
    
    return workflow.compile()


def print_welcome():
    """환영 메시지 출력"""
    print("=" * 70)
    print("🍽️  가중치 기반 프롬프트 멀티 에이전트 라우터")
    print("🤖  Powered by Vertex AI Gemini")
    print("=" * 70)
    print()
    print("🔥 시스템 특징:")
    print("• Vertex AI Gemini 2.0 Flash 모델 사용")
    print("• 과거 라우팅 패턴 기반 지능형 에이전트 선택")
    print("• 실시간 가중치 조정으로 A/B 테스트 지원")
    print()
    print("🤖 사용 가능한 에이전트:")
    print("• 냉장고 재료 에이전트: 집에 있는 재료로 요리 추천")
    print("• 음식점 추천 에이전트: 외식 장소 추천")
    print("• 레시피 검색 에이전트: 상세한 요리법 제공")
    print("• 건강식 컨설팅 에이전트: 건강 목적 음식 추천")
    print()
    print("💡 예시 질문:")
    print("- '집에서 만들 수 있는 요리 추천해줘'")
    print("- '맛있는 음식점 추천해줄래?'")
    print("- '김치볶음밥 레시피 알려줘'")
    print("- '다이어트에 좋은 음식 추천해줘'")
    print("- '오늘 저녁 뭐 먹지?'")
    print()
    print("⚙️  환경 설정:")
    print("GCP_PROJECT_ID와 GCP_VERTEXAI_LOCATION을 .env 파일에 설정해주세요.")
    print()
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("-" * 70)


def print_detailed_result(result: Dict[str, Any]):
    """상세 결과 출력"""
    if "routing_info" in result:
        routing_info = result["routing_info"]
        print(f"\n📊 라우팅 분석:")
        print(f"   선택된 에이전트: {routing_info['selected_agent']}")
        print(f"   참고 데이터: {routing_info['total_traces']}개")
        
    if "final_response" in result:
        response = result["final_response"]
        print(f"\n🤖 {response['agent']} 응답:")
        print(f"   {response['response']}")
        print(f"   신뢰도: {response['confidence']:.2f}")
        
        # 추가 정보 출력
        if "cooking_time" in response:
            print(f"   조리시간: {response['cooking_time']}")
        if "restaurant_info" in response:
            info = response["restaurant_info"]
            print(f"   평점: {info['rating']}점, 가격대: {info['price']}")
        if "difficulty" in response:
            print(f"   난이도: {response['difficulty']}")
        if "recommendation_type" in response:
            print(f"   추천 유형: {response['recommendation_type']}")


def main():
    """메인 실행 함수"""
    print_welcome()
    
    # 환경 변수 체크
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("\n❌ 오류: GCP_PROJECT_ID 환경변수가 설정되지 않았습니다.")
        print("🔧 해결 방법:")
        print("1. .env 파일을 생성하고 다음을 추가하세요:")
        print("   GCP_PROJECT_ID=your-gcp-project-id")
        print("   GCP_VERTEXAI_LOCATION=us-central1")
        print("2. 또는 환경변수를 직접 설정하세요:")
        print("   export GCP_PROJECT_ID=your-gcp-project-id")
        return
    
    print(f"✅ Google Cloud 프로젝트: {project_id}")
    print(f"✅ Vertex AI 위치: {os.getenv('GCP_VERTEXAI_LOCATION', 'us-central1')}")
    
    # 멀티 에이전트 그래프 생성
    try:
        app = create_multi_agent_graph()
        print("✅ 멀티 에이전트 시스템 초기화 완료!")
    except Exception as e:
        print(f"\n❌ 시스템 초기화 실패: {e}")
        print("환경 설정을 확인해주세요.")
        return
    
    while True:
        try:
            # 사용자 입력 받기
            user_input = input("\n💬 질문을 입력하세요: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료', 'q']:
                print("\n👋 시스템을 종료합니다. 안녕히 가세요!")
                break
                
            if not user_input:
                print("질문을 입력해주세요.")
                continue
            
            # 초기 상태 설정
            initial_state = {
                "messages": [HumanMessage(content=user_input)],
                "user_query": user_input,
                "next_agent": "",
                "routing_info": {},
                "final_response": {}
            }
            
            # 그래프 실행
            print("\n🔄 처리 중...")
            result = app.invoke(initial_state)
            
            # 결과 출력
            print_detailed_result(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 시스템을 종료합니다. 안녕히 가세요!")
            break
        except Exception as e:
            print(f"\n❌ 오류가 발생했습니다: {e}")
            print("다시 시도해주세요.")


if __name__ == "__main__":
    main() 