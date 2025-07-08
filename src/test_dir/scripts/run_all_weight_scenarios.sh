#!/bin/bash

# 모든 가중치 테스트 시나리오 통합 실행 스크립트
# 모든 가중치 관련 테스트를 순차적으로 실행하고 종합 분석

SCRIPT_DIR="$(dirname "$0")"
OUTPUT_DIR="comprehensive_weight_test_$(date +%Y%m%d_%H%M%S)"
SUMMARY_FILE="$OUTPUT_DIR/test_summary.txt"

echo "🚀 종합 가중치 테스트 시나리오 실행"
echo "=========================================="
echo "실행 대상:"
echo "  1. 시드 데이터 생성"
echo "  2. 점진적 가중치 증가 테스트"
echo "  3. 급격한 가중치 감소 테스트"
echo "  4. 순차적 에이전트 제어 테스트"
echo "  5. 경쟁 상황 테스트"
echo "  6. 실시간 다중 가중치 변경 테스트"
echo "=========================================="
echo "종합 결과 저장: $OUTPUT_DIR"
echo "=========================================="

# 결과 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# API 서버 상태 확인
echo "🔍 API 서버 상태 확인..."
if ! curl -s http://localhost:8000/routing-stats > /dev/null; then
    echo "❌ API 서버가 실행되지 않았습니다!"
    echo "💡 다음 명령으로 서버를 시작하세요:"
    echo "   cd /Users/idongju/dev/weighted-prompt-multi-agent-router"
    echo "   python -m run_dir.run_api"
    exit 1
fi
echo "✅ API 서버 연결 확인"

# 시작 시간 기록
overall_start=$(date +%s)

# 테스트 실행 함수
run_test() {
    local test_name="$1"
    local script_file="$2"
    local description="$3"
    
    echo ""
    echo "🧪 [$test_name] $description"
    echo "==============================="
    
    if [ ! -f "$script_file" ]; then
        echo "❌ 테스트 스크립트를 찾을 수 없습니다: $script_file"
        echo "[$test_name] SKIPPED - 스크립트 없음" >> "$SUMMARY_FILE"
        return 1
    fi
    
    # 테스트 실행
    start_time=$(date +%s)
    echo "⏱️  시작 시간: $(date)"
    
    if bash "$script_file"; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo "✅ [$test_name] 완료 (${duration}초)"
        echo "[$test_name] SUCCESS - ${duration}초 소요" >> "$SUMMARY_FILE"
        
        # 결과 디렉토리가 생성되었다면 통합 결과로 복사
        newest_result=$(find . -maxdepth 1 -name "${test_name%_test}_test_*" -type d 2>/dev/null | sort | tail -1)
        if [ -n "$newest_result" ] && [ -d "$newest_result" ]; then
            cp -r "$newest_result" "$OUTPUT_DIR/"
            echo "📁 결과 복사: $newest_result → $OUTPUT_DIR/"
        fi
        
        return 0
    else
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo "❌ [$test_name] 실패 (${duration}초)"
        echo "[$test_name] FAILED - ${duration}초 후 실패" >> "$SUMMARY_FILE"
        return 1
    fi
}

# 요약 파일 초기화
echo "종합 가중치 테스트 실행 요약" > "$SUMMARY_FILE"
echo "실행 시간: $(date)" >> "$SUMMARY_FILE"
echo "========================================" >> "$SUMMARY_FILE"

# 테스트 카운터
total_tests=6
passed_tests=0
failed_tests=0

# 1. 시드 데이터 생성
run_test "seed_data_generator" \
    "$SCRIPT_DIR/seed_data_generator.sh" \
    "모든 에이전트가 최소 1번씩 선택되도록 시드 데이터 생성"
if [ $? -eq 0 ]; then ((passed_tests++)); else ((failed_tests++)); fi

echo ""
echo "⏸️  다음 테스트 준비 중... (5초 대기)"
sleep 5

# 2. 점진적 가중치 증가 테스트
run_test "gradual_weight" \
    "$SCRIPT_DIR/gradual_weight_test.sh" \
    "특정 에이전트의 가중치를 점진적으로 증가시켜 라우팅 패턴 변화 관찰"
if [ $? -eq 0 ]; then ((passed_tests++)); else ((failed_tests++)); fi

echo ""
echo "⏸️  다음 테스트 준비 중... (5초 대기)"
sleep 5

