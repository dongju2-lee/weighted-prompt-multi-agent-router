"""
유틸리티 함수 모듈 (음식 추천 에이전트 버전)
"""
import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel
from langfuse import Langfuse

# 환경 변수 로드
load_dotenv()

# 전역 모델 캐시 (성능 최적화)
_cached_gemini_model: Optional[GenerativeModel] = None
_cached_langfuse_client: Optional[Langfuse] = None


def initialize_langfuse() -> tuple[Optional[Langfuse], Optional[Any]]:
    """
    Langfuse 초기화 (선택적)
    """
    try:
        from langfuse import Langfuse
        
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST")
        
        if public_key and secret_key:
            return Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host
            ), None
        else:
            print("⚠️ Langfuse 환경변수가 설정되지 않았습니다. 추적 기능을 사용할 수 없습니다.")
            return None, None
    except ImportError:
        print("⚠️ Langfuse 라이브러리가 설치되지 않았습니다.")
        return None, None


def initialize_gemini_model() -> GenerativeModel:
    """
    Vertex AI Gemini 모델 초기화
    """
    global _cached_gemini_model
    
    if _cached_gemini_model is not None:
        return _cached_gemini_model
    
    project_id = os.getenv("GCP_PROJECT_ID")
    location = os.getenv("GCP_VERTEXAI_LOCATION", "us-central1")
    model_name = os.getenv("SUPERVISOR_MODEL", "gemini-2.0-flash")
    
    if not project_id:
        raise ValueError("GCP_PROJECT_ID 환경변수가 설정되지 않았습니다.")
    
    # Vertex AI 초기화
    vertexai.init(project=project_id, location=location)
    
    # 모델 초기화
    _cached_gemini_model = GenerativeModel(model_name)
    
    return _cached_gemini_model


def extract_agent_name(gemini_response: str) -> str:
    """
    Gemini 응답에서 에이전트 이름 추출 (음식 추천 에이전트)
    """
    # 음식 에이전트 목록
    food_agents = [
        "냉장고_재료_에이전트",
        "음식점_추천_에이전트", 
        "레시피_검색_에이전트",
        "건강식_컨설팅_에이전트"
    ]
    
    response_lower = gemini_response.lower()
    
    # 1. 정확한 에이전트명 매칭
    for agent in food_agents:
        if agent in gemini_response:
            return agent
    
    # 2. 키워드 기반 매칭
    if any(keyword in response_lower for keyword in ["냉장고", "재료", "집", "간단"]):
        return "냉장고_재료_에이전트"
    elif any(keyword in response_lower for keyword in ["음식점", "맛집", "외식", "데이트"]):
        return "음식점_추천_에이전트"
    elif any(keyword in response_lower for keyword in ["레시피", "요리법", "만들기", "조리"]):
        return "레시피_검색_에이전트"
    elif any(keyword in response_lower for keyword in ["건강", "다이어트", "칼로리", "영양"]):
        return "건강식_컨설팅_에이전트"
    
    # 3. 기본값
    return "냉장고_재료_에이전트"


def validate_environment() -> bool:
    """환경 변수 검증"""
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("\n❌ 오류: GCP_PROJECT_ID 환경변수가 설정되지 않았습니다.")
        print("🔧 해결 방법:")
        print("1. .env 파일을 생성하고 다음을 추가하세요:")
        print("   GCP_PROJECT_ID=your-gcp-project-id")
        print("   GCP_VERTEXAI_LOCATION=us-central1")
        print("2. 또는 환경변수를 직접 설정하세요:")
        print("   export GCP_PROJECT_ID=your-gcp-project-id")
        return False
    
    print(f"✅ Google Cloud 프로젝트: {project_id}")
    print(f"✅ Vertex AI 위치: {os.getenv('GCP_VERTEXAI_LOCATION', 'us-central1')}")
    return True


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


def get_agent_node_mapping() -> Dict[str, str]:
    """에이전트 이름과 노드 이름 매핑"""
    return {
        "냉장고_재료_에이전트": "refrigerator_agent",
        "음식점_추천_에이전트": "restaurant_agent", 
        "레시피_검색_에이전트": "recipe_agent",
        "건강식_컨설팅_에이전트": "health_agent"
    }


def is_exit_command(user_input: str) -> bool:
    """종료 명령어 체크"""
    return user_input.lower() in ['quit', 'exit', '종료', 'q'] 