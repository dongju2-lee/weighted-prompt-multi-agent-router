# 🏃 가중치 기반 운동 추천 멀티 에이전트 시스템 - 상세 기술 문서

## 📝 시스템 개요

이 시스템은 **LangGraph**와 **Vertex AI Gemini**를 활용한 지능형 운동 추천 멀티 에이전트 시스템입니다. 사용자의 질문을 분석하여 4개의 전문 에이전트(축구, 농구, 야구, 테니스) 중 가장 적합한 에이전트를 자동 선택하고, 실시간 패턴 학습을 통해 지속적으로 향상됩니다.

### 🔥 핵심 특징

- **완전 동적 시스템**: 하드코딩된 패턴 없이 실제 선택 이력 기반 학습
- **구조화된 AI 응답**: Gemini 2.0의 Structured Output으로 안정적인 응답
- **실시간 가중치 조정**: API를 통한 실시간 에이전트 가중치 변경
- **자가 학습**: 각 선택이 미래 추천에 반영되는 적응형 시스템
- **상세한 모니터링**: 선택 통계, 이력 추적, 성능 분석

---

## 🏗️ 시스템 아키텍처

### 📂 전체 디렉토리 구조
```
src/
├── agent/                    # 멀티 에이전트 핵심 모듈
│   ├── __init__.py
│   ├── agents.py            # 각 에이전트 구현체
│   ├── graph.py             # LangGraph 워크플로우
│   ├── nodes.py             # 그래프 노드들
│   ├── prompts.py           # 프롬프트 생성 로직
│   ├── utils.py             # 유틸리티 함수들
│   └── weights.py           # 가중치 및 패턴 관리
├── run_dir/
│   └── run_api.py           # FastAPI 서버
├── test_dir/                # 테스트 디렉토리 (현재 위치)
│   ├── README.md           # 이 문서
│   ├── multi_test.sh       # 대규모 테스트 스크립트
│   ├── analyze_results.py  # 결과 분석 도구
│   └── test_results_*/     # 테스트 결과 디렉토리들
├── .env                     # 환경 변수 (실제)
├── .env.example             # 환경 변수 예시
├── requirements.txt         # 의존성 패키지
└── routing_history.json     # 선택 이력 저장소
```

### 🧩 시스템 컴포넌트

#### 1. **API 서버** (`run_dir/run_api.py`)
- **FastAPI** 기반 HTTP 서버
- RESTful API 엔드포인트 제공
- 요청 검증 및 응답 포맷팅

#### 2. **워크플로우 엔진** (`agent/graph.py`)
- **LangGraph** 기반 상태 기계
- 비동기 처리로 높은 성능
- 유연한 노드 간 라우팅

#### 3. **지능형 라우터** (`agent/nodes.py`)
- **Vertex AI Gemini** 기반 에이전트 선택
- 구조화된 출력으로 안정적인 파싱
- 3회 재시도 + 폴백 메커니즘

#### 4. **전문 에이전트** (`agent/agents.py`)
- 축구, 농구, 야구, 테니스 전문가
- 확장 가능한 에이전트 구조

#### 5. **패턴 학습 엔진** (`agent/weights.py`)
- 실시간 이력 저장 및 분석
- 가중치 기반 선택 확률 조정
- 동적 패턴 업데이트

---

## 🔄 요청 처리 플로우 (상세)

### 1️⃣ **API 요청 접수**
```
POST /sports-agent-route
{
  "query": "축구 하고 싶어"
}
```

**호출 함수**: `sports_agent_route()` in `run_api.py`
- 요청 데이터 검증
- 쿼리 추출 (`request.query` 또는 `request.user_query`)
- 워크플로우 호출

### 2️⃣ **워크플로우 초기화**
**호출 함수**: `run_sports_agent_workflow()` in `graph.py`

```python
async def run_sports_agent_workflow(user_query: str):
    # 1. LangGraph 워크플로우 생성
    app = create_sports_agent_graph()
    
    # 2. 초기 상태 설정
    initial_state = {
        "messages": [],
        "user_query": user_query,
        "selected_agent": "",
        "agent_response": {},
        "routing_info": {}
    }
    
    # 3. 비동기 실행
    result = await app.ainvoke(initial_state)
```

