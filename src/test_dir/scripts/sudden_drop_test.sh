#!/bin/bash

# 급격한 가중치 감소 테스트 스크립트
# 주도권을 가진 에이전트의 가중치를 급격히 낮춰서 라우팅 전환 테스트

API_URL="http://localhost:8000/sports-agent-route"
STATS_URL="http://localhost:8000/routing-stats"
WEIGHTS_URL="http://localhost:8000/agent-weights"

# 테스트 설정
TEST_QUERY="운동하고 싶어"
TESTS_PER_PHASE=20
OUTPUT_DIR="sudden_drop_test_$(date +%Y%m%d_%H%M%S)"

echo "💥 급격한 가중치 감소 테스트 시작"
echo "=========================================="
echo "테스트 목적: 주도권 에이전트의 가중치를 급격히 낮춰서 라우팅 전환 확인"
echo "테스트 쿼리: '$TEST_QUERY'"
echo "각 단계 테스트 수: $TESTS_PER_PHASE"
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

# 테스트 실행 함수
run_phase_test() {
    local phase_name="$1"
    local phase_description="$2"
    local weight_changes="$3"
    local phase_dir="$OUTPUT_DIR/$phase_name"
    
    mkdir -p "$phase_dir"
    
    echo ""
    echo "🧪 Phase: $phase_name"
    echo "📝 $phase_description"
    echo "----------------------------------------"
    
    # 가중치 변경
    if [ -n "$weight_changes" ]; then
        echo "⚙️  가중치 변경: $weight_changes"
        curl -s -X POST "$WEIGHTS_URL" \
             -H "Content-Type: application/json" \
             -d "$weight_changes" > "$phase_dir/weight_change.json"
        
        if [ $? -ne 0 ]; then
            echo "❌ 가중치 설정 실패"
            return 1
        fi
        
        sleep 2  # 가중치 변경 반영 대기
    fi
    
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
    done
    
    # 통계 저장
    curl -s "$STATS_URL" > "$phase_dir/routing_stats.json"
    
    echo "💾 결과 저장: $phase_dir"
}

# 시작 시간 기록
overall_start=$(date +%s)

# Phase 1: 특정 에이전트에게 주도권 부여
echo ""
echo "🎯 Phase 1: 농구 에이전트에게 주도권 부여"
run_phase_test "phase1_dominance" \
    "농구 에이전트 가중치를 5.0으로 높여서 주도권 확립" \
    '{"weights": {"농구_에이전트": 5.0, "축구_에이전트": 1.0, "야구_에이전트": 1.0, "테니스_에이전트": 1.0}}'

# Phase 2: 주도권 에이전트 급격히 감소
echo ""
echo "💥 Phase 2: 농구 에이전트 가중치 급격히 감소"
run_phase_test "phase2_sudden_drop" \
    "농구 에이전트 가중치를 0.1로 급격히 감소" \
    '{"weights": {"농구_에이전트": 0.1}}'

# Phase 3: 다른 에이전트 부스트
echo ""
echo "🚀 Phase 3: 축구 에이전트 부스트"
run_phase_test "phase3_alternative_boost" \
    "축구 에이전트 가중치를 5.0으로 부스트" \
    '{"weights": {"축구_에이전트": 5.0}}'

# Phase 4: 극단적 전환 테스트
echo ""
echo "⚡ Phase 4: 극단적 전환 (축구 → 테니스)"
run_phase_test "phase4_extreme_switch" \
    "축구 0.01, 테니스 10.0으로 극단적 전환" \
    '{"weights": {"축구_에이전트": 0.01, "테니스_에이전트": 10.0}}'

# 총 시간 계산
overall_end=$(date +%s)
total_duration=$((overall_end - overall_start))

# 최종 분석
echo ""
echo "📊 급격한 가중치 감소 테스트 결과 분석"
echo "=========================================="
echo "⏱️  총 실행 시간: ${total_duration}초"
echo ""

# 각 단계별 주도 에이전트 확인
echo "🔄 단계별 라우팅 전환 결과:"
echo "----------------------------------------"

phases=("phase1_dominance" "phase2_sudden_drop" "phase3_alternative_boost" "phase4_extreme_switch")
phase_descriptions=("농구 주도권 확립" "농구 급격 감소" "축구 부스트" "축구→테니스 전환")

for i in "${!phases[@]}"; do
    phase="${phases[$i]}"
    desc="${phase_descriptions[$i]}"
    
    if [ -d "$OUTPUT_DIR/$phase" ]; then
        echo "   $desc:"
        dominant_agent=$(grep -h "selected_agent" "$OUTPUT_DIR/$phase/"*.json 2>/dev/null | \
                        cut -d'"' -f4 | sort | uniq -c | sort -nr | head -1)
        echo "     $dominant_agent"
    fi
done

echo ""
echo "📁 상세 결과: $OUTPUT_DIR"
echo ""
echo "💡 분석 포인트:"
echo "   • Phase 1 → 2: 농구 주도권에서 급격 감소 후 다른 에이전트로 전환"
echo "   • Phase 2 → 3: 축구 부스트로 인한 주도권 이동"
echo "   • Phase 3 → 4: 극단적 가중치 조작으로 즉시 전환"
echo ""
echo "🎉 급격한 가중치 감소 테스트 완료!" 