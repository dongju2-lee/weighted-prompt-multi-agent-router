"""
가중치 기반 라우터 모듈
"""
import random
from typing import Dict, Tuple

# 기본 에이전트 가중치
DEFAULT_AGENT_WEIGHTS = {
    "냉장고_재료_에이전트": 1.0,
    "음식점_추천_에이전트": 1.0,
    "레시피_검색_에이전트": 1.0,
    "건강식_컨설팅_에이전트": 1.0
}

# Mock 과거 라우팅 패턴 데이터
MOCK_ROUTING_PATTERNS = {
    "음식 추천": {
        "냉장고_재료_에이전트": 30,
        "음식점_추천_에이전트": 25,
        "레시피_검색_에이전트": 25,
        "건강식_컨설팅_에이전트": 20
    },
    "요리": {
        "냉장고_재료_에이전트": 40,
        "음식점_추천_에이전트": 10,
        "레시피_검색_에이전트": 40,
        "건강식_컨설팅_에이전트": 10
    },
    "맛집": {
        "냉장고_재료_에이전트": 5,
        "음식점_추천_에이전트": 70,
        "레시피_검색_에이전트": 10,
        "건강식_컨설팅_에이전트": 15
    },
    "다이어트": {
        "냉장고_재료_에이전트": 15,
        "음식점_추천_에이전트": 10,
        "레시피_검색_에이전트": 15,
        "건강식_컨설팅_에이전트": 60
    },
    "default": {
        "냉장고_재료_에이전트": 25,
        "음식점_추천_에이전트": 25,
        "레시피_검색_에이전트": 25,
        "건강식_컨설팅_에이전트": 25
    }
}

def get_routing_pattern(user_query: str) -> Tuple[Dict[str, int], int]:
    """
    사용자 질문을 기반으로 과거 라우팅 패턴 반환
    """
    query_lower = user_query.lower()
    
    # 키워드 기반 패턴 매칭
    if any(keyword in query_lower for keyword in ["맛집", "음식점", "외식", "데이트"]):
        pattern_key = "맛집"
    elif any(keyword in query_lower for keyword in ["요리", "만들기", "레시피", "조리"]):
        pattern_key = "요리"
    elif any(keyword in query_lower for keyword in ["다이어트", "건강", "칼로리", "살"]):
        pattern_key = "다이어트"
    elif any(keyword in query_lower for keyword in ["음식", "추천", "뭐"]):
        pattern_key = "음식 추천"
    else:
        pattern_key = "default"
    
    pattern = MOCK_ROUTING_PATTERNS[pattern_key]
    total_traces = random.randint(80, 150)  # 과거 총 추적 수
    
    return pattern, total_traces

def apply_weights_and_normalize(base_pattern: Dict[str, int], agent_weights: Dict[str, float]) -> Dict[str, float]:
    """
    가중치를 적용하고 정규화된 확률 분포 반환 (0-1 범위)
    """
    weighted_scores = {}
    for agent, count in base_pattern.items():
        weight = agent_weights.get(agent, 1.0)
        weighted_scores[agent] = count * weight
    
    # 정규화 (0-1 범위)
    total = sum(weighted_scores.values())
    if total == 0:
        # 균등 분포로 fallback
        num_agents = len(weighted_scores)
        return {agent: 1.0/num_agents for agent in weighted_scores}
    
    return {agent: score/total for agent, score in weighted_scores.items()} 