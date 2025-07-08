"""
운동 추천 에이전트 함수 모듈
"""

def soccer_agent(user_query: str) -> dict:
    """
    축구 에이전트: 축구 관련 추천 및 정보 제공
    """
    return {
        "agent": "축구_에이전트",
        "answer": f"축구를 추천해드릴게요! 근처 축구장에서 풋살이나 축구 경기는 어떠세요?",
        "detail": "축구장 정보, 팀 매칭, 축구 용품 추천 등 축구 관련 모든 정보를 제공합니다."
    }

def basketball_agent(user_query: str) -> dict:
    """
    농구 에이전트: 농구 관련 추천 및 정보 제공
    """
    return {
        "agent": "농구_에이전트",
        "answer": f"농구를 추천해드릴게요! 농구장에서 3대3이나 자유투 연습은 어떠세요?",
        "detail": "농구장 정보, 팀 구성, 농구 기술 연습법 등 농구 관련 정보를 제공합니다."
    }

def baseball_agent(user_query: str) -> dict:
    """
    야구 에이전트: 야구 관련 추천 및 정보 제공
    """
    return {
        "agent": "야구_에이전트",
        "answer": f"야구를 추천해드릴게요! 타격장에서 배팅 연습이나 캐치볼은 어떠세요?",
        "detail": "야구장 정보, 팀 가입, 야구 기술 향상법 등 야구 관련 정보를 제공합니다."
    }

def tennis_agent(user_query: str) -> dict:
    """
    테니스 에이전트: 테니스 관련 추천 및 정보 제공
    """
    return {
        "agent": "테니스_에이전트",
        "answer": f"테니스를 추천해드릴게요! 테니스장에서 레슨이나 경기는 어떠세요?",
        "detail": "테니스장 예약, 레슨 정보, 파트너 매칭 등 테니스 관련 정보를 제공합니다."
} 