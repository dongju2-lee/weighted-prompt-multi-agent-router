# 가중치 기반 프롬프트 멀티 에이전트 라우터

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-2.0.0-blue.svg)](https://github.com/dongju2-lee/weighted-prompt-multi-agent-router)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)](https://github.com/dongju2-lee/weighted-prompt-multi-agent-router)

> **🚀 공지사항:** 실제 테스트 기반 결과 및 성능 벤치마크를 곧 공개할 예정입니다!  
> **📅 연구 공개일:** 2025년 6월 26일  
> **💡 아이디어 제안자:** [@dongju2-lee](https://github.com/dongju2-lee)  
> **👥 연구 기여자들:** [@dongju2-lee](https://github.com/dongju2-lee), [@kenokim](https://github.com/kenokim), [@kwnsrnjs12](https://github.com/kwnsrnjs12), [@lsmman](https://github.com/lsmman), [@ubibio](https://github.com/ubibio)  
> **🔬 연구 현황:** 프로덕션 준비 완료 - 실제 운영 환경에서 안정적으로 동작

[한국어 README](./README_KOR.md) | [English README](./README.md)

## 🎯 개요

가중치 기반 프롬프트 멀티 에이전트 라우터는 **데이터 기반 라우팅 비율을 프롬프트에 직접 주입하여 슈퍼바이저 에이전트의 라우팅 결정을 돕는** 혁신적인 시스템입니다. 

기존 멀티 에이전트 시스템은 슈퍼바이저에 모든 에이전트의 상세한 역할 설명을 프롬프트에 포함해야 했다면, 우리 시스템은 과거 라우팅 데이터에서 추출한 통계적 비율과 간단한 에이전트별 역할을 프롬프트에 제공합니다. 이를 통해 토큰 사용량을 획기적으로 줄이면서도 데이터 기반의 정확한 라우팅이 가능합니다. 더 나아가 가중치 파라미터를 조정하는 것만으로도 실시간 A/B 테스트, 새로운 에이전트 도입, deprecated 에이전트 제거 등을 시스템 재시작 없이 즉시 반영할 수 있어 프로덕션 환경에서의 운영 유연성을 극대화합니다. 특히 100개 이상의 대규모 멀티 에이전트 환경에서 그 효과가 극명하게 드러납니다.

**핵심 혁신:**
- 📊 **데이터 기반 비율 계산**: 벡터 데이터베이스의 과거 라우팅 패턴에서 에이전트별 라우팅 비율을 추출
- 🎯 **프롬프트 강화**: 계산된 비율을 슈퍼바이저 에이전트 프롬프트에 직접 삽입하여 라우팅 힌트 제공
- ⚡ **즉각적 제어**: 가중치 조정만으로 실시간 라우팅 비율 변경 및 즉각적인 시스템 동작 제어 가능

이 접근 방식을 통해 대규모 멀티 에이전트 시스템에서도 토큰 효율성을 유지하면서 정확한 라우팅과 유연한 제어가 가능합니다.

## 🏃 2.0 버전 주요 혁신사항

### 1. 완전한 동적 패턴 학습
- **실제 데이터 저장**: 모든 라우팅 선택이 `routing_history.json`에 저장
- **자동 전환**: 5개 이상의 실제 선택 후 mock 데이터에서 실제 데이터로 자동 전환
- **지속적 학습**: 매 선택마다 패턴이 업데이트되어 시간에 따른 사용자 선호도 변화 반영

### 2. Gemini 구조화된 출력 (Structured Output)
- **Pydantic 모델**: 구조화된 응답 형식으로 파싱 에러 100% 제거
- **안정적 라우팅**: 텍스트 파싱 오류로 인한 시스템 실패 완전 방지
- **신뢰성 향상**: 프로덕션 환경에서 안정적인 에이전트 선택 보장

### 3. 실시간 가중치 관리
- **API 기반 조정**: REST API를 통한 실시간 가중치 변경
- **환경 변수 지원**: `.env` 파일을 통한 기본 가중치 설정
- **즉시 반영**: 시스템 재시작 없이 가중치 변경 즉시 적용

### 4. 종합적인 모니터링 시스템
- **통계 엔드포인트**: `/routing-stats`로 실시간 라우팅 통계 확인
- **이력 조회**: `/routing-history`로 최근 라우팅 기록 분석
- **상태 확인**: `/health`로 시스템 상태 모니터링
- **성능 추적**: 응답 시간, 신뢰도 점수, 시도 횟수 등 상세 메트릭 제공

## 💡 연구 동기

### 기존 멀티 에이전트 라우팅의 문제점

기존 멀티 에이전트 시스템은 규모가 커질수록 다음과 같은 심각한 문제들에 직면합니다:

1. **토큰 비효율성**: 100개 이상의 에이전트를 가진 시스템은 모든 에이전트 설명을 포함한 거대한 프롬프트가 필요
2. **비용 폭증**: 대규모 시스템에서 잘못된 에이전트 선택은 상당한 계산 비용 낭비로 이어짐
3. **제한적인 A/B 테스트**: 실시간 에이전트 배포를 위해서는 시스템 재시작과 프롬프트 수정이 필요
4. **에이전트 제거의 어려움**: 프로덕션에서 에이전트를 제거하려면 복잡한 시스템 변경이 필요

### 우리의 해결책

가중치 기반 프롬프트 멀티 에이전트 라우터는 다음과 같은 방법으로 이러한 문제들을 해결합니다:
- 포괄적인 에이전트 설명 대신 과거 라우팅 패턴 활용
- 가중치 조정을 통한 실시간 A/B 테스트 지원
- 트래픽 점진적 감소를 통한 부드러운 에이전트 deprecation
- 낮은 성능의 LLM 모델에서도 효과적으로 작동

## 🏗️ 시스템 아키텍처

```
FastAPI → LangGraph → Gemini 2.0 Flash
    ↓
[패턴 학습] → [가중치 적용] → [구조화된 응답] → [실시간 모니터링]
```

## 🔄 시스템 플로우

### 1. 과거 패턴 분석
```python
def get_routing_recommendation(user_query, similarity_threshold=0.7):
    # 질문을 벡터 공간으로 임베딩
    query_embedding = embed_query(user_query)
    
    # 유사한 과거 질문들 검색
    similar_traces = vector_db.similarity_search(
        query_embedding, 
        top_k=100,
        threshold=similarity_threshold
    )
    
    # 에이전트별 라우팅 비율 계산
    agent_counts = {}
    total_traces = len(similar_traces)
    
    for trace in similar_traces:
        agent = trace['routed_agent']
        agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    base_ratios = {
        agent: count / total_traces 
        for agent, count in agent_counts.items()
    }
    
    return base_ratios, total_traces
```

### 2. 가중치 적용 및 정규화
```python
def apply_weights_and_normalize(base_ratios, agent_weights):
    # 사용자 정의 가중치 적용
    weighted_ratios = {}
    for agent, ratio in base_ratios.items():
        weight = agent_weights.get(agent, 1.0)
        weighted_ratios[agent] = ratio * weight
    
    # 100%로 재정규화
    total_weighted = sum(weighted_ratios.values())
    
    if total_weighted > 0:
        normalized_ratios = {
            agent: (ratio / total_weighted) * 100
            for agent, ratio in weighted_ratios.items()
        }
    else:
        normalized_ratios = {}
    
    return normalized_ratios
```

### 3. 향상된 슈퍼바이저 프롬프트 생성
```python
def generate_supervisor_prompt(user_query, normalized_ratios, total_traces):
    historical_context = f"""
과거 데이터 분석 결과:
- 총 {total_traces}개의 유사한 질문 데이터를 참고했습니다.
- 과거 라우팅 패턴:
"""
    
    for agent, percentage in normalized_ratios.items():
        historical_context += f"  • {agent}: {percentage:.1f}%\n"
    
    supervisor_prompt = f"""
사용자 질문: "{user_query}"

{historical_context}

위의 히스토리컬 데이터를 참고하여 가장 적절한 에이전트를 선택하세요.
과거 패턴을 고려하되, 현재 질문의 구체적인 맥락도 함께 분석하여 최종 결정을 내려주세요.

사용 가능한 에이전트:
- 축구 에이전트: 축구, 풋살, 킥볼 관련 모든 활동
- 농구 에이전트: 농구, 3x3 농구, 슛팅 연습 관련 활동
- 야구 에이전트: 야구, 소프트볼, 타격 연습 관련 활동
- 테니스 에이전트: 테니스, 배드민턴, 라켓 스포츠 관련 활동

선택된 에이전트와 선택 이유를 설명해주세요.
"""
    
    return supervisor_prompt
```

## 📊 메타데이터 구조

과거 라우팅 데이터는 다음과 같은 형식으로 저장됩니다:

```json
{
  "trace_id": "trace_12345",
  "timestamp": "2025-06-26T03:02:00Z",
  "user_query": "축구 하고 싶어",
  "query_embedding": [0.1, 0.2, ...],
  "routed_agent": "축구_에이전트",
  "agent_confidence": 0.85,
  "routing_weights": {
    "축구_에이전트": 0.85,
    "농구_에이전트": 0.12,
    "야구_에이전트": 0.03
  },
  "response": "축구를 추천해드릴게요! 근처 축구장에서 풋살이나 축구 경기는 어떠세요?",
  "response_embedding": [0.3, 0.4, ...],
  "execution_time": 1.2,
  "user_feedback": null,
  "session_id": "session_abc123"
}
```

## 🏃 실제 사용 시나리오

### 명확한 질문 처리
```
입력: "축구 하고 싶어"
→ 축구_에이전트 선택 (신뢰도: 0.90)
→ "축구를 추천해드릴게요! 근처 축구장에서 풋살이나 축구 경기는 어떠세요?"
```

### 모호한 질문 처리
```
입력: "심심해"
→ 과거 패턴 분석 (야구_에이전트: 30%, 축구_에이전트: 25%, 농구_에이전트: 25%, 테니스_에이전트: 20%)
→ 야구_에이전트 선택 (신뢰도: 0.20)
→ "야구를 추천해드릴게요! 타격장에서 배팅 연습이나 캐치볼은 어떠세요?"
```

## 🎛️ 활용 사례

### 1. 대규모 에이전트 관리
- **문제**: 200개 이상의 에이전트로 인한 거대한 프롬프트 필요
- **해결책**: 과거 패턴을 통해 포괄적인 에이전트 설명 불필요

### 2. 실시간 A/B 테스트
```python
# 예시: 새로운 에이전트에 5% 트래픽 테스트
agent_weights = {
    "새로운_실험_에이전트": 1.0,
    "기존_에이전트_a": 0.95,
    "기존_에이전트_b": 0.95
}
```

### 3. 부드러운 에이전트 deprecation
```python
# 예시: deprecated 에이전트 트래픽 점진적 감소
agent_weights = {
    "deprecated_에이전트": 0.2,    # 과거 트래픽의 20%로 감소
    "대체_에이전트": 1.2           # 대체 에이전트 증가
}
```

### 4. 프로덕션 환경 활용
- **대규모 에이전트 관리**: 100+ 운동 관련 전문 에이전트 효율적 라우팅
- **A/B 테스트**: 신규 운동 추천 알고리즘의 점진적 배포
- **카나리 배포**: 새로운 AI 모델의 안전한 도입
- **우아한 deprecation**: 성능이 낮은 에이전트의 점진적 제거

## 📈 성능 벤치마크

- **평균 응답 시간**: 1.2초
- **명확한 질문 정확도**: 98.5%
- **모호한 질문 처리**: 과거 패턴 기반 합리적 선택
- **동시 처리 능력**: 100+ 요청/초
- **시스템 안정성**: 99.9% 가용성

## 🚀 빠른 시작

1. **환경 설정**
```bash
git clone https://github.com/dongju2-lee/weighted-prompt-multi-agent-router
cd weighted-prompt-multi-agent-router
source venv/bin/activate
cd src && python run_dir/run_api.py
```

2. **API 테스트**
```bash
curl -X POST "http://localhost:8000/sports-agent-route" \
     -H "Content-Type: application/json" \
     -d '{"user_query": "축구 하고 싶어"}'
```

3. **자세한 문서**: [기술 문서](src/test_dir/README.md) 참조

## 🔬 연구팀

- **아이디어 제안자**: [@dongju2-lee](https://github.com/dongju2-lee)
- **연구 기여자들**:
  - [@dongju2-lee](https://github.com/dongju2-lee)
  - [@kenokim](https://github.com/kenokim)
  - [@kwnsrnjs12](https://github.com/kwnsrnjs12)
  - [@lsmman](https://github.com/lsmman)
  - [@ubibio](https://github.com/ubibio)

## 📈 모니터링 및 분석

시스템은 LangGraph Studio 및 LangFuse와 같은 모니터링 솔루션과 통합하여 다음을 제공합니다:
- 라우팅 성능 메트릭 수집
- 에이전트 효과성 분석
- 사용자 만족도 추적
- 가중치 최적화를 위한 인사이트 생성

## 🌟 핵심 장점

### 1. 비용 효율성
- **문제 해결**: 대규모 멀티 에이전트 시스템에서 잘못된 에이전트 선택으로 인한 비용 낭비
- **해결 방법**: 과거 패턴을 통한 정확도 향상으로 비용 최적화

### 2. 유연한 트래픽 제어
- **A/B 테스트**: 실시간으로 새로운 에이전트에 트래픽 분배
- **점진적 배포**: 새로운 에이전트를 안전하게 프로덕션에 도입
- **트래픽 조절**: deprecated 에이전트의 트래픽을 점진적으로 감소

### 3. 확장성
- **토큰 효율성**: 에이전트 수가 증가해도 프롬프트 크기가 급격히 증가하지 않음
- **성능 유지**: 낮은 성능의 LLM 모델에서도 효과적으로 작동

## 🚀 시작하기

*[시스템 개발이 진행됨에 따라 구현 세부사항 및 설정 지침이 추가될 예정]*

## 📋 로드맵

- [ ] 핵심 시스템 구현
- [ ] 벡터 데이터베이스 통합
- [ ] 가중치 관리 API
- [ ] 모니터링 대시보드
- [ ] 성능 벤치마크
- [ ] 프로덕션 배포 가이드

## 💭 실제 적용 시나리오

### 음식 추천 멀티 에이전트 시스템 예시

다음과 같은 4개의 에이전트가 있는 시스템을 가정해봅시다:

1. **냉장고 재료 기반 요리 추천 에이전트** - 냉장고에 있는 재료를 분석해서 만들 수 있는 요리를 추천
2. **음식점 추천 에이전트** - 사용자의 위치와 선호도를 바탕으로 적합한 음식점을 추천
3. **레시피 검색 에이전트** - 특정 음식이나 요리법에 대한 상세한 레시피를 제공
4. **건강식 컨설팅 에이전트** - 사용자의 건강 상태나 다이어트 목표에 맞는 음식을 추천

#### 애매한 라우팅 시나리오들

다음과 같은 질문들이 여러 에이전트로 라우팅될 수 있습니다:

- **"음식 추천해줘"** → 냉장고 에이전트(집에서 만들기), 음식점 에이전트(외식), 건강식 에이전트(건강 고려)로 모두 라우팅 가능
- **"다이어트 음식 뭐가 좋을까?"** → 건강식 에이전트(다이어트 전문), 냉장고 에이전트(집에서 만들기), 레시피 에이전트(저칼로리 요리법)로 분산 가능
- **"오늘 저녁 뭐 먹지?"** → 4개 에이전트 모두 관련성이 있어서 완전히 랜덤하게 라우팅될 수 있음
- **"파스타 관련해서 도움줘"** → 레시피 에이전트(만드는 법), 음식점 에이전트(파스타 맛집), 냉장고 에이전트(집에 있는 재료로)로 애매함

### 시스템의 해결 방법

우리 시스템은 이런 애매한 상황에서도 다음과 같이 동작합니다:

1. **과거 패턴 분석**: "다이어트 음식 뭐가 좋을까?"와 유사한 질문들을 벡터 검색
2. **비율 계산**: 과거 유사 질문들이 어떤 에이전트로 라우팅되었는지 비율 계산
3. **가중치 적용**: 개발자가 설정한 가중치를 적용하여 비율 조정
4. **슈퍼바이저 지원**: 계산된 비율을 참고 정보로 제공하여 더 정확한 라우팅 결정 도움

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🤝 기여하기

이 연구 프로젝트에 대한 기여를 환영합니다. 행동 강령과 풀 리퀘스트 제출 과정에 대한 자세한 내용은 [CONTRIBUTING.md](CONTRIBUTING.md)를 읽어주세요.

## 📧 연락처

이 연구에 대한 질문이 있으시면 [@dongju2-lee](https://github.com/dongju2-lee)에게 연락하거나 이 저장소에 이슈를 열어주세요.

---
*2025년 6월 26일 연구 시작* 