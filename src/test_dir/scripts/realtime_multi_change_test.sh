#!/bin/bash

# 실시간 다중 가중치 변경 테스트 스크립트
# 테스트 실행 중간에 여러 번 가중치를 실시간으로 변경

API_URL="http://localhost:8000/sports-agent-route"
STATS_URL="http://localhost:8000/routing-stats"
WEIGHTS_URL="http://localhost:8000/agent-weights"

# 테스트 설정
TEST_QUERY="운동하고 싶어"
TOTAL_TESTS=100  # 총 테스트 수
CHANGE_INTERVAL=10  # 가중치 변경 간격 (테스트 수 기준)
OUTPUT_DIR="realtime_multi_change_test_$(date +%Y%m%d_%H%M%S)"

echo "🔄 실시간 다중 가중치 변경 테스트 시작"
echo "=========================================="
echo "테스트 목적: 실행 중 실시간 가중치 변경으로 라우팅 패턴 즉시 반영 확인"
echo "테스트 쿼리: '$TEST_QUERY'"
echo "총 테스트 수: $TOTAL_TESTS"
echo "가중치 변경 간격: 매 $CHANGE_INTERVAL 테스트마다"
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

# 가중치 변경 시나리오 정의
weight_scenarios=(
    '{"weights": {"축구_에이전트": 5.0, "농구_에이전트": 1.0, "야구_에이전트": 1.0, "테니스_에이전트": 1.0}}'  # 축구 우세
    '{"weights": {"축구_에이전트": 1.0, "농구_에이전트": 5.0, "야구_에이전트": 1.0, "테니스_에이전트": 1.0}}'  # 농구 우세
    '{"weights": {"축구_에이전트": 1.0, "농구_에이전트": 1.0, "야구_에이전트": 5.0, "테니스_에이전트": 1.0}}'  # 야구 우세
    '{"weights": {"축구_에이전트": 1.0, "농구_에이전트": 1.0, "야구_에이전트": 1.0, "테니스_에이전트": 5.0}}'  # 테니스 우세
    '{"weights": {"축구_에이전트": 3.0, "농구_에이전트": 3.0, "야구_에이전트": 1.0, "테니스_에이전트": 1.0}}'  # 축구+농구 경쟁
    '{"weights": {"축구_에이전트": 1.0, "농구_에이전트": 1.0, "야구_에이전트": 3.0, "테니스_에이전트": 3.0}}'  # 야구+테니스 경쟁
    '{"weights": {"축구_에이전트": 2.0, "농구_에이전트": 2.0, "야구_에이전트": 2.0, "테니스_에이전트": 2.0}}'  # 균등
    '{"weights": {"축구_에이전트": 0.1, "농구_에이전트": 0.1, "야구_에이전트": 0.1, "테니스_에이전트": 10.0}}'  # 테니스 극우세
    '{"weights": {"축구_에이전트": 4.0, "농구_에이전트": 3.0, "야구_에이전트": 2.0, "테니스_에이전트": 1.0}}'  # 계단식
    '{"weights": {"축구_에이전트": 1.0, "농구_에이전트": 2.0, "야구_에이전트": 3.0, "테니스_에이전트": 4.0}}'  # 역계단식
)

scenario_names=(
    "축구_우세"
    "농구_우세"
    "야구_우세"
    "테니스_우세"
    "축구농구_경쟁"
    "야구테니스_경쟁"
    "4자_균등"
    "테니스_극우세"
    "계단식_하향"
    "계단식_상향"
)

# 테스트 결과 추적을 위한 CSV 초기화
echo "test_number,change_point,scenario_name,selected_agent,timestamp" > "$OUTPUT_DIR/realtime_results.csv"
echo "change_point,scenario_name,weight_config" > "$OUTPUT_DIR/weight_changes.csv"

# 시작 시간 기록
overall_start=$(date +%s)
current_scenario=0

echo ""
echo "🧪 실시간 테스트 시작..."
echo "----------------------------------------"

# 초기 균등 상태로 시작
echo "⚙️  초기 균등 가중치 설정..."
curl -s -X POST "$WEIGHTS_URL" \
     -H "Content-Type: application/json" \
     -d '{"weights": {"축구_에이전트": 1.0, "농구_에이전트": 1.0, "야구_에이전트": 1.0, "테니스_에이전트": 1.0}}' > /dev/null