### 3️⃣ **슈퍼바이저 노드 실행**
**호출 함수**: `supervisor_node()` in `nodes.py`

#### 3.1 패턴 데이터 로딩
**호출 함수**: `get_routing_data_with_history()`
```python
# 실제 이력이 5개 이상이면 실제 데이터 사용, 아니면 Mock 데이터
base_ratios, total_traces = get_routing_data_with_history(user_query)
# 결과: {'축구_에이전트': 0.4, '농구_에이전트': 0.2, ...}
```

#### 3.2 가중치 적용
**호출 함수**: `get_default_agent_weights()` + `apply_weights_and_normalize()`
```python
# 환경변수에서 가중치 로드
agent_weights = get_default_agent_weights()
# 가중치 적용 및 정규화
normalized_ratios = apply_weights_and_normalize(base_ratios, agent_weights)
```

#### 3.3 프롬프트 생성
**호출 함수**: `generate_supervisor_prompt()` in `prompts.py`

```python
def generate_supervisor_prompt(user_query: str, normalized_ratios: dict, total_traces: int) -> str:
    return f"""
당신은 운동 추천 멀티 에이전트 시스템의 SUPERVISOR입니다.
사용자 질문: "{user_query}"

다음 4개의 전문 에이전트 중 정확히 하나를 선택해야 합니다:
🥅 축구_에이전트 - 축구, 풋살, 킥볼 관련 모든 활동
🏀 농구_에이전트 - 농구, 3x3 농구, 슛팅 연습 관련 활동  
⚾ 야구_에이전트 - 야구, 소프트볼, 타격 연습 관련 활동
🎾 테니스_에이전트 - 테니스, 배드민턴, 라켓 스포츠 관련 활동

=== 과거 사용자 패턴 데이터 (총 {total_traces}회) ===
{format_ratios(normalized_ratios)}

=== 판단 기준 ===
1. 사용자 질문의 키워드 분석 (가장 중요)
2. 과거 패턴 데이터 참고 (부차적 참고사항)
...
"""
```

#### 3.4 Gemini AI 호출
**호출 함수**: `initialize_gemini_model()` + `with_structured_output()`

```python
# Pydantic 모델로 구조화된 응답 정의
class AgentSelection(BaseModel):
    selected_agent: str
    reason: str
    confidence: float

# ChatVertexAI 모델 초기화
model = initialize_gemini_model()  # gemini-2.0-flash-lite
structured_model = model.with_structured_output(AgentSelection)

# 구조화된 응답 요청 (최대 3회 시도)
for attempt in range(1, 4):
    try:
        agent_selection = await loop.run_in_executor(
            None,
            lambda: structured_model.invoke(supervisor_prompt)
        )
        # 성공하면 break
        break
    except Exception as e:
        # 실패시 재시도 또는 폴백
```

#### 3.5 선택 결과 저장
**호출 함수**: `save_routing_choice()` in `weights.py`

```python
save_routing_choice(
    user_query=state["user_query"],
    selected_agent=agent_selection.selected_agent,
    confidence=agent_selection.confidence,
    reason=agent_selection.reason
)
# → routing_history.json에 추가
```

### 4️⃣ **에이전트 노드 실행**
**호출 함수**: `should_continue()` → 해당 에이전트 노드

```python
def should_continue(state: AgentState) -> str:
    selected_agent = state["selected_agent"]
    
    if selected_agent == "축구_에이전트":
        return "soccer"  # → soccer_node() 호출
    elif selected_agent == "농구_에이전트":
        return "basketball"  # → basketball_node() 호출
    # ...
```

#### 4.1 축구 에이전트 예시
**호출 함수**: `soccer_node()` → `soccer_agent()`

```python
async def soccer_node(state: AgentState) -> Dict[str, Any]:
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            soccer_agent,  # 실제 에이전트 함수 호출
            state["user_query"]
        )
        return {"agent_response": response}
    except Exception as e:
        # 에러 처리
```

