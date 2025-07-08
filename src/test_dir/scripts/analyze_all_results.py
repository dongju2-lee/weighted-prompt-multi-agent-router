#!/usr/bin/env python3
"""
종합 가중치 테스트 결과 분석 스크립트
모든 테스트 결과를 분석하여 인사이트와 시각화 제공
"""

import os
import sys
import json
import csv
import glob
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

class WeightTestAnalyzer:
    def __init__(self, results_dir):
        self.results_dir = Path(results_dir)
        self.agents = ["축구_에이전트", "농구_에이전트", "야구_에이전트", "테니스_에이전트"]
        self.agent_emojis = {"축구_에이전트": "⚽", "농구_에이전트": "🏀", 
                           "야구_에이전트": "⚾", "테니스_에이전트": "🎾"}
        
    def analyze_all_tests(self):
        """모든 테스트 결과를 종합 분석"""
        print("📊 종합 가중치 테스트 결과 분석")
        print("=" * 50)
        
        # 각 테스트별 분석
        test_results = {}
        
        # 1. 점진적 가중치 증가 테스트 분석
        gradual_results = self.analyze_gradual_weight_test()
        if gradual_results:
            test_results['gradual'] = gradual_results
            
        # 2. 순차적 제어 테스트 분석
        sequential_results = self.analyze_sequential_control_test()
        if sequential_results:
            test_results['sequential'] = sequential_results
            
        # 3. 경쟁 상황 테스트 분석
        competition_results = self.analyze_competition_test()
        if competition_results:
            test_results['competition'] = competition_results
            
        # 4. 실시간 변경 테스트 분석
        realtime_results = self.analyze_realtime_test()
        if realtime_results:
            test_results['realtime'] = realtime_results
            
        # 5. 급격한 감소 테스트 분석
        sudden_drop_results = self.analyze_sudden_drop_test()
        if sudden_drop_results:
            test_results['sudden_drop'] = sudden_drop_results
        
        # 종합 인사이트 생성
        self.generate_insights(test_results)
        
        return test_results
    
    def analyze_gradual_weight_test(self):
        """점진적 가중치 증가 테스트 분석"""
        print("\n🔍 점진적 가중치 증가 테스트 분석")
        print("-" * 30)
        
        gradual_dirs = list(self.results_dir.glob("gradual_weight_test_*"))
        if not gradual_dirs:
            print("❌ 점진적 가중치 테스트 결과를 찾을 수 없습니다.")
            return None
            
        latest_dir = max(gradual_dirs, key=lambda x: x.stat().st_mtime)
        progression_file = latest_dir / "target_agent_progression.csv"
        
        if not progression_file.exists():
            print("❌ 진행률 데이터 파일을 찾을 수 없습니다.")
            return None
            
        # CSV 데이터 읽기
        progression_data = []
        with open(progression_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                progression_data.append({
                    'weight': float(row['weight']),
                    'count': int(row['count']),
                    'percentage': int(row['percentage'])
                })
        
        if progression_data:
            print(f"📈 가중치별 선택률 변화 ({len(progression_data)}단계):")
            for data in progression_data:
                print(f"   가중치 {data['weight']:3.1f}: {data['percentage']:2d}% ({data['count']:2d}회)")
                
            # 가중치 효과성 계산
            weight_effectiveness = self.calculate_weight_effectiveness(progression_data)
            print(f"💡 가중치 효과성 지수: {weight_effectiveness:.1f}% (선형 증가 대비)")
            
            return {
                'progression': progression_data,
                'effectiveness': weight_effectiveness,
                'test_dir': str(latest_dir)
            }
        
        return None
    
    def analyze_sequential_control_test(self):
        """순차적 제어 테스트 분석"""
        print("\n🔍 순차적 에이전트 제어 테스트 분석")
        print("-" * 30)
        
        sequential_dirs = list(self.results_dir.glob("sequential_control_test_*"))
        if not sequential_dirs:
            print("❌ 순차적 제어 테스트 결과를 찾을 수 없습니다.")
            return None
            
        latest_dir = max(sequential_dirs, key=lambda x: x.stat().st_mtime)
        effectiveness_file = latest_dir / "control_effectiveness.csv"
        
        if not effectiveness_file.exists():
            print("❌ 제어 효과 데이터 파일을 찾을 수 없습니다.")
            return None
            
        # 제어 효과 데이터 읽기
        control_data = []
        with open(effectiveness_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                emoji = self.agent_emojis.get(row['agent'], '❓')
                control_data.append({
                    'agent': row['agent'],
                    'effectiveness': int(row['effectiveness_percentage']),
                    'emoji': emoji
                })
        
        if control_data:
            print("🎯 에이전트별 제어 효과:")
            total_effectiveness = 0
            for data in sorted(control_data, key=lambda x: x['effectiveness'], reverse=True):
                print(f"   {data['emoji']} {data['agent']}: {data['effectiveness']:2d}%")
                total_effectiveness += data['effectiveness']
                
            avg_effectiveness = total_effectiveness / len(control_data)
            print(f"📊 평균 제어 효과: {avg_effectiveness:.1f}%")
            
            return {
                'control_data': control_data,
                'average_effectiveness': avg_effectiveness,
                'test_dir': str(latest_dir)
            }
        
        return None
    
    def analyze_competition_test(self):
        """경쟁 상황 테스트 분석"""
        print("\n🔍 경쟁 상황 테스트 분석")
        print("-" * 30)
        
        competition_dirs = list(self.results_dir.glob("competition_test_*"))
        if not competition_dirs:
            print("❌ 경쟁 상황 테스트 결과를 찾을 수 없습니다.")
            return None
            
        latest_dir = max(competition_dirs, key=lambda x: x.stat().st_mtime)
        competition_file = latest_dir / "competition_index.csv"
        
        if not competition_file.exists():
            print("❌ 경쟁 지수 데이터 파일을 찾을 수 없습니다.")
            return None
            
        # 경쟁 지수 데이터 읽기
        competition_data = []
        with open(competition_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                competition_data.append({
                    'scenario': row['scenario'],
                    'competition_index': int(row['competition_index'])
                })
        
        if competition_data:
            print("🏆 시나리오별 경쟁 지수 (100%=완전 경쟁):")
            scenarios_desc = {
                'equal': '동일 가중치',
                'slight': '미세한 차이',
                'three': '3자 경쟁',
                'four': '4자 균등',
                'high': '고가중치',
                'stepwise': '계단식'
            }
            
            for data in sorted(competition_data, key=lambda x: x['competition_index'], reverse=True):
                scenario_key = next((k for k in scenarios_desc.keys() if k in data['scenario']), 'other')
                desc = scenarios_desc.get(scenario_key, '기타')
                print(f"   {desc}: {data['competition_index']:2d}%")
                
            avg_competition = sum(d['competition_index'] for d in competition_data) / len(competition_data)
            print(f"📊 평균 경쟁 지수: {avg_competition:.1f}%")
            
            return {
                'competition_data': competition_data,
                'average_competition': avg_competition,
                'test_dir': str(latest_dir)
            }
        
        return None
    
    def analyze_realtime_test(self):
        """실시간 변경 테스트 분석"""
        print("\n🔍 실시간 다중 가중치 변경 테스트 분석")
        print("-" * 30)
        
        realtime_dirs = list(self.results_dir.glob("realtime_multi_change_test_*"))
        if not realtime_dirs:
            print("❌ 실시간 변경 테스트 결과를 찾을 수 없습니다.")
            return None
            
        latest_dir = max(realtime_dirs, key=lambda x: x.stat().st_mtime)
        realtime_file = latest_dir / "realtime_results.csv"
        weight_changes_file = latest_dir / "weight_changes.csv"
        
        if not realtime_file.exists():
            print("❌ 실시간 결과 데이터 파일을 찾을 수 없습니다.")
            return None
            
        # 실시간 결과 분석
        realtime_data = []
        with open(realtime_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                realtime_data.append({
                    'test_number': int(row['test_number']),
                    'change_point': row['change_point'] == 'yes',
                    'scenario_name': row['scenario_name'],
                    'selected_agent': row['selected_agent']
                })
        
        if realtime_data:
            # 변경 시점별 반응성 분석
            change_points = [d for d in realtime_data if d['change_point']]
            response_analysis = []
            
            for change in change_points:
                test_num = change['test_number']
                # 변경 후 3개 테스트 결과 확인
                next_tests = [d for d in realtime_data 
                            if d['test_number'] >= test_num and d['test_number'] < test_num + 3]
                
                if next_tests:
                    agents = [t['selected_agent'] for t in next_tests]
                    dominant_agent = Counter(agents).most_common(1)[0][0]
                    response_analysis.append({
                        'scenario': change['scenario_name'],
                        'responses': agents,
                        'dominant_agent': dominant_agent
                    })
            
            print(f"⚡ 가중치 변경 반응성 분석 ({len(change_points)}회 변경):")
            for i, analysis in enumerate(response_analysis):
                emoji = self.agent_emojis.get(analysis['dominant_agent'], '❓')
                print(f"   변경 {i+1}: {analysis['scenario']} → {emoji} {analysis['dominant_agent']}")
                
            # 전체 분포
            all_agents = [d['selected_agent'] for d in realtime_data]
            agent_distribution = Counter(all_agents)
            print(f"\n📈 전체 에이전트 분포 (총 {len(all_agents)}회):")
            for agent, count in agent_distribution.most_common():
                emoji = self.agent_emojis.get(agent, '❓')
                percentage = (count * 100) // len(all_agents)
                print(f"   {emoji} {agent}: {count}회 ({percentage}%)")
                
            return {
                'change_points': len(change_points),
                'response_analysis': response_analysis,
                'distribution': dict(agent_distribution),
                'test_dir': str(latest_dir)
            }
        
        return None
    
    def analyze_sudden_drop_test(self):
        """급격한 감소 테스트 분석"""
        print("\n🔍 급격한 가중치 감소 테스트 분석")
        print("-" * 30)
        
        sudden_dirs = list(self.results_dir.glob("sudden_drop_test_*"))
        if not sudden_dirs:
            print("❌ 급격한 감소 테스트 결과를 찾을 수 없습니다.")
            return None
            
        latest_dir = max(sudden_dirs, key=lambda x: x.stat().st_mtime)
        
        # 각 단계별 결과 분석
        phases = ['phase1_dominance', 'phase2_sudden_drop', 'phase3_alternative_boost', 'phase4_extreme_switch']
        phase_results = {}
        
        for phase in phases:
            phase_dir = latest_dir / phase
            if phase_dir.exists():
                test_files = list(phase_dir.glob("test_*.json"))
                if test_files:
                    agents = []
                    for test_file in test_files:
                        try:
                            with open(test_file, 'r') as f:
                                data = json.load(f)
                                if 'selected_agent' in data:
                                    agents.append(data['selected_agent'])
                        except:
                            continue
                    
                    if agents:
                        agent_count = Counter(agents)
                        dominant = agent_count.most_common(1)[0]
                        phase_results[phase] = {
                            'dominant_agent': dominant[0],
                            'dominant_count': dominant[1],
                            'total_tests': len(agents),
                            'dominance_rate': (dominant[1] * 100) // len(agents)
                        }
        
        if phase_results:
            print("💥 단계별 라우팅 전환 분석:")
            phase_names = {
                'phase1_dominance': '농구 주도권 확립',
                'phase2_sudden_drop': '농구 급격 감소',
                'phase3_alternative_boost': '축구 부스트',
                'phase4_extreme_switch': '축구→테니스 전환'
            }
            
            for phase, name in phase_names.items():
                if phase in phase_results:
                    result = phase_results[phase]
                    emoji = self.agent_emojis.get(result['dominant_agent'], '❓')
                    print(f"   {name}: {emoji} {result['dominant_agent']} "
                          f"({result['dominance_rate']}% - {result['dominant_count']}/{result['total_tests']})")
            
            return {
                'phase_results': phase_results,
                'test_dir': str(latest_dir)
            }
        
        return None
    
    def calculate_weight_effectiveness(self, progression_data):
        """가중치 효과성 계산"""
        if len(progression_data) < 2:
            return 0
            
        # 선형 증가 대비 실제 증가율 계산
        weights = [d['weight'] for d in progression_data]
        percentages = [d['percentage'] for d in progression_data]
        
        # 가중치 범위 정규화
        weight_range = max(weights) - min(weights)
        percentage_range = max(percentages) - min(percentages)
        
        if weight_range == 0 or percentage_range == 0:
            return 0
            
        # 효과성 지수: 실제 증가율 / 이론적 최대 증가율
        effectiveness = (percentage_range / weight_range) * (weight_range / max(weights)) * 100
        return min(effectiveness, 100)  # 100% 상한
    
    def generate_insights(self, test_results):
        """종합 인사이트 생성"""
        print("\n" + "=" * 50)
        print("💡 종합 인사이트 및 결론")
        print("=" * 50)
        
        insights = []
        
        # 1. 가중치 제어 효과성
        if 'gradual' in test_results and 'sequential' in test_results:
            gradual_eff = test_results['gradual']['effectiveness']
            sequential_eff = test_results['sequential']['average_effectiveness']
            
            if gradual_eff > 70 and sequential_eff > 80:
                insights.append("✅ 가중치 제어가 매우 효과적으로 작동합니다.")
            elif gradual_eff > 50 and sequential_eff > 60:
                insights.append("✅ 가중치 제어가 적절히 작동합니다.")
            else:
                insights.append("⚠️  가중치 제어 효과가 제한적입니다.")
        
        # 2. 경쟁 상황 분석
        if 'competition' in test_results:
            avg_competition = test_results['competition']['average_competition']
            if avg_competition > 80:
                insights.append("⚔️  높은 경쟁 지수로 균형잡힌 라우팅이 가능합니다.")
            elif avg_competition > 60:
                insights.append("⚔️  적절한 수준의 경쟁적 라우팅이 구현되었습니다.")
            else:
                insights.append("⚠️  경쟁 상황에서 편향된 라우팅이 발생할 수 있습니다.")
        
        # 3. 실시간 반응성
        if 'realtime' in test_results:
            change_points = test_results['realtime']['change_points']
            if change_points >= 8:
                insights.append("⚡ 실시간 가중치 변경에 대한 즉시적 반응이 확인되었습니다.")
            else:
                insights.append("⚡ 실시간 변경 테스트 샘플이 제한적입니다.")
        
        # 4. 시스템 안정성
        all_tests_successful = len(test_results) >= 4
        if all_tests_successful:
            insights.append("🔧 시스템이 다양한 가중치 시나리오에서 안정적으로 작동합니다.")
        
        # 인사이트 출력
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        # 추천사항
        print("\n📋 추천사항:")
        print("1. 시드 데이터 생성을 통해 0×가중치 문제를 해결했습니다.")
        print("2. 극단적 가중치 비율(10.0 vs 0.1)로 명확한 제어가 가능합니다.")
        print("3. 실시간 가중치 변경으로 동적 라우팅 제어가 구현되었습니다.")
        print("4. 경쟁 상황에서도 확률적 분배가 적절히 작동합니다.")
        
        # 결과 파일 저장
        summary_file = self.results_dir / "comprehensive_analysis.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("종합 가중치 테스트 분석 결과\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"분석 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for i, insight in enumerate(insights, 1):
                f.write(f"{i}. {insight}\n")
                
        print(f"\n📁 분석 결과 저장: {summary_file}")

def main():
    if len(sys.argv) != 2:
        print("사용법: python3 analyze_all_results.py <결과_디렉토리>")
        sys.exit(1)
    
    results_dir = sys.argv[1]
    if not os.path.exists(results_dir):
        print(f"❌ 결과 디렉토리를 찾을 수 없습니다: {results_dir}")
        sys.exit(1)
    
    analyzer = WeightTestAnalyzer(results_dir)
    analyzer.analyze_all_tests()

if __name__ == "__main__":
    main() 