for ((test=1; test<=TOTAL_TESTS; test++)); do
    # 가중치 변경 시점 확인
    if [ $((test % CHANGE_INTERVAL)) -eq 1 ] && [ $test -gt 1 ]; then
        scenario_index=$((current_scenario % ${#weight_scenarios[@]}))
        weight_config="${weight_scenarios[$scenario_index]}"
        scenario_name="${scenario_names[$scenario_index]}"
        
        echo ""
        echo "🔄 Test $test: 가중치 변경 → $scenario_name"
        echo "   설정: $weight_config"
        
        # 가중치 변경
        curl -s -X POST "$WEIGHTS_URL" \
             -H "Content-Type: application/json" \
             -d "$weight_config" > /dev/null
        
        # 변경 기록
        echo "$test,$scenario_name,$weight_config" >> "$OUTPUT_DIR/weight_changes.csv"
        
        current_scenario=$((current_scenario + 1))
        sleep 1  # 가중치 반영 대기
    fi
    
    # 테스트 실행
    timestamp=$(date +%s)
    result=$(curl -s -X POST "$API_URL" \
                  -H "Content-Type: application/json" \
                  -d "{\"query\": \"$TEST_QUERY\"}" | \
                  grep -o '"selected_agent":"[^"]*"' | \
                  cut -d'"' -f4)
    
    # 결과 기록
    change_point="no"
    if [ $((test % CHANGE_INTERVAL)) -eq 1 ] && [ $test -gt 1 ]; then
        change_point="yes"
    fi
    
    scenario_name="${scenario_names[$((((test-1)/CHANGE_INTERVAL) % ${#scenario_names[@]}))]}"
    echo "$test,$change_point,$scenario_name,$result,$timestamp" >> "$OUTPUT_DIR/realtime_results.csv"
    
    # 진행률 표시
    if [ $((test % 10)) -eq 0 ]; then
        progress=$((test * 100 / TOTAL_TESTS))
        echo -n "[$progress%] "
    elif [ $((test % 5)) -eq 0 ]; then
        echo -n "."
    fi
done

echo ""
echo "✅ 실시간 테스트 완료!"

# 총 시간 계산
overall_end=$(date +%s)
total_duration=$((overall_end - overall_start))

# 결과 분석
echo ""
echo "📊 실시간 다중 가중치 변경 테스트 결과 분석"
echo "=========================================="
echo "⏱️  총 실행 시간: ${total_duration}초"
echo "🔄 총 가중치 변경 횟수: $((TOTAL_TESTS / CHANGE_INTERVAL))"
echo ""

# 전체 분포 분석
echo "📈 전체 에이전트 선택 분포:"
echo "----------------------------------------"
tail -n +2 "$OUTPUT_DIR/realtime_results.csv" | cut -d',' -f4 | sort | uniq -c | sort -nr | \
while read count agent; do
    percentage=$(( (count * 100) / TOTAL_TESTS ))
    printf "   %s: %d회 (%d%%)\n" "$agent" "$count" "$percentage"
done

# 시나리오별 반응성 분석
echo ""
echo "⚡ 가중치 변경 시점별 반응성 분석:"
echo "----------------------------------------"

python3 << 'EOF'
import csv
import sys

# CSV 파일 읽기
results = []
with open(sys.argv[1] + '/realtime_results.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        results.append(row)

# 가중치 변경 시점 분석
change_points = [r for r in results if r['change_point'] == 'yes']
print(f"총 {len(change_points)}개의 가중치 변경 시점 분석:")
print()

for i, change in enumerate(change_points):
    test_num = int(change['test_number'])
    scenario = change['scenario_name']
    
    # 변경 후 3개 테스트의 결과 확인
    next_tests = [r for r in results if int(r['test_number']) >= test_num and int(r['test_number']) < test_num + 3]
    
    if next_tests:
        agents = [t['selected_agent'] for t in next_tests]
        print(f"   변경 {i+1}: {scenario}")
        print(f"      즉시 반응: {' → '.join(agents)}")
        
        # 주도 에이전트 확인
        from collections import Counter
        counter = Counter(agents)
        dominant = counter.most_common(1)[0] if agents else ('없음', 0)
        print(f"      주도 에이전트: {dominant[0]} ({dominant[1]}/3)")
        print()

EOF "$OUTPUT_DIR"

echo ""
echo "📁 상세 결과: $OUTPUT_DIR"
echo "📋 실시간 결과: $OUTPUT_DIR/realtime_results.csv"
echo "🔄 가중치 변경 기록: $OUTPUT_DIR/weight_changes.csv"
echo ""
echo "💡 분석 포인트:"
echo "   • 가중치 변경의 즉시 반영 여부"
echo "   • 시나리오별 라우팅 패턴 변화"
echo "   • 실시간 제어의 효과성"
echo "   • 연속적 변경에 대한 시스템 안정성"
echo ""
echo "🎉 실시간 다중 가중치 변경 테스트 완료!" 