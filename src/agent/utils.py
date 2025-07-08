"""
유틸리티 함수 모듈 (운동 추천 에이전트 버전)
"""
import os
import re
from typing import Dict, Any, Optional, Literal
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel
from langchain_google_vertexai import ChatVertexAI
from langfuse import Langfuse
from google.cloud import aiplatform
from pydantic import BaseModel, Field

# 환경 변수 로드
load_dotenv()

# 전역 모델 캐시 (성능 최적화)
_cached_gemini_model: Optional[ChatVertexAI] = None
_cached_langfuse_client: Optional[Langfuse] = None


class AgentSelection(BaseModel):
    """에이전트 선택 결과를 위한 구조화된 출력"""
    selected_agent: Literal["축구_에이전트", "농구_에이전트", "야구_에이전트", "테니스_에이전트"] = Field(
        description="선택된 에이전트명 (정확히 4개 중 하나만 가능)"
    )
    reason: str = Field(
        description="선택 이유에 대한 구체적인 설명"
    )
    confidence: float = Field(
        description="선택 확신도 (0.0~1.0)", 
        ge=0.0, 
        le=1.0
    )


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
    """Gemini 모델 초기화 (LangChain ChatVertexAI)"""
    try:
        # 환경변수 읽기
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_VERTEXAI_LOCATION", "us-central1")
        model_name = os.getenv("SUPERVISOR_MODEL", "gemini-1.5-flash")
        
        if not project_id:
            raise ValueError("GCP_PROJECT_ID 환경변수가 설정되지 않았습니다.")
        
        # ChatVertexAI 모델 초기화
        model = ChatVertexAI(
            model=model_name,
            project=project_id,
            location=location,
            temperature=0.1,  # 일관성을 위해 낮은 temperature
        )
        print(f"✅ ChatVertexAI 모델 초기화 완료: {model_name} (Project: {project_id})")
        
        return model
    except Exception as e:
        print(f"❌ Gemini 모델 초기화 실패: {e}")
        raise


def extract_agent_name(llm_response: str) -> str:
    """
    LLM 응답에서 에이전트 이름 추출 (운동 추천 에이전트)
    백업 매칭 없이 오직 정규표현식으로만 처리
    """
    # 운동 에이전트 이름들
    valid_agents = [
        "축구_에이전트",
        "농구_에이전트", 
        "야구_에이전트",
        "테니스_에이전트"
    ]
    
    print(f"🔍 extract_agent_name 분석:")
    print(f"   Gemini 응답: {llm_response[:300]}...")
    
    # 정규표현식으로 "선택된 에이전트:" 패턴 찾기
    agent_pattern = r"선택된\s*에이전트\s*:\s*([가-힣_]+)"
    match = re.search(agent_pattern, llm_response)
    
    if match:
        extracted_agent = match.group(1).strip()
        print(f"   정규표현식 추출 결과: '{extracted_agent}'")
        
        # 추출된 에이전트가 유효한 에이전트 목록에 있는지 확인
        if extracted_agent in valid_agents:
            print(f"   ✅ 성공: {extracted_agent}")
            return extracted_agent
        else:
            print(f"   ❌ 유효하지 않은 에이전트명: '{extracted_agent}'")
            print(f"   📋 유효한 에이전트: {valid_agents}")
            raise ValueError(f"유효하지 않은 에이전트명: '{extracted_agent}'. Gemini가 올바른 형식으로 응답하지 않았습니다.")
    else:
        print(f"   ❌ '선택된 에이전트:' 패턴을 찾을 수 없음")
        print(f"   📋 유효한 에이전트: {valid_agents}")
        raise ValueError("Gemini 응답에서 '선택된 에이전트:' 패턴을 찾을 수 없습니다. 프롬프트를 다시 확인해주세요.")


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