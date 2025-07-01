"""
음식 관련 4개 에이전트 구현
"""
import random
from typing import Dict, Any, List


def refrigerator_recipe_agent(query: str) -> Dict[str, Any]:
    """냉장고 재료 기반 요리 추천 에이전트"""
    recipes = [
        "계란과 양파로 오믈렛 만들기: 계란 2개를 풀고 양파를 볶아서 함께 요리하세요.",
        "감자와 베이컨 볶음: 감자를 얇게 썰어 베이컨과 함께 볶으면 맛있어요.",
        "토마토 스크램블 에그: 토마토와 계란을 함께 볶아 간단한 요리를 만드세요.",
        "양배추 볶음밥: 남은 밥과 양배추로 간단한 볶음밥을 만들어보세요.",
        "치즈 토스트: 식빵에 치즈를 올려 구워서 간단한 간식을 만드세요."
    ]
    
    selected_recipe = random.choice(recipes)
    
    return {
        "agent": "냉장고_재료_에이전트",
        "response": f"냉장고에 있는 재료로 다음 요리를 추천드립니다: {selected_recipe}",
        "confidence": 0.85,
        "ingredients_needed": ["기본 재료들", "조미료"],
        "cooking_time": f"{random.randint(10, 30)}분"
    }


def restaurant_recommendation_agent(query: str) -> Dict[str, Any]:
    """음식점 추천 에이전트"""
    restaurants = [
        {"name": "맛있는 한식당", "cuisine": "한식", "price": "중간", "rating": 4.5},
        {"name": "이탈리아 파스타", "cuisine": "이탈리안", "price": "높음", "rating": 4.7},
        {"name": "동네 치킨집", "cuisine": "치킨", "price": "낮음", "rating": 4.2},
        {"name": "스시 마스터", "cuisine": "일식", "price": "높음", "rating": 4.8},
        {"name": "중국집 맛가", "cuisine": "중식", "price": "중간", "rating": 4.3}
    ]
    
    selected = random.choice(restaurants)
    
    return {
        "agent": "음식점_추천_에이전트",
        "response": f"{selected['name']}을 추천드립니다. {selected['cuisine']} 음식점으로 가격대는 {selected['price']}이고 평점은 {selected['rating']}점입니다.",
        "confidence": 0.78,
        "restaurant_info": selected,
        "location": "근처"
    }


def recipe_search_agent(query: str) -> Dict[str, Any]:
    """레시피 검색 에이전트"""
    recipes_detail = [
        {
            "name": "김치볶음밥",
            "ingredients": ["밥 1공기", "김치 100g", "돼지고기 50g", "계란 1개", "파 적당량"],
            "steps": ["1. 김치와 돼지고기를 볶는다", "2. 밥을 넣고 볶는다", "3. 계란을 올려 완성한다"],
            "time": "15분"
        },
        {
            "name": "스파게티 카르보나라",
            "ingredients": ["스파게티 200g", "베이컨 100g", "계란 2개", "파마산 치즈", "마늘"],
            "steps": ["1. 스파게티를 삶는다", "2. 베이컨을 볶는다", "3. 계란과 치즈를 섞어 소스를 만든다", "4. 모든 재료를 섞는다"],
            "time": "20분"
        },
        {
            "name": "된장찌개",
            "ingredients": ["된장 2큰술", "두부 150g", "양파 1/2개", "애호박 1/3개", "대파 1대"],
            "steps": ["1. 물에 된장을 푼다", "2. 야채를 넣고 끓인다", "3. 두부를 넣고 마저 끓인다"],
            "time": "25분"
        }
    ]
    
    selected = random.choice(recipes_detail)
    
    return {
        "agent": "레시피_검색_에이전트",
        "response": f"{selected['name']} 레시피를 찾아드렸습니다. 조리시간: {selected['time']}",
        "confidence": 0.92,
        "recipe": selected,
        "difficulty": "중간"
    }


def health_food_consulting_agent(query: str) -> Dict[str, Any]:
    """건강식 컨설팅 에이전트"""
    health_foods = [
        {
            "food": "퀴노아 샐러드",
            "benefits": "고단백, 글루텐프리, 풍부한 식이섬유",
            "calories": "약 200kcal",
            "nutrients": ["단백질", "식이섬유", "마그네슘"]
        },
        {
            "food": "연어 스테이크",
            "benefits": "오메가3 풍부, 고단백 저칼로리",
            "calories": "약 250kcal",
            "nutrients": ["오메가3", "단백질", "비타민D"]
        },
        {
            "food": "아보카도 토스트",
            "benefits": "건강한 지방, 식이섬유 풍부",
            "calories": "약 300kcal",
            "nutrients": ["불포화지방산", "식이섬유", "비타민K"]
        },
        {
            "food": "그릭 요거트 베리볼",
            "benefits": "프로바이오틱스, 저당, 고단백",
            "calories": "약 150kcal",
            "nutrients": ["단백질", "프로바이오틱스", "항산화제"]
        }
    ]
    
    selected = random.choice(health_foods)
    
    return {
        "agent": "건강식_컨설팅_에이전트", 
        "response": f"건강을 위해 {selected['food']}을 추천드립니다. {selected['benefits']} 효과가 있고 칼로리는 {selected['calories']}입니다.",
        "confidence": 0.88,
        "health_info": selected,
        "recommendation_type": "건강식"
    }


# 에이전트 매핑
AGENTS = {
    "냉장고_재료_에이전트": refrigerator_recipe_agent,
    "음식점_추천_에이전트": restaurant_recommendation_agent,
    "레시피_검색_에이전트": recipe_search_agent,
    "건강식_컨설팅_에이전트": health_food_consulting_agent
} 