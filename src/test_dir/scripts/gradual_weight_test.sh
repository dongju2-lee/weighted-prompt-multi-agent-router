#!/bin/bash

# 점진적 가중치 증가 테스트 스크립트
# 특정 에이전트의 가중치를 점진적으로 증가시켜 라우팅 패턴 변화 관찰

API_URL="http://localhost:8000/sports-agent-route"
STATS_URL="http://localhost:8000/routing-stats"
WEIGHTS_URL="http://localhost:8000/agent-weights"

# 테스트 설정
TEST_QUERY="운동하고 싶어"
TARGET_AGENT="야구_에이전트"  # 테스트할 대상 에이전트
TESTS_PER_PHASE=15  # 각 단계마다 실행할 테스트 수
OUTPUT_DIR="gradual_weight_test_$(date +%Y%m%d_%H%M%S)"

echo "📈 점진적 가중치 증가 테스트 시작"
echo "=========================================="
echo "테스트 목적: ${TARGET_AGENT} 가중치를 점진적으로 증가시켜 라우팅 패턴 변화 관찰"
echo "테스트 쿼리: '$TEST_QUERY'"
echo "대상 에이전트: $TARGET_AGENT"
echo "각 단계 테스트 수: $TESTS_PER_PHASE"
echo "결과 저장: $OUTPUT_DIR"
echo "=========================================="

# 결과 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 시드 데이터가 있는지 확인
echo "🔍 시드 데이터 상태 확인..."
total_requests=$(curl -s "$STATS_URL" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data['statistics']['total_requests'] if data['success'] else 0)
" 2>/dev/null)

if [ "$total_requests" -lt 4 ]; then
    echo "⚠️  시드 데이터가 부족합니다. seed_data_generator.sh를 먼저 실행해주세요."
    echo "💡 시드 데이터 자동 생성 중..."
    if [ -f "$(dirname "$0")/seed_data_generator.sh" ]; then
        bash "$(dirname "$0")/seed_data_generator.sh"
    else
        echo "❌ seed_data_generator.sh를 찾을 수 없습니다."
        exit 1
    fi
fi

# 가중치 단계별 설정
weight_steps=(1.0 1.5 2.0 3.0 5.0)
step_names=("baseline" "step1.5" "step2.0" "step3.0" "step5.0")

# 테스트 실행 함수
run_phase_test() {
    local phase_name="$1"
    local weight_value="$2"
    local phase_dir="$OUTPUT_DIR/$phase_name"
    
    mkdir -p "$phase_dir"
    
    echo ""
    echo "🧪 Phase: $phase_name (가중치: $weight_value)"
    echo "----------------------------------------"
    
    # 가중치 설정
    echo "⚙️  $TARGET_AGENT 가중치를 $weight_value 로 설정..."
    curl -s -X POST "$WEIGHTS_URL" \
         -H "Content-Type: application/json" \
         -d "{\"weights\": {\"$TARGET_AGENT\": $weight_value}}" > "$phase_dir/weight_change.json"
    
    if [ $? -ne 0 ]; then
        echo "❌ 가중치 설정 실패"
        return 1
    fi
    
    sleep 2  # 가중치 변경 반영 대기
    
    # 테스트 실행
    echo "🧪 테스트 실행 중... ($TESTS_PER_PHASE 회)"
    start_time=$(date +%s)
    
    for ((i=1; i<=TESTS_PER_PHASE; i++)); do
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
    echo "✅ Phase $phase_name 완료 (${duration}초)"
    
    # 결과 분석
    echo "📊 라우팅 분포:"
    grep -h "selected_agent" "$phase_dir/"*.json 2>/dev/null | \
    cut -d'"' -f4 | sort | uniq -c | sort -nr | \
    while read count agent; do
        percentage=$(( (count * 100) / TESTS_PER_PHASE ))
        printf "   %s: %d회 (%d%%)\n" "$agent" "$count" "$percentage"
        if [ "$agent" = "$TARGET_AGENT" ]; then
            echo "$weight_value,$count,$percentage" >> "$OUTPUT_DIR/target_agent_progression.csv"
        fi
    done
    
    # 통계 저장
    curl -s "$STATS_URL" > "$phase_dir/routing_stats.json"
    
    echo "💾 결과 저장: $phase_dir"
}

# CSV 헤더 생성
echo "weight,count,percentage" > "$OUTPUT_DIR/target_agent_progression.csv"

# 시작 시간 기록
overall_start=$(date +%s)

# 각 단계별 테스트 실행
for i in "${!weight_steps[@]}"; do
    weight="${weight_steps[$i]}"
    step_name="${step_names[$i]}"
    
    run_phase_test "$step_name" "$weight"
done

# 총 시간 계산
overall_end=$(date +%s)
total_duration=$((overall_end - overall_start))

# 최종 분석
echo ""
echo "📊 점진적 가중치 증가 테스트 결과 분석"
echo "=========================================="
echo "⏱️  총 실행 시간: ${total_duration}초"
echo ""
echo "🎯 $TARGET_AGENT 선택률 변화:"
echo "----------------------------------------"

if [ -f "$OUTPUT_DIR/target_agent_progression.csv" ]; then
    cat "$OUTPUT_DIR/target_agent_progression.csv" | while IFS=, read weight count percentage; do
        if [ "$weight" != "weight" ]; then  # 헤더 제외
            printf "   가중치 %s: %s회 (%s%%)\n" "$weight" "$count" "$percentage"
        fi
    done
fi

echo ""
echo "📁 상세 결과: $OUTPUT_DIR"
echo "📈 진행률 데이터: $OUTPUT_DIR/target_agent_progression.csv"
echo ""
echo "🎉 점진적 가중치 증가 테스트 완료!" 