#!/bin/bash

# 시드 데이터 생성 스크립트
# 모든 에이전트가 최소 1번씩 선택되도록 강제로 시드 데이터 생성
# 목적: 0 × 가중치 = 0 문제 해결

API_URL="http://localhost:8000/sports-agent-route"
STATS_URL="http://localhost:8000/routing-stats"
WEIGHTS_URL="http://localhost:8000/agent-weights"

echo "🌱 시드 데이터 생성 시작"
echo "=========================================="
echo "목적: 모든 에이전트가 최소 1번씩 선택되도록 강제 시드 데이터 생성"
echo "쿼리: '운동하고 싶어' (동일한 쿼리로만 테스트)"
echo "방법: 극단적 가중치 조작으로 각 에이전트 강제 선택"
echo "=========================================="

# 라우팅 히스토리 초기화
echo "🔄 라우팅 히스토리 초기화..."
curl -s -X DELETE http://localhost:8000/routing-history > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ 히스토리 초기화 완료"
else
    echo "❌ 히스토리 초기화 실패"
    exit 1
fi

# 각 에이전트 강제 선택
agents=("축구_에이전트" "농구_에이전트" "야구_에이전트" "테니스_에이전트")

for i in "${!agents[@]}"; do
    agent="${agents[$i]}"
    step=$((i + 1))
    
    echo ""
    echo "🎯 Step $step: $agent 강제 선택"
    
    # 해당 에이전트만 극도로 높은 가중치 설정
    weight_json='{"weights": {"'$agent'": 10.0'
    
    # 나머지 에이전트들은 0.01로 설정
    for other_agent in "${agents[@]}"; do
        if [ "$other_agent" != "$agent" ]; then
            weight_json+=', "'$other_agent'": 0.01'
        fi
    done
    weight_json+='}}'
    
    # 가중치 설정
    curl -s -X POST "$WEIGHTS_URL" \
         -H "Content-Type: application/json" \
         -d "$weight_json" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "   ⚙️  가중치 설정 완료: $agent = 10.0"
    else
        echo "   ❌ 가중치 설정 실패"
        continue
    fi
    
    # 테스트 실행
    result=$(curl -s -X POST "$API_URL" \
                  -H "Content-Type: application/json" \
                  -d '{"query": "운동하고 싶어"}' | \
                  grep -o '"selected_agent":"[^"]*"' | \
                  cut -d'"' -f4)
    
    if [ "$result" = "$agent" ]; then
        echo "   ✅ 성공: $agent 선택됨"
    else
        echo "   ❌ 실패: $result 선택됨 (예상: $agent)"
    fi
    
    sleep 1  # API 호출 간격
done

# 가중치 정상화
echo ""
echo "🔧 가중치 정상화 (모두 1.0으로 설정)..."
curl -s -X POST "$WEIGHTS_URL" \
     -H "Content-Type: application/json" \
     -d '{"weights": {"축구_에이전트": 1.0, "농구_에이전트": 1.0, "야구_에이전트": 1.0, "테니스_에이전트": 1.0}}' > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ 가중치 정상화 완료"
else
    echo "❌ 가중치 정상화 실패"
fi

# 최종 통계 확인
echo ""
echo "📊 시드 데이터 생성 결과:"
echo "----------------------------------------"
curl -s "$STATS_URL" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data['success']:
    stats = data['statistics']
    print(f'총 요청 수: {stats[\"total_requests\"]}')
    for agent, info in stats['agents'].items():
        print(f'   {agent}: {info[\"count\"]}회 ({info[\"percentage\"]}%)')
else:
    print('통계 조회 실패')
"

echo ""
echo "🎉 시드 데이터 생성 완료!"
echo "📝 이제 모든 에이전트가 최소 1번씩 선택되어 가중치 변경 테스트가 가능합니다." 