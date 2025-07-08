#!/usr/bin/env python3
"""
테스트 결과 자동 분석 스크립트
- 명령행 인자로 날짜시간을 받아서 해당 테스트 결과 분석
- 분석 결과를 test_result_anal 디렉토리에 txt 파일로 저장
"""

import json
import os
import sys
import glob
from collections import Counter, defaultdict
from datetime import datetime
import statistics

class TestResultAnalyzer:
    def __init__(self, datetime_str):
        self.datetime_str = datetime_str
        self.results = []
        self.agent_counts = Counter()
        self.query_patterns = defaultdict(list)
        self.weight_effects = defaultdict(list)
        self.routing_info = []
        self.analysis_output = []  # 분석 결과를 저장할 리스트
        
    def log(self, message):
        """분석 결과를 콘솔과 출력 리스트에 동시에 저장"""
        print(message)
        self.analysis_output.append(message)
        
    def find_test_directory(self):
        """지정된 날짜시간의 테스트 결과 디렉토리 찾기"""
        target_dir = f"test_results_{self.datetime_str}"
        
        if not os.path.exists(target_dir):
            self.log(f"❌ 테스트 결과 디렉토리를 찾을 수 없습니다: {target_dir}")
            return None
            
        self.log(f"📁 분석 대상 디렉토리: {target_dir}")
        return target_dir
    
    def load_test_results(self, directory):
        """테스트 결과 파일들을 로드"""
        json_files = glob.glob(os.path.join(directory, "test_*.json"))
        
        if not json_files:
            self.log(f"❌ {directory}에서 테스트 결과 파일을 찾을 수 없습니다.")
            return False
            
        self.log(f"📊 {len(json_files)}개의 테스트 결과 파일을 로드 중...")
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('success', False):
                        self.results.append(data)
                        self.agent_counts[data['selected_agent']] += 1
                        self.query_patterns[data['user_query']].append(data['selected_agent'])
                        
                        # 라우팅 정보 저장
                        if 'routing_info' in data:
                            self.routing_info.append(data['routing_info'])
                            
                        # 가중치 효과 분석
                        if 'routing_info' in data and 'agent_weights' in data['routing_info']:
                            weights = data['routing_info']['agent_weights']
                            selected = data['selected_agent']
                            if selected in weights:
                                self.weight_effects[selected].append(weights[selected])
                                
            except (json.JSONDecodeError, KeyError) as e:
                self.log(f"⚠️  파일 로드 오류 ({file_path}): {e}")
                continue
                
        self.log(f"✅ {len(self.results)}개의 유효한 테스트 결과를 로드했습니다.")
        return len(self.results) > 0
    
    def analyze_agent_distribution(self):
        """에이전트 분포 분석"""
        self.log("\n" + "="*60)
        self.log("🎯 에이전트 선택 분포 분석")
        self.log("="*60)
        
        total_tests = len(self.results)
        
        self.log(f"총 테스트 수: {total_tests}")
        self.log("\n에이전트별 선택 횟수:")
        self.log("-" * 40)
        
        for agent, count in self.agent_counts.most_common():
            percentage = (count / total_tests) * 100
            bar = "█" * int(percentage / 2)  # 50% = 25개 블록
            self.log(f"{agent:<20} {count:>3}회 ({percentage:>5.1f}%) {bar}")
            
        # 균등 분포와의 차이 분석
        expected_per_agent = total_tests / len(self.agent_counts) if len(self.agent_counts) > 0 else 0
        self.log(f"\n균등 분포 기댓값: {expected_per_agent:.1f}회 per 에이전트")
        
        self.log("\n균등 분포 대비 편차:")
        self.log("-" * 40)
        for agent, count in self.agent_counts.items():
            deviation = count - expected_per_agent
            deviation_pct = (deviation / expected_per_agent) * 100 if expected_per_agent > 0 else 0
            status = "📈" if deviation > 0 else "📉" if deviation < 0 else "➡️"
            self.log(f"{agent:<20} {status} {deviation:+6.1f}회 ({deviation_pct:+5.1f}%)")
    
    def analyze_weight_effects(self):
        """가중치 효과 분석"""
        self.log("\n" + "="*60)
        self.log("⚖️  가중치 효과 분석")
        self.log("="*60)
        
        if not self.weight_effects:
            self.log("가중치 데이터가 없습니다.")
            return
            
        for agent, weights in self.weight_effects.items():
            if len(weights) > 1:
                avg_weight = statistics.mean(weights)
                min_weight = min(weights)
                max_weight = max(weights)
                
                self.log(f"\n{agent}:")
                self.log(f"  평균 가중치: {avg_weight:.2f}")
                self.log(f"  가중치 범위: {min_weight:.2f} ~ {max_weight:.2f}")
                self.log(f"  선택된 횟수: {len(weights)}회")
    
    def analyze_routing_patterns(self):
        """라우팅 패턴 분석"""
        self.log("\n" + "="*60)
        self.log("🔄 라우팅 패턴 분석")
        self.log("="*60)
        
        if not self.routing_info:
            self.log("라우팅 정보가 없습니다.")
            return
            
        # 정규화된 비율 분석
        all_ratios = defaultdict(list)
        
        for info in self.routing_info:
            if 'normalized_ratios' in info:
                for agent, ratio in info['normalized_ratios'].items():
                    all_ratios[agent].append(ratio)
        
        self.log("에이전트별 평균 정규화 비율:")
        self.log("-" * 40)
        
        for agent, ratios in all_ratios.items():
            avg_ratio = statistics.mean(ratios)
            min_ratio = min(ratios)
            max_ratio = max(ratios)
            
            self.log(f"{agent:<20} {avg_ratio:.3f} (범위: {min_ratio:.3f}~{max_ratio:.3f})")
        
        # 총 추적 횟수 분석
        total_traces = [info.get('total_traces', 0) for info in self.routing_info if 'total_traces' in info]
        if total_traces:
            avg_traces = statistics.mean(total_traces)
            self.log(f"\n평균 총 추적 횟수: {avg_traces:.1f}")
    
    def analyze_query_patterns(self):
        """질의 패턴 분석"""
        self.log("\n" + "="*60)
        self.log("💬 질의 패턴 분석")
        self.log("="*60)
        
        self.log("주요 질의와 선택된 에이전트:")
        self.log("-" * 40)
        
        # 빈도순으로 정렬
        sorted_queries = sorted(self.query_patterns.items(), 
                              key=lambda x: len(x[1]), reverse=True)
        
        for query, agents in sorted_queries[:10]:  # 상위 10개만 표시
            agent_counts = Counter(agents)
            
            self.log(f"\n질의: '{query}' ({len(agents)}회)")
            for agent, count in agent_counts.most_common():
                percentage = (count / len(agents)) * 100
                self.log(f"  → {agent}: {count}회 ({percentage:.1f}%)")
    
    def generate_summary(self):
        """분석 요약 생성"""
        self.log("\n" + "="*60)
        self.log("📋 분석 요약")
        self.log("="*60)
        
        total_tests = len(self.results)
        unique_queries = len(self.query_patterns)
        
        self.log(f"• 총 테스트 수: {total_tests}")
        self.log(f"• 고유 질의 수: {unique_queries}")
        self.log(f"• 에이전트 수: {len(self.agent_counts)}")
        
        # 가장 많이 선택된 에이전트
        if self.agent_counts:
            most_selected = self.agent_counts.most_common(1)[0]
            least_selected = self.agent_counts.most_common()[-1]
            
            self.log(f"• 최다 선택 에이전트: {most_selected[0]} ({most_selected[1]}회)")
            self.log(f"• 최소 선택 에이전트: {least_selected[0]} ({least_selected[1]}회)")
            
            # 분포 균등성 측정 (표준편차)
            counts = list(self.agent_counts.values())
            if len(counts) > 1:
                std_dev = statistics.stdev(counts)
                mean_count = statistics.mean(counts)
                cv = (std_dev / mean_count) * 100  # 변동계수
                
                self.log(f"• 분포 균등성 (CV): {cv:.1f}% (낮을수록 균등)")
                
                if cv < 10:
                    self.log("  → 매우 균등한 분포 ✅")
                elif cv < 20:
                    self.log("  → 비교적 균등한 분포 ⚖️")
                else:
                    self.log("  → 불균등한 분포 ⚠️")
    
    def save_results(self):
        """분석 결과를 txt 파일로 저장"""
        # test_result_anal 디렉토리 생성
        output_dir = "test_result_anal"
        os.makedirs(output_dir, exist_ok=True)
        
        # 파일명 생성
        output_file = os.path.join(output_dir, f"analysis_{self.datetime_str}.txt")
        
        # 분석 결과를 파일로 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"테스트 결과 분석 리포트\n")
            f.write(f"분석 날짜시간: {self.datetime_str}\n")
            f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "="*80 + "\n\n")
            
            for line in self.analysis_output:
                f.write(line + "\n")
        
        self.log(f"\n💾 분석 결과가 저장되었습니다: {output_file}")
        return output_file
    
    def run_analysis(self):
        """전체 분석 실행"""
        self.log("🔍 테스트 결과 분석을 시작합니다...")
        self.log(f"⏰ 분석 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"📅 대상 날짜시간: {self.datetime_str}")
        
        # 테스트 디렉토리 찾기
        test_dir = self.find_test_directory()
        if not test_dir:
            return
            
        # 테스트 결과 로드
        if not self.load_test_results(test_dir):
            return
            
        # 각종 분석 실행
        self.analyze_agent_distribution()
        self.analyze_weight_effects()
        self.analyze_routing_patterns()
        self.analyze_query_patterns()
        self.generate_summary()
        
        # 결과 저장
        output_file = self.save_results()
        
        self.log(f"\n⏰ 분석 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("🎉 분석이 완료되었습니다!")
        
        return output_file

def main():
    """메인 함수"""
    if len(sys.argv) != 2:
        print("사용법: python3 analyze_results.py <날짜시간>")
        print("예시: python3 analyze_results.py 20250702_032337")
        sys.exit(1)
    
    datetime_str = sys.argv[1]
    analyzer = TestResultAnalyzer(datetime_str)
    analyzer.run_analysis()

if __name__ == "__main__":
    main()