#### 4.2 실제 에이전트 응답 생성
**호출 함수**: `soccer_agent()` in `agents.py`

```python
def soccer_agent(user_query: str) -> dict:
    return {
        "agent": "축구_에이전트",
        "answer": f"축구를 추천해드릴게요! 근처 축구장에서 풋살이나 축구 경기는 어떠세요?",
        "detail": "축구장 정보, 팀 매칭, 축구 용품 추천 등 축구 관련 모든 정보를 제공합니다."
    }
```

### 5️⃣ **응답 포맷팅 및 반환**
**호출 함수**: `sports_agent_route()` → `QueryResponse`

```python
return QueryResponse(
    success=True,
    user_query=user_query,
    selected_agent=result["selected_agent"],
    agent_response=result["agent_response"],
    routing_info=result["routing_info"]
)
```

---

## 📊 API 엔드포인트 상세

### 🎯 주요 엔드포인트

#### 1. **운동 추천 라우팅**
```http
POST /sports-agent-route
Content-Type: application/json

{
  "query": "축구 하고 싶어"
}
```

**응답 예시**:
```json
{
  "success": true,
  "user_query": "축구 하고 싶어",
  "selected_agent": "축구_에이전트",
  "agent_response": {
    "agent": "축구_에이전트",
    "answer": "축구를 추천해드릴게요! 근처 축구장에서 풋살이나 축구 경기는 어떠세요?",
    "detail": "축구장 정보, 팀 매칭, 축구 용품 추천 등 축구 관련 모든 정보를 제공합니다."
  },
  "routing_info": {
    "normalized_ratios": {
      "축구_에이전트": 0.4,
      "농구_에이전트": 0.2,
      "야구_에이전트": 0.2,
      "테니스_에이전트": 0.2
    },
    "total_traces": 182,
    "gemini_response": {
      "selected_agent": "축구_에이전트",
      "reason": "사용자 질문에 '축구'라는 키워드가 명확하게 포함되어 있어...",
      "confidence": 0.9
    },
    "agent_weights": {
      "축구_에이전트": 1.0,
      "농구_에이전트": 1.0,
      "야구_에이전트": 1.2,
      "테니스_에이전트": 0.8
    },
    "attempts_made": 1,
    "using_real_history": true
  }
}
```

#### 2. **라우팅 통계 조회**
```http
GET /routing-stats
```

**응답**:
```json
{
  "success": true,
  "statistics": {
    "total_requests": 45,
    "agent_counts": {
      "축구_에이전트": 18,
      "농구_에이전트": 12,
      "야구_에이전트": 10,
      "테니스_에이전트": 5
    },
    "agent_ratios": {
      "축구_에이전트": 0.4,
      "농구_에이전트": 0.267,
      "야구_에이전트": 0.222,
      "테니스_에이전트": 0.111
    }
  }
}
```

#### 3. **에이전트 가중치 조회**
```http
GET /agent-weights
```

#### 4. **에이전트 가중치 업데이트**
```http
POST /agent-weights
Content-Type: application/json

{
  "weights": {
    "축구_에이전트": 1.0,
    "야구_에이전트": 1.5,
    "테니스_에이전트": 0.8
  }
}
```

#### 5. **라우팅 이력 조회**
```http
GET /routing-history?limit=10
```

#### 6. **라우팅 이력 초기화**
```http
DELETE /routing-history
```

---

## 🛠️ 설치 및 설정

### 1️⃣ **필수 요구사항**
- Python 3.8+
- Google Cloud Project (Vertex AI 활성화)
- Google Cloud SDK

### 2️⃣ **환경 설정**

#### 프로젝트 클론
```bash
git clone <repository-url>
cd weighted-prompt-multi-agent-router
```

#### 가상환경 생성
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 의존성 설치
```bash
cd src
pip install -r requirements.txt
```

#### 환경 변수 설정
```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

**필수 환경 변수**:
```bash
# Google Cloud 설정 (필수)
GCP_PROJECT_ID=your-gcp-project-id
GCP_VERTEXAI_LOCATION=us-central1

