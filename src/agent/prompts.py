"""
프롬프트 생성 모듈 (운동 추천 에이전트 버전)
"""
from typing import Dict


def generate_supervisor_prompt(user_query: str, normalized_ratios: Dict[str, float], total_traces: int) -> str:
    """
    과거 패턴 데이터를 기반으로 한 슈퍼바이저 프롬프트 생성 (Structured Output 버전)
    """
    return f"""
당신은 운동 추천 멀티 에이전트 시스템의 SUPERVISOR입니다.

사용자 질문: "{user_query}"

다음 4개의 전문 에이전트 중 정확히 하나를 선택해야 합니다:

🥅 축구_에이전트 - 축구, 풋살, 킥볼 관련 모든 활동
🏀 농구_에이전트 - 농구, 3x3 농구, 슛팅 연습 관련 활동  
⚾ 야구_에이전트 - 야구, 소프트볼, 타격 연습 관련 활동
🎾 테니스_에이전트 - 테니스, 배드민턴, 라켓 스포츠 관련 활동

=== 과거 사용자 패턴 데이터 (총 {total_traces}회) ===
축구_에이전트: {normalized_ratios.get('축구_에이전트', 0):.1%}
농구_에이전트: {normalized_ratios.get('농구_에이전트', 0):.1%}
야구_에이전트: {normalized_ratios.get('야구_에이전트', 0):.1%}
테니스_에이전트: {normalized_ratios.get('테니스_에이전트', 0):.1%}

=== 판단 기준 ===
1. 사용자 질문의 키워드 분석 (가장 중요)
2. 과거 패턴 데이터 참고 (부차적 참고사항)
3. 운동 종목 관련성
4. 꼭 퍼센트가 높다고 우선순위가 절대적으로 높은건 아닙니다.
5. 만약 40%이면 100번중 40번은 해당 에이전트가 선택되었다는 의미입니다.
6. 만약 0%이면 100번중 0번은 해당 에이전트가 선택되었다는 의미입니다.
7. 에이전트의 순서가 우선순위가 아닙니다. 적절하게 선택하세요.
8. 분포가 균등하다고 첫번째 에이전트를 선택하지 마세요.
9. 분포가 균등하면 주사위를 던지는 것처럼 스스로 확률에 맡기세요.

분석해서 가장 적합한 에이전트를 선택하고, 구체적인 이유와 확신도(0.0~1.0)를 제공하세요.

⚠️ 중요: 에이전트명은 다음 중 정확히 하나여야 합니다:
- 축구_에이전트
- 농구_에이전트
- 야구_에이전트  
- 테니스_에이전트
"""


def get_welcome_message() -> str:
    """환영 메시지 반환"""
    return """======================================================================
🏃  가중치 기반 프롬프트 멀티 에이전트 라우터
🤖  Powered by Vertex AI Gemini
======================================================================

🔥 시스템 특징:
• Vertex AI Gemini 2.0 Flash 모델 사용
• 과거 라우팅 패턴 기반 지능형 에이전트 선택
• 실시간 가중치 조정으로 A/B 테스트 지원

🤖 사용 가능한 에이전트:
• 축구 에이전트: 축구 관련 정보 및 활동 추천
• 농구 에이전트: 농구 관련 정보 및 활동 추천
• 야구 에이전트: 야구 관련 정보 및 활동 추천
• 테니스 에이전트: 테니스 관련 정보 및 활동 추천

💡 예시 질문:
- '축구 하고 싶어'
- '농구장 어디 있어?'
- '야구 배우고 싶어'
- '테니스 레슨 받고 싶어'
- '심심해'

⚙️  환경 설정:
GCP_PROJECT_ID와 GCP_VERTEXAI_LOCATION을 .env 파일에 설정해주세요.

종료하려면 'quit' 또는 'exit'를 입력하세요.
----------------------------------------------------------------------"""


def get_agent_descriptions() -> Dict[str, str]:
    """에이전트별 상세 설명 반환"""
    return {
        "축구_에이전트": "축구장 정보, 팀 매칭, 축구 기술 연습법을 제공합니다.",
        "농구_에이전트": "농구장 정보, 팀 구성, 농구 기술 연습법을 제공합니다.",
        "야구_에이전트": "야구장 정보, 팀 가입, 야구 기술 향상법을 제공합니다.",
        "테니스_에이전트": "테니스장 예약, 레슨 정보, 파트너 매칭을 제공합니다."
    } 