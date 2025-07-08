#!/bin/bash

# 경쟁 상황 테스트 스크립트
# 두 개 이상의 에이전트 가중치를 비슷하게 높여서 경쟁 상황 테스트

API_URL="http://localhost:8000/sports-agent-route"
STATS_URL="http://localhost:8000/routing-stats"
WEIGHTS_URL="http://localhost:8000/agent-weights"

# 테스트 설정
TEST_QUERY="운동하고 싶어"
TESTS_PER_COMPETITION=30
OUTPUT_DIR="competition_test_$(date +%Y%m%d_%H%M%S)"

echo "⚔️  경쟁 상황 테스트 시작"
echo "=========================================="
echo "테스트 목적: 여러 에이전트 간 가중치 경쟁 상황에서의 라우팅 분배"
echo "테스트 쿼리: '$TEST_QUERY'"
echo "각 경쟁 시나리오당 테스트 수: $TESTS_PER_COMPETITION"
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

# 경쟁 시나리오 실행 함수
run_competition() {
    local scenario_name="$1"
    local scenario_description="$2"
    local weight_config="$3"
    local scenario_dir="$OUTPUT_DIR/$scenario_name"
    
    mkdir -p "$scenario_dir"
    
    echo ""
    echo "🥊 경쟁 시나리오: $scenario_name"
    echo "📝 $scenario_description"
    echo "----------------------------------------"
    
    # 가중치 설정
    echo "⚙️  가중치 설정: $weight_config"
    curl -s -X POST "$WEIGHTS_URL" \
         -H "Content-Type: application/json" \
         -d "$weight_config" > "$scenario_dir/weight_change.json"
    
    if [ $? -ne 0 ]; then
        echo "❌ 가중치 설정 실패"
        return 1
    fi
    
    sleep 2  # 가중치 변경 반영 대기
    
    # 테스트 실행
    echo "🧪 테스트 실행 중... ($TESTS_PER_COMPETITION 회)"
    start_time=$(date +%s)
    
    for ((i=1; i<=TESTS_PER_COMPETITION; i++)); do
        result_file="$scenario_dir/test_${i}.json"
        
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
    echo "✅ $scenario_name 완료 (${duration}초)"
    
    # 결과 분석
    echo "📊 경쟁 결과 분포:"
    grep -h "selected_agent" "$scenario_dir/"*.json 2>/dev/null | \
    cut -d'"' -f4 | sort | uniq -c | sort -nr | \
    while read count agent; do
        percentage=$(( (count * 100) / TESTS_PER_COMPETITION ))
        printf "   %s: %d회 (%d%%)\n" "$agent" "$count" "$percentage"
    done
    
    # 경쟁 지수 계산 (상위 2개 에이전트 간 차이)
    top_two=$(grep -h "selected_agent" "$scenario_dir/"*.json 2>/dev/null | \
              cut -d'"' -f4 | sort | uniq -c | sort -nr | head -2)
    
    if [ $(echo "$top_two" | wc -l) -eq 2 ]; then
        first_count=$(echo "$top_two" | head -1 | awk '{print $1}')
        second_count=$(echo "$top_two" | tail -1 | awk '{print $1}')
        competition_index=$(( 100 - ((first_count - second_count) * 100 / TESTS_PER_COMPETITION) ))
        echo "🏆 경쟁 지수: ${competition_index}% (100%에 가까울수록 치열한 경쟁)"
        echo "$scenario_name,$competition_index" >> "$OUTPUT_DIR/competition_index.csv"
    fi
    
    # 통계 저장
    curl -s "$STATS_URL" > "$scenario_dir/routing_stats.json"
    
    echo "💾 결과 저장: $scenario_dir"
}

# CSV 헤더 생성
echo "scenario,competition_index" > "$OUTPUT_DIR/competition_index.csv"

# 시작 시간 기록
overall_start=$(date +%s)