# AI 모델 설정
SUPERVISOR_MODEL=gemini-2.0-flash-lite

# 에이전트 가중치 (선택)
WEIGHT_축구_에이전트=1.0
WEIGHT_농구_에이전트=1.0
WEIGHT_야구_에이전트=1.2
WEIGHT_테니스_에이전트=0.8
```

#### Google Cloud 인증
```bash
# gcloud CLI 설치 후
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 또는 서비스 계정 키 사용
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

### 3️⃣ **서버 실행**
```bash
cd src
python run_dir/run_api.py
```

서버가 성공적으로 시작되면:
```
🏃 운동 추천 멀티 에이전트 API 서버를 시작합니다...
======================================================================
🏃  가중치 기반 프롬프트 멀티 에이전트 라우터
🤖  Powered by Vertex AI Gemini
======================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🧪 종합 테스트 방법

### 1️⃣ **기본 API 테스트**

#### cURL 테스트
```bash
# 축구 관련 질문
curl -X POST "http://localhost:8000/sports-agent-route" \
  -H "Content-Type: application/json" \
  -d '{"query": "축구 하고 싶어"}'

# 농구 관련 질문  
curl -X POST "http://localhost:8000/sports-agent-route" \
  -H "Content-Type: application/json" \
  -d '{"query": "농구장 어디 있어?"}'

# 모호한 질문
curl -X POST "http://localhost:8000/sports-agent-route" \
  -H "Content-Type: application/json" \
  -d '{"query": "심심해"}'
```

#### Python requests 테스트
```python
import requests
import json

# 테스트 함수
def test_agent_routing(query):
    url = "http://localhost:8000/sports-agent-route"
    data = {"query": query}
    
    response = requests.post(url, json=data)
    result = response.json()
    
    print(f"질문: {query}")
    print(f"선택된 에이전트: {result['selected_agent']}")
    print(f"응답: {result['agent_response']['answer']}")
    print(f"확신도: {result['routing_info']['gemini_response']['confidence']}")
    print("-" * 50)

# 다양한 테스트 케이스
test_cases = [
    "축구 하고 싶어",
    "농구 배우고 싶어", 
    "야구장 어디 있어?",
    "테니스 레슨 받고 싶어",
    "심심해",
    "운동 추천해줘",
    "볼 차는 운동",
    "라켓 스포츠"
]

for query in test_cases:
    test_agent_routing(query)
```

### 2️⃣ **패턴 학습 테스트**

#### 연속 요청으로 패턴 확인
```bash
# 1. 초기 통계 확인
curl "http://localhost:8000/routing-stats"

# 2. 같은 종류 질문 반복 (5회 이상)
for i in {1..6}; do
  curl -X POST "http://localhost:8000/sports-agent-route" \
    -H "Content-Type: application/json" \
    -d '{"query": "심심해"}'
  sleep 1
done

# 3. 통계 변화 확인
curl "http://localhost:8000/routing-stats"

# 4. 이력 확인
curl "http://localhost:8000/routing-history?limit=10"
```

### 3️⃣ **가중치 조정 테스트**

#### 가중치 변경 및 영향 확인
```bash
# 1. 현재 가중치 확인
curl "http://localhost:8000/agent-weights"

# 2. 야구 에이전트 가중치 증가
curl -X POST "http://localhost:8000/agent-weights" \
  -H "Content-Type: application/json" \
  -d '{
    "weights": {
      "야구_에이전트": 2.0
    }
  }'

# 3. 모호한 질문으로 영향 테스트
for i in {1..10}; do
  curl -X POST "http://localhost:8000/sports-agent-route" \
    -H "Content-Type: application/json" \
    -d '{"query": "심심해"} | jq .selected_agent
  sleep 1
done

# 4. 통계로 가중치 영향 확인
curl "http://localhost:8000/routing-stats"
```

### 4️⃣ **대규모 성능 테스트 (multi_test.sh 사용)**

#### 500회 멀티프로세스 테스트
```bash
cd src/test_dir

