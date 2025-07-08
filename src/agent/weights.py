"""
가중치 및 라우팅 패턴 관리 모듈 (운동 추천 에이전트 버전)
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict


# 선택 이력 파일 경로
ROUTING_HISTORY_FILE = "routing_history.json"


def load_routing_history() -> List[Dict]:
    """선택 이력 로드"""
    if not os.path.exists(ROUTING_HISTORY_FILE):
        return []
    
    try:
        with open(ROUTING_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("⚠️ 선택 이력 파일을 읽을 수 없어 새로 시작합니다.")
        return []


def save_routing_choice(user_query: str, selected_agent: str, confidence: float, reason: str):
    """선택 결과를 이력에 저장"""
    history = load_routing_history()
    
    new_record = {
        "timestamp": datetime.now().isoformat(),
        "user_query": user_query,
        "selected_agent": selected_agent,
        "confidence": confidence,
        "reason": reason
    }
    
    history.append(new_record)
    
    # 최근 1000개만 유지 (메모리 관리)
    if len(history) > 1000:
        history = history[-1000:]
    
    try:
        with open(ROUTING_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"✅ 선택 이력 저장 완료: {selected_agent} (총 {len(history)}개)")
    except Exception as e:
        print(f"❌ 선택 이력 저장 실패: {e}")


def get_real_routing_patterns() -> Tuple[Dict[str, float], int]:
    """실제 선택 이력에서 패턴 계산"""
    history = load_routing_history()
    
    if not history:
        print("📊 선택 이력이 없어 기본 패턴을 사용합니다.")
        return get_mock_routing_data("기본")
    
    # 에이전트별 선택 횟수 계산
    agent_counts = defaultdict(int)
    total_count = len(history)
    
    for record in history:
        agent_counts[record["selected_agent"]] += 1
    
    # 비율 계산
    agent_ratios = {}
    sports_agents = ["축구_에이전트", "농구_에이전트", "야구_에이전트", "테니스_에이전트"]
    
    for agent in sports_agents:
        agent_ratios[agent] = agent_counts[agent] / total_count if total_count > 0 else 0.0
    
    print(f"📊 실제 패턴 (총 {total_count}회):")
    for agent, ratio in agent_ratios.items():
        count = agent_counts[agent]
        print(f"   {agent}: {ratio:.1%} ({count}회)")
    
    return agent_ratios, total_count


def get_routing_data_with_history(user_query: str) -> Tuple[Dict[str, float], int]:
    """
    선택 이력이 있으면 실제 패턴, 없으면 mock 데이터 반환
    """
    history = load_routing_history()
    
    if len(history) >= 5:  # 최소 5개 이력이 있으면 실제 패턴 사용
        return get_real_routing_patterns()
    else:
        print(f"📊 이력이 부족해 mock 데이터 사용 (현재: {len(history)}개, 필요: 5개)")
        return get_mock_routing_data(user_query)


def get_mock_routing_data(user_query: str) -> Tuple[Dict[str, float], int]:
    """
    Mock 과거 라우팅 패턴 데이터 생성 (운동 추천 에이전트 버전)
    """
    import random
    
    # 기본 패턴들
    patterns = {
        "균등": {"축구_에이전트": 0.25, "농구_에이전트": 0.25, "야구_에이전트": 0.25, "테니스_에이전트": 0.25},
        "축구선호": {"축구_에이전트": 0.4, "농구_에이전트": 0.2, "야구_에이전트": 0.2, "테니스_에이전트": 0.2},
        "구기선호": {"축구_에이전트": 0.35, "농구_에이전트": 0.35, "야구_에이전트": 0.15, "테니스_에이전트": 0.15},
        "라켓선호": {"축구_에이전트": 0.2, "농구_에이전트": 0.2, "야구_에이전트": 0.25, "테니스_에이전트": 0.35}
    }
    
    # 질문 키워드에 따른 패턴 선택
    query_lower = user_query.lower()
    if any(word in query_lower for word in ["축구", "킥", "풋살"]):
        base_ratios = patterns["축구선호"]
    elif any(word in query_lower for word in ["농구", "슛", "3점"]):
        base_ratios = patterns["구기선호"]
    elif any(word in query_lower for word in ["야구", "배팅", "홈런"]):
        base_ratios = patterns["구기선호"]
    elif any(word in query_lower for word in ["테니스", "라켓", "서브"]):
        base_ratios = patterns["라켓선호"]
    else:
        base_ratios = patterns["균등"]
    
    # 가상 총 추적 횟수
    total_traces = random.randint(80, 200)
    
    return base_ratios, total_traces


def get_default_agent_weights() -> Dict[str, float]:
    """환경변수에서 에이전트 가중치 로드"""
    sports_agents = ["축구_에이전트", "농구_에이전트", "야구_에이전트", "테니스_에이전트"]
    weights = {}
    
    for agent in sports_agents:
        # 환경변수에서 가중치 읽기 (기본값: 1.0)
        env_key = f"WEIGHT_{agent}"
        try:
            weight_value = float(os.getenv(env_key, "1.0"))
            weights[agent] = weight_value
        except (ValueError, TypeError):
            print(f"⚠️ {env_key} 환경변수가 잘못된 형태입니다. 기본값 1.0을 사용합니다.")
            weights[agent] = 1.0
    
    print(f"📊 현재 에이전트 가중치:")
    for agent, weight in weights.items():
        print(f"   {agent}: {weight}")
    
    return weights


def apply_weights_and_normalize(base_ratios: Dict[str, float], weights: Dict[str, float]) -> Dict[str, float]:
    """가중치 적용 및 정규화"""
    weighted_ratios = {}
    for agent, base_ratio in base_ratios.items():
        weight = weights.get(agent, 1.0)
        weighted_ratios[agent] = base_ratio * weight
    
    # 정규화
    total = sum(weighted_ratios.values())
    if total > 0:
        for agent in weighted_ratios:
            weighted_ratios[agent] /= total
    
    return weighted_ratios


def get_routing_statistics() -> Dict:
    """라우팅 통계 반환"""
    history = load_routing_history()
    
    if not history:
        return {"total_requests": 0, "agents": {}}
    
    agent_stats = defaultdict(lambda: {"count": 0, "avg_confidence": 0.0})
    total_count = len(history)
    
    for record in history:
        agent = record["selected_agent"]
        agent_stats[agent]["count"] += 1
        agent_stats[agent]["avg_confidence"] += record.get("confidence", 0.0)
    
    # 평균 확신도 계산
    for agent in agent_stats:
        if agent_stats[agent]["count"] > 0:
            agent_stats[agent]["avg_confidence"] /= agent_stats[agent]["count"]
        agent_stats[agent]["percentage"] = agent_stats[agent]["count"] / total_count * 100
    
    return {
        "total_requests": total_count,
        "agents": dict(agent_stats)
    }

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