# 경쟁 시나리오 1: 축구 vs 농구 (동일 가중치)
run_competition "scenario1_soccer_vs_basketball_equal" \
    "축구 vs 농구 동일 가중치 경쟁 (각 3.0)" \
    '{"weights": {"축구_에이전트": 3.0, "농구_에이전트": 3.0, "야구_에이전트": 1.0, "테니스_에이전트": 1.0}}'

# 경쟁 시나리오 2: 축구 vs 농구 (미세한 차이)
run_competition "scenario2_soccer_vs_basketball_slight" \
    "축구 vs 농구 미세한 차이 (3.0 vs 2.8)" \
    '{"weights": {"축구_에이전트": 3.0, "농구_에이전트": 2.8, "야구_에이전트": 1.0, "테니스_에이전트": 1.0}}'

# 경쟁 시나리오 3: 3자 경쟁
run_competition "scenario3_three_way_competition" \
    "축구 vs 농구 vs 야구 3자 경쟁 (각 2.5)" \
    '{"weights": {"축구_에이전트": 2.5, "농구_에이전트": 2.5, "야구_에이전트": 2.5, "테니스_에이전트": 0.5}}'

# 경쟁 시나리오 4: 4자 균등 경쟁
run_competition "scenario4_four_way_equal" \
    "4개 에이전트 균등 경쟁 (모두 2.0)" \
    '{"weights": {"축구_에이전트": 2.0, "농구_에이전트": 2.0, "야구_에이전트": 2.0, "테니스_에이전트": 2.0}}'

# 경쟁 시나리오 5: 야구 vs 테니스 (높은 가중치)
run_competition "scenario5_baseball_vs_tennis_high" \
    "야구 vs 테니스 고가중치 경쟁 (각 5.0)" \
    '{"weights": {"축구_에이전트": 0.5, "농구_에이전트": 0.5, "야구_에이전트": 5.0, "테니스_에이전트": 5.0}}'

# 경쟁 시나리오 6: 불균등 경쟁 (계단식)
run_competition "scenario6_stepwise_competition" \
    "계단식 가중치 경쟁 (4.0, 3.0, 2.0, 1.0)" \
    '{"weights": {"축구_에이전트": 4.0, "농구_에이전트": 3.0, "야구_에이전트": 2.0, "테니스_에이전트": 1.0}}'

# 총 시간 계산
overall_end=$(date +%s)
total_duration=$((overall_end - overall_start))

# 최종 분석
echo ""
echo "📊 경쟁 상황 테스트 결과 분석"
echo "=========================================="
echo "⏱️  총 실행 시간: ${total_duration}초"
echo ""

echo "🏆 시나리오별 경쟁 지수:"
echo "----------------------------------------"
if [ -f "$OUTPUT_DIR/competition_index.csv" ]; then
    cat "$OUTPUT_DIR/competition_index.csv" | while IFS=, read scenario index; do
        if [ "$scenario" != "scenario" ]; then  # 헤더 제외
            case $scenario in
                *equal*) desc="동일 가중치" ;;
                *slight*) desc="미세한 차이" ;;
                *three*) desc="3자 경쟁" ;;
                *four*) desc="4자 균등" ;;
                *high*) desc="고가중치" ;;
                *stepwise*) desc="계단식" ;;
                *) desc="기타" ;;
            esac
            printf "   %s (%s): %s%%\n" "$desc" "$scenario" "$index"
        fi
    done
fi

echo ""
echo "📁 상세 결과: $OUTPUT_DIR"
echo "📈 경쟁 지수 데이터: $OUTPUT_DIR/competition_index.csv"
echo ""
echo "💡 분석 포인트:"
echo "   • 동일 가중치에서의 확률적 분배"
echo "   • 미세한 가중치 차이의 영향"
echo "   • 다자간 경쟁에서의 균형점"
echo "   • 고가중치 vs 저가중치 그룹 간 경쟁"
echo ""
echo "🎉 경쟁 상황 테스트 완료!" 