"""
유틸리티 함수 모듈 (운동 추천 에이전트 버전)
"""
import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel
from langfuse import Langfuse
from google.cloud import aiplatform

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


def initialize_vertexai():
    """Vertex AI 초기화"""
    try:
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_VERTEXAI_LOCATION", "us-central1")
        
        if not project_id:
            raise ValueError("GCP_PROJECT_ID 환경변수가 설정되지 않았습니다.")
        
        # Vertex AI 초기화
        vertexai.init(project=project_id, location=location)
        print(f"✅ Vertex AI 초기화 완료 (Project: {project_id}, Location: {location})")
        
        return project_id, location
    except Exception as e:
        print(f"❌ Vertex AI 초기화 실패: {e}")
        raise


def initialize_gemini_model():
    """Gemini 모델 초기화"""
    try:
        # Vertex AI 초기화
        initialize_vertexai()
        
        # Gemini 2.0 Flash 모델 초기화
        model = GenerativeModel("gemini-2.0-flash-exp")
        print("✅ Gemini 2.0 Flash 모델 초기화 완료")
        
        return model
    except Exception as e:
        print(f"❌ Gemini 모델 초기화 실패: {e}")
        raise


def extract_agent_name(llm_response: str) -> str:
    """
    LLM 응답에서 에이전트 이름 추출 (운동 추천 에이전트)
    """
    # 운동 에이전트 이름들
    sports_agents = [
        "축구_에이전트",
        "농구_에이전트", 
        "야구_에이전트",
        "테니스_에이전트"
    ]
    
    print(f"🔍 extract_agent_name 디버그:")
    print(f"   입력 텍스트: {llm_response[:200]}...")
    
    # 1. 먼저 정규표현식으로 "선택된 에이전트:" 패턴 찾기 (가장 정확한 방법)
    agent_pattern = r"선택된\s*에이전트\s*:\s*([가-힣_]+)"
    match = re.search(agent_pattern, llm_response)
    if match:
        extracted_agent = match.group(1).strip()
        print(f"   정규표현식 매칭 결과: {extracted_agent}")
        # 추출된 에이전트가 유효한지 확인
        for agent in sports_agents:
            if agent == extracted_agent:
                print(f"   ✅ 정규표현식으로 선택: {agent}")
                return agent
        print(f"   ❌ 정규표현식 결과가 유효하지 않음: {extracted_agent}")
    else:
        print(f"   ❌ 정규표현식 매칭 실패")
    
    # 2. 정규표현식이 실패했을 때만 에이전트 이름 포함 여부 확인
    response_lower = llm_response.lower()
    found_agents = []
    for agent in sports_agents:
        if agent.lower() in response_lower:
            found_agents.append(agent)
    
    if found_agents:
        print(f"   키워드 매칭으로 발견된 에이전트들: {found_agents}")
        # 여러 에이전트가 발견된 경우 첫 번째 선택 (기존 로직 유지)
        print(f"   ✅ 키워드 매칭으로 선택: {found_agents[0]}")
        return found_agents[0]
    
    # 3. 백업: 키워드 기반 매칭
    if any(keyword in response_lower for keyword in ["축구", "풋살", "킥", "골"]):
        print(f"   ✅ 백업 키워드 매칭으로 선택: 축구_에이전트")
        return "축구_에이전트"
    elif any(keyword in response_lower for keyword in ["농구", "농구장", "슛", "3점"]):
        print(f"   ✅ 백업 키워드 매칭으로 선택: 농구_에이전트")
        return "농구_에이전트"
    elif any(keyword in response_lower for keyword in ["야구", "배팅", "타격", "홈런"]):
        print(f"   ✅ 백업 키워드 매칭으로 선택: 야구_에이전트")
        return "야구_에이전트"
    elif any(keyword in response_lower for keyword in ["테니스", "라켓", "서브", "코트"]):
        print(f"   ✅ 백업 키워드 매칭으로 선택: 테니스_에이전트")
        return "테니스_에이전트"
    
    # 4. 기본값
    print(f"   ✅ 기본값으로 선택: 축구_에이전트")
    return "축구_에이전트"


def format_percentage(value: float) -> str:
    """소수를 백분율로 포맷팅"""
    return f"{value * 100:.1f}%"


def validate_environment():
    """환경 변수 검증"""
    required_vars = ["GCP_PROJECT_ID"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("📝 .env 파일에 다음 변수들을 설정해주세요:")
        for var in missing_vars:
            if var == "GCP_PROJECT_ID":
                print(f"   {var}=your-gcp-project-id")
            elif var == "GCP_VERTEXAI_LOCATION":
                print(f"   {var}=us-central1")
        return False
    
    return True


def get_system_info():
    """시스템 정보 반환"""
    return {
        "model": "Vertex AI Gemini 2.0 Flash",
        "agents": ["축구_에이전트", "농구_에이전트", "야구_에이전트", "테니스_에이전트"],
        "features": ["가중치 기반 라우팅", "과거 패턴 분석", "실시간 A/B 테스트"]
    }


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