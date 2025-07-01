# 가중치 기반 프롬프트 멀티 에이전트 라우터

## 🚀 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# Google Cloud 설정 (필수)
GCP_PROJECT_ID=your-gcp-project-id
GCP_VERTEXAI_LOCATION=us-central1

# AI 모델 설정
SUPERVISOR_MODEL=gemini-2.0-flash

# 시스템 설정
SYSTEM_DEBUG=false
LOG_LEVEL=20

# LangFuse 추적 설정 (선택사항)
LANGFUSE_ENABLED=false
LANGFUSE_SECRET_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_HOST=http://localhost:3000
```

### 3. Google Cloud 인증 설정

Google Cloud 인증을 설정하세요:

```bash
# Application Default Credentials 설정
gcloud auth application-default login

# 또는 서비스 계정 키 파일 사용
export GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
```

### 4. 시스템 실행

```bash
python run.py
```

또는

```bash
python multi_agent_system.py
```

## 🎯 사용 방법

시스템이 시작되면 콘솔에서 음식 관련 질문을 입력할 수 있습니다:

- "집에서 만들 수 있는 요리 추천해줘"
- "맛있는 음식점 추천해줘"
- "김치볶음밥 레시피 알려줘"
- "다이어트에 좋은 음식 추천해줘"
- "오늘 저녁 뭐 먹지?"

## 🤖 시스템 구조

### 에이전트 구성
1. **냉장고 재료 에이전트**: 집에 있는 재료로 요리 추천
2. **음식점 추천 에이전트**: 외식 장소 추천
3. **레시피 검색 에이전트**: 상세한 요리법 제공
4. **건강식 컨설팅 에이전트**: 건강 목적 음식 추천

### 핵심 기능
- **Vertex AI Gemini 2.0 Flash**: 지능형 슈퍼바이저 라우팅
- **가중치 기반 라우팅**: 과거 패턴 + 실시간 가중치 조정
- **A/B 테스트 지원**: 에이전트별 가중치 조정으로 트래픽 제어
- **자동 대체 로직**: Gemini 호출 실패 시 규칙 기반 라우팅

## 📊 시스템 동작 방식

1. 사용자 질문 입력
2. 과거 유사 질문 패턴 분석 (Mock 데이터)
3. 가중치 적용 및 정규화
4. Gemini 모델에 히스토리컬 데이터와 함께 프롬프트 전송
5. Gemini의 라우팅 결정
6. 선택된 에이전트 실행
7. 결과 반환

## ⚙️ 설정 변경

`multi_agent_system.py`의 `supervisor_node` 함수에서 에이전트별 가중치를 조정할 수 있습니다:

```python
agent_weights = {
    "냉장고_재료_에이전트": 1.0,
    "음식점_추천_에이전트": 1.0, 
    "레시피_검색_에이전트": 1.0,
    "건강식_컨설팅_에이전트": 1.2  # 20% 더 우선
}
```

## 🔧 문제 해결

### GCP 인증 오류
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 모델 접근 권한 오류
Vertex AI API가 활성화되어 있는지 확인하세요:
```bash
gcloud services enable aiplatform.googleapis.com
```

## 📝 로그 확인

시스템은 실행 중 다음 정보를 출력합니다:
- 과거 라우팅 패턴 분석 결과
- Gemini 모델의 라우팅 결정
- 선택된 에이전트와 응답
- 신뢰도 및 추가 메타데이터 