# 3. 급격한 가중치 감소 테스트
run_test "sudden_drop" \
    "$SCRIPT_DIR/sudden_drop_test.sh" \
    "주도권 에이전트의 가중치를 급격히 낮춰서 라우팅 전환 확인"
if [ $? -eq 0 ]; then ((passed_tests++)); else ((failed_tests++)); fi

echo ""
echo "⏸️  다음 테스트 준비 중... (5초 대기)"
sleep 5

# 4. 순차적 에이전트 제어 테스트
run_test "sequential_control" \
    "$SCRIPT_DIR/sequential_control_test.sh" \
    "각 에이전트가 순차적으로 주도권을 가지도록 제어"
if [ $? -eq 0 ]; then ((passed_tests++)); else ((failed_tests++)); fi

echo ""
echo "⏸️  다음 테스트 준비 중... (5초 대기)"
sleep 5

# 5. 경쟁 상황 테스트
run_test "competition" \
    "$SCRIPT_DIR/competition_test.sh" \
    "여러 에이전트 간 가중치 경쟁 상황에서의 라우팅 분배"
if [ $? -eq 0 ]; then ((passed_tests++)); else ((failed_tests++)); fi

echo ""
echo "⏸️  다음 테스트 준비 중... (5초 대기)"
sleep 5

# 6. 실시간 다중 가중치 변경 테스트
run_test "realtime_multi_change" \
    "$SCRIPT_DIR/realtime_multi_change_test.sh" \
    "실행 중 실시간 가중치 변경으로 라우팅 패턴 즉시 반영 확인"
if [ $? -eq 0 ]; then ((passed_tests++)); else ((failed_tests++)); fi

# 총 시간 계산
overall_end=$(date +%s)
total_duration=$((overall_end - overall_start))

# 최종 통계
echo "" >> "$SUMMARY_FILE"
echo "========================================" >> "$SUMMARY_FILE"
echo "최종 통계:" >> "$SUMMARY_FILE"
echo "  총 테스트: $total_tests" >> "$SUMMARY_FILE"
echo "  성공: $passed_tests" >> "$SUMMARY_FILE"
echo "  실패: $failed_tests" >> "$SUMMARY_FILE"
echo "  성공률: $(( (passed_tests * 100) / total_tests ))%" >> "$SUMMARY_FILE"
echo "  총 실행 시간: ${total_duration}초" >> "$SUMMARY_FILE"
echo "  종료 시간: $(date)" >> "$SUMMARY_FILE"

# 최종 결과 출력
echo ""
echo "🎯 종합 가중치 테스트 실행 완료!"
echo "========================================"
echo "📊 최종 통계:"
echo "   총 테스트: $total_tests"
echo "   ✅ 성공: $passed_tests"
echo "   ❌ 실패: $failed_tests"
echo "   📈 성공률: $(( (passed_tests * 100) / total_tests ))%"
echo "   ⏱️  총 실행 시간: ${total_duration}초 ($(( total_duration / 60 ))분 $(( total_duration % 60 ))초)"

if [ $failed_tests -eq 0 ]; then
    echo ""
    echo "🎉 모든 테스트가 성공적으로 완료되었습니다!"
else
    echo ""
    echo "⚠️  일부 테스트가 실패했습니다. 상세 내용을 확인해주세요."
fi

echo ""
echo "📁 종합 결과: $OUTPUT_DIR"
echo "📝 실행 요약: $SUMMARY_FILE"

# 결과 분석 스크립트가 있다면 실행
if [ -f "$SCRIPT_DIR/analyze_all_results.py" ]; then
    echo ""
    echo "📊 종합 결과 분석 실행 중..."
    python3 "$SCRIPT_DIR/analyze_all_results.py" "$OUTPUT_DIR"
fi

echo ""
echo "💡 개별 테스트 재실행 방법:"
echo "   bash $SCRIPT_DIR/seed_data_generator.sh"
echo "   bash $SCRIPT_DIR/gradual_weight_test.sh"
echo "   bash $SCRIPT_DIR/sudden_drop_test.sh"
echo "   bash $SCRIPT_DIR/sequential_control_test.sh"
echo "   bash $SCRIPT_DIR/competition_test.sh"
echo "   bash $SCRIPT_DIR/realtime_multi_change_test.sh" 