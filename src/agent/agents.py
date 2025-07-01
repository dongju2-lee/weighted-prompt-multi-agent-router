"""
음식 추천 에이전트 함수 모듈
"""

def refrigerator_recipe_agent(user_query: str) -> dict:
    """
    냉장고 재료 기반 레시피 에이전트: 집에 있는 재료로 요리 추천
    """
    return {
        "agent": "냉장고_재료_에이전트",
        "answer": f"집에 있는 재료로 만들 수 있는 요리를 추천해드릴게요! 김치볶음밥이나 계란후라이는 어떠세요?",
        "detail": "냉장고에 있는 기본 재료들로 간단하고 맛있는 요리를 만들 수 있습니다."
    }

def restaurant_recommendation_agent(user_query: str) -> dict:
    """
    음식점 추천 에이전트: 외식 장소 추천
    """
    return {
        "agent": "음식점_추천_에이전트",
        "answer": f"맛있는 음식점을 추천해드릴게요! 근처 한식당이나 이탈리안 레스토랑은 어떠세요?",
        "detail": "지역별 맛집 정보와 리뷰를 바탕으로 최적의 외식 장소를 추천해드립니다."
    }

def recipe_search_agent(user_query: str) -> dict:
    """
    레시피 검색 에이전트: 상세한 요리법 제공
    """
    return {
        "agent": "레시피_검색_에이전트",
        "answer": f"자세한 레시피를 알려드릴게요! 단계별로 따라하시면 맛있는 요리를 만들 수 있어요.",
        "detail": "재료 준비부터 조리 과정까지 상세한 레시피를 제공합니다."
    }

def health_food_consulting_agent(user_query: str) -> dict:
    """
    건강식 컨설팅 에이전트: 건강과 다이어트를 고려한 음식 추천
    """
    return {
        "agent": "건강식_컨설팅_에이전트",
        "answer": f"건강한 식단을 추천해드릴게요! 저칼로리 샐러드나 단백질이 풍부한 닭가슴살 요리는 어떠세요?",
        "detail": "영양 균형과 칼로리를 고려한 건강한 식단을 제안합니다."
    } 