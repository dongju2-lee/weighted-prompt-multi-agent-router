#!/bin/bash

# 순차적 에이전트 제어 테스트 스크립트
# 각 에이전트가 순차적으로 주도권을 가지도록 테스트

API_URL="http://localhost:8000/sports-agent-route"
STATS_URL="http://localhost:8000/routing-stats"
WEIGHTS_URL="http://localhost:8000/agent-weights"

# 테스트 설정
TEST_QUERY="운동하고 싶어"
TESTS_PER_AGENT=25  # 각 에이전트당 테스트 수
OUTPUT_DIR="sequential_control_test_$(date +%Y%m%d_%H%M%S)"

echo "🔄 순차적 에이전트 제어 테스트 시작"
echo "=========================================="
echo "테스트 목적: 각 에이전트가 순차적으로 주도권을 가지도록 제어"
echo "테스트 쿼리: '$TEST_QUERY'"
echo "각 에이전트당 테스트 수: $TESTS_PER_AGENT"
echo "결과 저장: $OUTPUT_DIR"
echo "=========================================="

# 결과 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 시드 데이터 확인
echo "🔍 시드 데이터 상태 확인..."
total_requests=$(curl -s "$STATS_URL" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data['statistics']['total_requests'] if data['success'] else 0)
" 2>/dev/null)

if [ "$total_requests" -lt 4 ]; then
    echo "💡 시드 데이터 자동 생성 중..."
    if [ -f "$(dirname "$0")/seed_data_generator.sh" ]; then
        bash "$(dirname "$0")/seed_data_generator.sh"
    else
        echo "❌ seed_data_generator.sh를 찾을 수 없습니다."
        exit 1
    fi
fi

# 에이전트 리스트 및 이모지
agents=("축구_에이전트" "농구_에이전트" "야구_에이전트" "테니스_에이전트")
emojis=("⚽" "🏀" "⚾" "🎾")
agent_names=("Soccer" "Basketball" "Baseball" "Tennis")

# 순차 제어 함수
control_agent() {
    local agent="$1"
    local emoji="$2"
    local agent_name="$3"
    local phase_dir="$OUTPUT_DIR/control_$agent"
    
    mkdir -p "$phase_dir"
    
    echo ""
    echo "$emoji $agent_name 에이전트 제어 단계"
    echo "----------------------------------------"
    
    # 해당 에이전트만 높은 가중치, 나머지는 낮게
    weight_json='{"weights": {"'$agent'": 8.0'
    for other_agent in "${agents[@]}"; do
        if [ "$other_agent" != "$agent" ]; then
            weight_json+=', "'$other_agent'": 0.5'
        fi
    done
    weight_json+='}}'
    
    echo "⚙️  가중치 설정: $agent = 8.0, 나머지 = 0.5"
    curl -s -X POST "$WEIGHTS_URL" \
         -H "Content-Type: application/json" \
         -d "$weight_json" > "$phase_dir/weight_change.json"
    
    if [ $? -ne 0 ]; then
        echo "❌ 가중치 설정 실패"
        return 1
    fi
    
    sleep 2  # 가중치 변경 반영 대기
    
    # 테스트 실행
    echo "🧪 테스트 실행 중... ($TESTS_PER_AGENT 회)"
    start_time=$(date +%s)
    
    for ((i=1; i<=TESTS_PER_AGENT; i++)); do
        result_file="$phase_dir/test_${i}.json"
        
        curl -s -X POST "$API_URL" \
             -H "Content-Type: application/json" \
             -d "{\"query\": \"$TEST_QUERY\"}" \
             > "$result_file" 2>/dev/null
        
        if [ $((i % 5)) -eq 0 ]; then
            echo -n "."
        fi
    done
    echo ""
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    echo "✅ $agent_name 제어 완료 (${duration}초)"
    
    # 결과 분석
    echo "📊 라우팅 분포:"
    local target_count=0
    local total_count=0
    
    grep -h "selected_agent" "$phase_dir/"*.json 2>/dev/null | \
    cut -d'"' -f4 | sort | uniq -c | sort -nr | \
    while read count selected_agent; do
        percentage=$(( (count * 100) / TESTS_PER_AGENT ))
        printf "   %s: %d회 (%d%%)\n" "$selected_agent" "$count" "$percentage"
        
        if [ "$selected_agent" = "$agent" ]; then
            target_count=$count
        fi
        total_count=$((total_count + count))
    done
    
    # 제어 효과 계산
    if [ $total_count -gt 0 ]; then
        control_effectiveness=$(( (target_count * 100) / total_count ))
        echo "🎯 제어 효과: $control_effectiveness% ($target_count/$total_count)"
        echo "$agent,$control_effectiveness" >> "$OUTPUT_DIR/control_effectiveness.csv"
    fi
    
    # 통계 저장
    curl -s "$STATS_URL" > "$phase_dir/routing_stats.json"
    
    echo "💾 결과 저장: $phase_dir"
}

# CSV 헤더 생성
echo "agent,effectiveness_percentage" > "$OUTPUT_DIR/control_effectiveness.csv"

# 시작 시간 기록
overall_start=$(date +%s)

# 각 에이전트 순차적으로 제어
for i in "${!agents[@]}"; do
    agent="${agents[$i]}"
    emoji="${emojis[$i]}"
    agent_name="${agent_names[$i]}"
    
    control_agent "$agent" "$emoji" "$agent_name"
    
    # 단계 간 잠깐 대기
    if [ $i -lt $((${#agents[@]} - 1)) ]; then
        echo ""
        echo "⏸️  다음 단계 준비 중... (3초 대기)"
        sleep 3
    fi
done

# 최종 균형 상태로 복원
echo ""
echo "🔧 최종 균형 상태로 복원..."
curl -s -X POST "$WEIGHTS_URL" \
     -H "Content-Type: application/json" \
     -d '{"weights": {"축구_에이전트": 1.0, "농구_에이전트": 1.0, "야구_에이전트": 1.0, "테니스_에이전트": 1.0}}' > "$OUTPUT_DIR/final_balance.json"

# 총 시간 계산
overall_end=$(date +%s)
total_duration=$((overall_end - overall_start))

# 최종 분석
echo ""
echo "📊 순차적 에이전트 제어 테스트 결과 분석"
echo "=========================================="
echo "⏱️  총 실행 시간: ${total_duration}초"
echo ""

echo "🎯 각 에이전트 제어 효과:"
echo "----------------------------------------"
if [ -f "$OUTPUT_DIR/control_effectiveness.csv" ]; then
    cat "$OUTPUT_DIR/control_effectiveness.csv" | while IFS=, read agent effectiveness; do
        if [ "$agent" != "agent" ]; then  # 헤더 제외
            printf "   %s: %s%% 제어 성공\n" "$agent" "$effectiveness"
        fi
    done
fi

echo ""
echo "📁 상세 결과: $OUTPUT_DIR"
echo "📈 제어 효과 데이터: $OUTPUT_DIR/control_effectiveness.csv"
echo ""
echo "💡 분석 포인트:"
echo "   • 각 에이전트가 주도권을 가질 때의 제어 효과"
echo "   • 가중치 변경을 통한 즉시적 라우팅 전환"
echo "   • 순차적 제어를 통한 시스템 반응성 확인"
echo ""
echo "🎉 순차적 에이전트 제어 테스트 완료!" 