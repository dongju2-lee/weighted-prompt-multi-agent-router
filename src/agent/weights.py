"""
가중치 기반 라우팅 모듈 (운동 추천 버전)
"""
import random
from typing import Dict

def get_mock_routing_data(user_query: str) -> tuple[Dict[str, float], int]:
    """
    과거 패턴을 모방한 Mock 데이터 생성 (운동 추천 에이전트 버전)
    """
    # 운동 관련 키워드 기반 패턴 시뮬레이션
    sports_keywords = {
        "축구": ["축구", "풋살", "킥", "골", "패스", "드리블"],
        "농구": ["농구", "농구장", "슛", "드리블", "3점", "자유투"],
        "야구": ["야구", "배팅", "타격", "캐치볼", "홈런", "투구"],
        "테니스": ["테니스", "라켓", "서브", "발리", "코트", "레슨"]
    }
    
    # 기본 분포 
    base_ratios = {
        "축구_에이전트": 0.25 ,
        "농구_에이전트": 0.25 ,
        "야구_에이전트": 0.25 ,
        "테니스_에이전트": 0.25 
    }
    
    # 정규화
    total = sum(base_ratios.values())
    base_ratios = {k: v/total for k, v in base_ratios.items()}
    
    # 과거 패턴 시뮬레이션 (총 추적 수)
    total_traces = random.randint(50, 200)
    
    return base_ratios, total_traces

def get_default_agent_weights() -> Dict[str, float]:
    """
    기본 에이전트 가중치 반환 (운동 추천 에이전트)
    """
    return {
        "축구_에이전트": 1.0,
        "농구_에이전트": 0.0,
        "야구_에이전트": 1.0,
        "테니스_에이전트": 0.0
    }

def apply_weights_and_normalize(base_ratios: Dict[str, float], weights: Dict[str, float]) -> Dict[str, float]:
    """
    가중치를 적용하고 정규화
    """
    weighted_ratios = {}
    for agent, ratio in base_ratios.items():
        weight = weights.get(agent, 1.0)
        weighted_ratios[agent] = ratio * weight
    
    # 정규화
    total = sum(weighted_ratios.values())
    if total > 0:
        weighted_ratios = {k: v/total for k, v in weighted_ratios.items()}
    
    return weighted_ratios

def get_ab_test_weights(test_variant: str = "default") -> Dict[str, float]:
    """A/B 테스트용 가중치 설정"""
    if test_variant == "soccer_focus":
        # 축구 에이전트 강화
        return {
            "축구_에이전트": 1.5,
            "농구_에이전트": 0.8,
            "야구_에이전트": 0.8,
            "테니스_에이전트": 0.9
        }
    elif test_variant == "basketball_focus":
        # 농구 에이전트 강화
        return {
            "축구_에이전트": 0.8,
            "농구_에이전트": 1.4,
            "야구_에이전트": 0.9,
            "테니스_에이전트": 0.9
        }
    elif test_variant == "baseball_focus":
        # 야구 에이전트 강화
        return {
            "축구_에이전트": 0.8,
            "농구_에이전트": 0.9,
            "야구_에이전트": 1.4,
            "테니스_에이전트": 0.9
        }
    else:
        # 기본 설정
        return get_default_agent_weights()

def simple_supervisor_routing(user_query: str, agent_weights: Dict[str, float] = None) -> str:
    """
    간단한 슈퍼바이저 라우팅 함수 (LLM 없이 가중치 기반으로 결정)
    """
    if agent_weights is None:
        agent_weights = get_default_agent_weights()
    
    # 과거 패턴 분석
    base_ratios, total_traces = get_mock_routing_data(user_query)
    
    # 가중치 적용 및 정규화
    normalized_ratios = apply_weights_and_normalize(base_ratios, agent_weights)
    
    # 매번 다른 랜덤 시드 사용
    random.seed(int(time.time() * 1000000) % 1000000)
    
    # 가중치 기반 랜덤 선택
    agents = list(normalized_ratios.keys())
    weights = list(normalized_ratios.values())
    
    if not agents:
        return "축구_에이전트"  # 기본 에이전트
    
    # 확률적 선택
    selected_agent = random.choices(agents, weights=weights, k=1)[0]
    
    return selected_agent

def print_routing_analysis(user_query: str, selected_agent: str, normalized_ratios: Dict[str, float], total_traces: int):
    """라우팅 분석 결과 출력"""
    print(f"\n=== Gemini 슈퍼바이저 분석 결과 ===")
    print(f"질문: {user_query}")
    print(f"참고한 과거 데이터: {total_traces}개")
    print("과거 라우팅 패턴:")
    for agent, percentage in normalized_ratios.items():
        mark = "★" if agent == selected_agent else " "
        print(f"  {mark} {agent}: {percentage:.1f}%")
    print(f"Gemini 선택 결과: {selected_agent}")
    print("=" * 40) 