# 테스트 실행 (500회, 50개 프로세스)
./multi_test.sh

# 결과 분석
python3 analyze_results.py test_results_YYYYMMDD_HHMMSS/
```

#### 테스트 설정 커스터마이징
```bash
# multi_test.sh 파일에서 설정 변경
API_URL="http://localhost:8000/sports-agent-route"
TEST_QUERY="심심해"                 # 테스트할 질문 변경
TOTAL_TESTS=1000                   # 테스트 횟수 증가
CONCURRENT_JOBS=100                # 동시 프로세스 수 증가
```

### 5️⃣ **동시 요청 성능 테스트**

#### Apache Bench 사용
```bash
# test_data.json 생성
echo '{"query": "축구 하고 싶어"}' > test_data.json

# 100개 요청, 10개 동시 연결
ab -n 100 -c 10 -T application/json -p test_data.json \
  http://localhost:8000/sports-agent-route
```

#### Python 비동기 테스트
```python
import asyncio
import aiohttp
import time

async def test_concurrent_requests():
    async with aiohttp.ClientSession() as session:
        tasks = []
        queries = ["축구 하고 싶어", "농구 하고 싶어", "야구 하고 싶어", "테니스 하고 싶어"] * 25
        
        start_time = time.time()
        
        for query in queries:
            task = session.post(
                "http://localhost:8000/sports-agent-route",
                json={"query": query}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"100개 요청 처리 시간: {end_time - start_time:.2f}초")
        print(f"평균 응답 시간: {(end_time - start_time) / 100:.2f}초")

# 실행
asyncio.run(test_concurrent_requests())
```

### 6️⃣ **에러 처리 테스트**

#### 잘못된 요청 테스트
```bash
# 빈 쿼리
curl -X POST "http://localhost:8000/sports-agent-route" \
  -H "Content-Type: application/json" \
  -d '{}'

# 잘못된 JSON
curl -X POST "http://localhost:8000/sports-agent-route" \
  -H "Content-Type: application/json" \
  -d '{"query":'

# 매우 긴 쿼리
curl -X POST "http://localhost:8000/sports-agent-route" \
  -H "Content-Type: application/json" \
  -d '{"query": "'$(python -c 'print("a" * 10000)')'"}''
```

### 7️⃣ **모니터링 테스트**

#### 시스템 상태 확인
```bash
# 헬스체크
curl "http://localhost:8000/health"

# 전체 API 정보
curl "http://localhost:8000/"

# 에이전트별 선택 비율 모니터링
watch -n 5 'curl -s "http://localhost:8000/routing-stats" | jq .statistics.agent_ratios'
```

### 8️⃣ **통합 테스트 스크립트**

```python
#!/usr/bin/env python3
"""
통합 테스트 스크립트
"""
import requests
import json
import time
from typing import List, Dict

class AgentTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_basic_routing(self):
        """기본 라우팅 테스트"""
        print("🧪 기본 라우팅 테스트 시작...")
        
        test_cases = [
            ("축구 하고 싶어", "축구_에이전트"),
            ("농구 배우고 싶어", "농구_에이전트"),
            ("야구장 어디 있어?", "야구_에이전트"),
            ("테니스 레슨 받고 싶어", "테니스_에이전트"),
        ]
        
        for query, expected_agent in test_cases:
            response = self.session.post(
                f"{self.base_url}/sports-agent-route",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                selected = result['selected_agent']
                success = selected == expected_agent
                print(f"✅ {query} → {selected} {'✓' if success else '✗'}")
            else:
                print(f"❌ {query} → HTTP {response.status_code}")
    
    def test_pattern_learning(self):
        """패턴 학습 테스트"""
        print("\n🧪 패턴 학습 테스트 시작...")
        
        # 이력 초기화
        self.session.delete(f"{self.base_url}/routing-history")
        
        # 동일 질문 반복
        query = "심심해"
        selections = []
        
        for i in range(10):
            response = self.session.post(
                f"{self.base_url}/sports-agent-route",
                json={"query": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                selections.append(result['selected_agent'])
                time.sleep(0.5)
        
        # 분포 확인
        from collections import Counter
        distribution = Counter(selections)
        print(f"✅ 10회 '{query}' 질문 결과:")
        for agent, count in distribution.items():
            print(f"   {agent}: {count}회 ({count/10*100:.1f}%)")
    
    def test_weight_adjustment(self):
        """가중치 조정 테스트"""
        print("\n🧪 가중치 조정 테스트 시작...")
        
        # 가중치 조정
        response = self.session.post(
            f"{self.base_url}/agent-weights",
            json={
                "weights": {
                    "야구_에이전트": 3.0,
                    "테니스_에이전트": 0.1
                }
            }
        )
        
        if response.status_code == 200:
            print("✅ 가중치 조정 완료 (야구↑, 테니스↓)")
            
            # 영향 테스트
            selections = []
            for i in range(20):
                response = self.session.post(
                    f"{self.base_url}/sports-agent-route",
                    json={"query": "심심해"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    selections.append(result['selected_agent'])
                    time.sleep(0.2)
            
            from collections import Counter
            distribution = Counter(selections)
            print(f"✅ 가중치 조정 후 20회 테스트 결과:")
            for agent, count in distribution.items():
                print(f"   {agent}: {count}회 ({count/20*100:.1f}%)")
        else:
            print("❌ 가중치 조정 실패")
    
    def run_all_tests(self):
        """전체 테스트 실행"""
        print("🚀 통합 테스트 시작\n")
        
        # 서버 상태 확인
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ 서버 연결 성공\n")
            else:
                print("❌ 서버 연결 실패")
                return
        except Exception as e:
            print(f"❌ 서버 연결 불가: {e}")
            return
        
        self.test_basic_routing()
        self.test_pattern_learning()
        self.test_weight_adjustment()
        
        print("\n🎉 통합 테스트 완료!")

if __name__ == "__main__":
    tester = AgentTester()
    tester.run_all_tests()
```

실행:
```bash
cd src/test_dir
python test_integration.py
```

---

## 🔧 고급 설정 및 커스터마이징

### 새로운 에이전트 추가

#### 1. 에이전트 함수 추가 (`agents.py`)
```python
def swimming_agent(user_query: str) -> dict:
    return {
        "agent": "수영_에이전트",
        "answer": f"수영을 추천해드릴게요! 수영장에서 자유형이나 접영은 어떠세요?",
        "detail": "수영장 정보, 레슨 예약, 수영 기술 가이드 등을 제공합니다."
    }
```

#### 2. 노드 추가 (`nodes.py`)
```python
async def swimming_node(state: AgentState) -> Dict[str, Any]:
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            swimming_agent,
            state["user_query"]
        )
        return {"agent_response": response}
    except Exception as e:
        print(f"❌ 수영 에이전트 오류: {e}")
        return {"agent_response": {"agent": "수영_에이전트", "answer": "오류 발생", "detail": "시스템 오류"}}
```

#### 3. 그래프 수정 (`graph.py`)
```python
def create_sports_agent_graph():
    workflow = StateGraph(AgentState)
    
    # 기존 노드들...
    workflow.add_node("swimming", swimming_node)
    
    # 조건부 엣지에 추가
    workflow.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "soccer": "soccer",
            "basketball": "basketball", 
            "baseball": "baseball",
            "tennis": "tennis",
            "swimming": "swimming"  # 새 에이전트 추가
        }
    )
    
    workflow.add_edge("swimming", END)
```

#### 4. 라우팅 로직 수정 (`nodes.py`)
```python
def should_continue(state: AgentState) -> str:
    selected_agent = state["selected_agent"]
    
    if selected_agent == "축구_에이전트":
        return "soccer"
    elif selected_agent == "농구_에이전트":
        return "basketball"
    elif selected_agent == "야구_에이전트":
        return "baseball"
    elif selected_agent == "테니스_에이전트":
        return "tennis"
    elif selected_agent == "수영_에이전트":  # 새 에이전트
        return "swimming"
    else:
        return "soccer"
```

### 환경별 설정

#### 개발 환경 (`src/.env.dev`)
```bash
SUPERVISOR_MODEL=gemini-2.0-flash-lite
SYSTEM_DEBUG=true
LOG_LEVEL=10
LANGFUSE_ENABLED=false
```

#### 프로덕션 환경 (`src/.env.prod`)
```bash
SUPERVISOR_MODEL=gemini-2.0-flash
SYSTEM_DEBUG=false
LOG_LEVEL=20
LANGFUSE_ENABLED=true
LANGFUSE_SECRET_KEY=sk-xxx
LANGFUSE_PUBLIC_KEY=pk-xxx
```

---

## 🚨 트러블슈팅

### 자주 발생하는 문제들

#### 1. **Vertex AI 인증 오류**
```
❌ 시도 1 실패: 404 Publisher Model was not found
```

**해결책**:
```bash
# 1. 프로젝트 ID 확인
gcloud config get-value project

# 2. Vertex AI API 활성화
gcloud services enable aiplatform.googleapis.com

# 3. 인증 재설정
gcloud auth application-default login

# 4. 리전 확인 (us-central1 권장)
```

#### 2. **환경 변수 누락**
```
❌ 환경변수 검증 실패: GCP_PROJECT_ID
```

**해결책**:
```bash
# .env 파일 확인
cat src/.env

# 필수 변수 설정
echo "GCP_PROJECT_ID=your-project-id" >> src/.env
echo "GCP_VERTEXAI_LOCATION=us-central1" >> src/.env
```

#### 3. **모델 버전 오류**
```
❌ 404 Publisher Model gemini-1.5-flash was not found
```

**해결책**:
```bash
# .env에서 모델 변경
SUPERVISOR_MODEL=gemini-2.0-flash-lite
```

#### 4. **포트 충돌**
```
❌ [Errno 48] Address already in use
```

**해결책**:
```bash
# 8000번 포트 사용중인 프로세스 확인
lsof -i :8000

# 프로세스 종료
kill -9 <PID>

# 또는 다른 포트 사용
uvicorn run_api:app --port 8080
```

#### 5. **메모리 부족**
```
❌ 워크플로우 실행 오류: Out of memory
```

**해결책**:
```bash
# 시스템 리소스 확인
free -h

# Python 메모리 제한 설정
export PYTHONHASHSEED=0
ulimit -v 4194304  # 4GB 제한
```

---

## 📈 모니터링 및 최적화

### 성능 메트릭 수집

#### 응답 시간 로깅
```python
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"⏱️ {func.__name__}: {end - start:.2f}초")
        return result
    return wrapper

# 노드에 적용
@measure_time
async def supervisor_node(state: AgentState):
    # 기존 코드...
```

#### 선택 정확도 분석
```python
def analyze_selection_accuracy():
    """선택 정확도 분석"""
    history = load_routing_history()
    
    keyword_matches = {
        "축구": "축구_에이전트",
        "농구": "농구_에이전트", 
        "야구": "야구_에이전트",
        "테니스": "테니스_에이전트"
    }
    
    correct = 0
    total = 0
    
    for record in history:
        query = record["user_query"].lower()
        selected = record["selected_agent"]
        
        for keyword, expected_agent in keyword_matches.items():
            if keyword in query:
                if selected == expected_agent:
                    correct += 1
                total += 1
                break
    
    accuracy = correct / total if total > 0 else 0
    print(f"📊 키워드 기반 정확도: {accuracy:.2f} ({correct}/{total})")
```

---

## 🔗 관련 자료

### 공식 문서
- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [Vertex AI Python SDK](https://cloud.google.com/vertex-ai/docs/python-sdk/use-vertex-ai-python-sdk)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)

### 참고 논문
- [Multi-Agent Systems for AI](https://arxiv.org/abs/2308.10848)
- [Large Language Model Routing](https://arxiv.org/abs/2309.15025)

---

## 📜 라이센스

MIT License - 자세한 내용은 LICENSE 파일을 참조하세요.

---

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 문의

프로젝트 관련 문의나 버그 리포트는 GitHub Issues를 이용해 주세요.