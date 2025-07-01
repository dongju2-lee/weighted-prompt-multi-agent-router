"""
가중치 기반 프롬프트 멀티 에이전트 라우터
"""
import random
from typing import Dict, Any, List, Tuple


def get_mock_routing_data(user_query: str) -> Tuple[Dict[str, float], int]:
    """
    과거 라우팅 데이터를 시뮬레이션하는 함수
    실제로는 벡터 데이터베이스에서 유사한 질문들을 검색하여 비율을 계산
    """
    # 질문 유형별로 다른 패턴을 시뮬레이션
    query_lower = user_query.lower()
    
    if any(word in query_lower for word in ['집에서', '냉장고', '재료', '만들', '요리']):
        # 집에서 요리 관련 질문
        base_ratios = {
            "냉장고_재료_에이전트": 0.45,
            "레시피_검색_에이전트": 0.30,
            "건강식_컨설팅_에이전트": 0.15,
            "음식점_추천_에이전트": 0.10
        }
        total_traces = 85
    elif any(word in query_lower for word in ['음식점', '식당', '외식', '맛집']):
        # 외식 관련 질문
        base_ratios = {
            "음식점_추천_에이전트": 0.60,
            "냉장고_재료_에이전트": 0.15,
            "레시피_검색_에이전트": 0.15,
            "건강식_컨설팅_에이전트": 0.10
        }
        total_traces = 92
    elif any(word in query_lower for word in ['다이어트', '건강', '칼로리', '영양']):
        # 건강식 관련 질문
        base_ratios = {
            "건강식_컨설팅_에이전트": 0.50,
            "냉장고_재료_에이전트": 0.25,
            "레시피_검색_에이전트": 0.20,
            "음식점_추천_에이전트": 0.05
        }
        total_traces = 67
    elif any(word in query_lower for word in ['레시피', '만드는법', '요리법']):
        # 레시피 관련 질문
        base_ratios = {
            "레시피_검색_에이전트": 0.55,
            "냉장고_재료_에이전트": 0.25,
            "건강식_컨설팅_에이전트": 0.12,
            "음식점_추천_에이전트": 0.08
        }
        total_traces = 78
    else:
        # 일반적인 음식 추천 질문
        base_ratios = {
            "냉장고_재료_에이전트": 0.30,
            "음식점_추천_에이전트": 0.25,
            "레시피_검색_에이전트": 0.25,
            "건강식_컨설팅_에이전트": 0.20
        }
        total_traces = 120
    
    return base_ratios, total_traces


def apply_weights_and_normalize(base_ratios: Dict[str, float], agent_weights: Dict[str, float]) -> Dict[str, float]:
    """
    사용자 정의 가중치를 적용하고 100%로 정규화
    """
    weighted_ratios = {}
    for agent, ratio in base_ratios.items():
        weight = agent_weights.get(agent, 1.0)
        weighted_ratios[agent] = ratio * weight
    
    # 100%로 재정규화
    total_weighted = sum(weighted_ratios.values())
    
    if total_weighted > 0:
        normalized_ratios = {
            agent: (ratio / total_weighted) * 100
            for agent, ratio in weighted_ratios.items()
        }
    else:
        normalized_ratios = {}
    
    return normalized_ratios


def generate_supervisor_prompt(user_query: str, normalized_ratios: Dict[str, float], total_traces: int) -> str:
    """
    가중치 기반 라우팅 정보가 포함된 슈퍼바이저 프롬프트 생성
    """
    historical_context = f"""
과거 데이터 분석 결과:
- 총 {total_traces}개의 유사한 질문 데이터를 참고했습니다.
- 과거 라우팅 패턴:
"""
    
    for agent, percentage in normalized_ratios.items():
        historical_context += f"  • {agent}: {percentage:.1f}%\n"
    
    supervisor_prompt = f"""
사용자 질문: "{user_query}"

{historical_context}

위의 히스토리컬 데이터를 참고하여 가장 적절한 에이전트를 선택하세요.
과거 패턴을 고려하되, 현재 질문의 구체적인 맥락도 함께 분석하여 최종 결정을 내려주세요.

사용 가능한 에이전트:
- 냉장고_재료_에이전트: 집에 있는 재료로 요리 추천
- 음식점_추천_에이전트: 외식 장소 추천  
- 레시피_검색_에이전트: 상세한 요리법 제공
- 건강식_컨설팅_에이전트: 건강 목적 음식 추천

에이전트 이름만 정확히 반환해주세요 (예: "냉장고_재료_에이전트").
"""
    
    return supervisor_prompt


def simple_supervisor_routing(user_query: str, agent_weights: Dict[str, float] = None) -> str:
    """
    간단한 슈퍼바이저 라우팅 함수 (LLM 없이 가중치 기반으로 결정)
    """
    if agent_weights is None:
        agent_weights = {}
    
    # 과거 패턴 분석
    base_ratios, total_traces = get_mock_routing_data(user_query)
    
    # 가중치 적용 및 정규화
    normalized_ratios = apply_weights_and_normalize(base_ratios, agent_weights)
    
    # 가중치 기반 랜덤 선택 (실제로는 LLM이 이 정보를 참고하여 결정)
    agents = list(normalized_ratios.keys())
    weights = list(normalized_ratios.values())
    
    if not agents:
        return "냉장고_재료_에이전트"  # 기본 에이전트
    
    selected_agent = random.choices(agents, weights=weights, k=1)[0]
    
    # 디버깅 정보 출력
    print(f"\n=== 라우팅 분석 결과 ===")
    print(f"질문: {user_query}")
    print(f"참고한 과거 데이터: {total_traces}개")
    print("과거 라우팅 패턴:")
    for agent, percentage in normalized_ratios.items():
        mark = "★" if agent == selected_agent else " "
        print(f"  {mark} {agent}: {percentage:.1f}%")
    print(f"선택된 에이전트: {selected_agent}")
    print("=" * 30)
    
    return selected_agent 