#!/usr/bin/env python3
"""
운동 추천 멀티 에이전트 시스템 실행 스크립트 (비동기 버전)
"""

import sys
import os
import asyncio

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.graph import run_sports_agent_workflow
from agent.utils import validate_environment, format_percentage
from agent.prompts import get_welcome_message


async def main():
    """메인 실행 함수"""
    # 환경 변수 검증
    if not validate_environment():
        print("❌ 환경 설정을 확인해주세요.")
        return
    
    # 환영 메시지 출력
    print(get_welcome_message())
    
    print("\n🚀 운동 추천 멀티 에이전트 시스템이 준비되었습니다!")
    print("질문을 입력하세요 (종료: 'quit' 또는 'exit')\n")
    
    while True:
        try:
            # 사용자 입력
            user_input = input("🏃 운동 추천 질문: ").strip()
            
            # 종료 조건
            if user_input.lower() in ['quit', 'exit', '종료', 'q']:
                print("\n👋 운동 추천 시스템을 종료합니다. 건강한 운동 하세요!")
                break
            
            if not user_input:
                print("❌ 질문을 입력해주세요.")
                continue
            
            print(f"\n🔄 '{user_input}' 분석 중...")
            
            # 멀티 에이전트 워크플로우 실행
            result = await run_sports_agent_workflow(user_input)
            
            if result.get("success"):
                # 성공적인 결과 출력
                print_result(result)
            else:
                print(f"❌ 오류: {result.get('error', '알 수 없는 오류')}")
            
            print("\n" + "="*70)
            
        except KeyboardInterrupt:
            print("\n\n👋 운동 추천 시스템을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")


def print_result(result):
    """결과 출력 함수"""
    try:
        selected_agent = result.get("selected_agent", "알 수 없음")
        agent_response = result.get("agent_response", {})
        routing_info = result.get("routing_info", {})
        
        print(f"\n✅ 선택된 에이전트: {selected_agent}")
        print(f"📝 추천 내용: {agent_response.get('answer', '응답 없음')}")
        print(f"ℹ️  상세 정보: {agent_response.get('detail', '상세 정보 없음')}")
        
        # 라우팅 정보 출력
        if routing_info:
            normalized_ratios = routing_info.get("normalized_ratios", {})
            total_traces = routing_info.get("total_traces", 0)
            
            print(f"\n📊 라우팅 분석 (총 {total_traces}회 참고):")
            for agent, ratio in normalized_ratios.items():
                mark = "★" if agent == selected_agent else " "
                print(f"  {mark} {agent}: {format_percentage(ratio)}")
        
    except Exception as e:
        print(f"❌ 결과 출력 중 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 