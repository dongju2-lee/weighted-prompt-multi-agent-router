#!/bin/bash

# 운동 추천 시스템 멀티프로세스 테스트 스크립트
# 500번 테스트를 동시에 실행하여 라우팅 분석

API_URL="http://localhost:8000/sports-agent-route"
TEST_QUERY="운동하구 싶다"
TOTAL_TESTS=10
CONCURRENT_JOBS=5  # 동시 실행할 프로세스 수
OUTPUT_DIR="test_results_$(date +%Y%m%d_%H%M%S)"

echo "🏃 운동 추천 시스템 멀티프로세스 테스트 시작"
echo "========================================"
echo "테스트 횟수: $TOTAL_TESTS"
echo "동시 프로세스: $CONCURRENT_JOBS"
echo "테스트 질문: '$TEST_QUERY'"
echo "결과 저장: $OUTPUT_DIR"
echo "========================================"

# 결과 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 단일 테스트 함수
run_single_test() {
    local test_id=$1
    local result_file="$OUTPUT_DIR/test_${test_id}.json"
    
    # curl 실행 및 결과 저장
    curl -s -X POST "$API_URL" \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"$TEST_QUERY\"}" \
         > "$result_file" 2>/dev/null
    
    # 성공 여부 확인
    if [ $? -eq 0 ] && [ -s "$result_file" ]; then
        echo "✅ Test $test_id completed"
    else
        echo "❌ Test $test_id failed"
        echo "{\"error\": \"request_failed\", \"test_id\": $test_id}" > "$result_file"
    fi
}

# export 함수 (병렬 실행을 위해)
export -f run_single_test
export API_URL TEST_QUERY OUTPUT_DIR

echo "🚀 테스트 실행 중..."
start_time=$(date +%s)

# GNU parallel이 있으면 사용, 없으면 xargs 사용
if command -v parallel >/dev/null 2>&1; then
    echo "Using GNU parallel for faster execution..."
    seq 1 $TOTAL_TESTS | parallel -j $CONCURRENT_JOBS run_single_test {}
else
    echo "Using xargs for parallel execution..."
    seq 1 $TOTAL_TESTS | xargs -n 1 -P $CONCURRENT_JOBS -I {} bash -c 'run_single_test {}'
fi

end_time=$(date +%s)
execution_time=$((end_time - start_time))

echo "⏱️  실행 시간: ${execution_time}초"
echo "📊 결과 분석 시작..."

# Python 분석 스크립트 호출 (같은 디렉토리에서)
python3 "$(dirname "$0")/analyze_results.py" "$OUTPUT_DIR" "$TEST_QUERY" "$TOTAL_TESTS" "$execution_time"

echo "🎉 테스트 완료! 결과는 $OUTPUT_DIR 디렉토리에 저장되었습니다." 