#!/usr/bin/env python3
"""
음식 추천 멀티 에이전트 시스템 실행기
"""

import sys
import os
import asyncio

# src 디렉토리를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))  # run_dir
src_dir = os.path.dirname(current_dir)  # src
sys.path.append(src_dir)

from agent.main import run_food_recommendation_system

async def main():
    """
    메인 함수
    """
    print("🍽️ 음식 추천 멀티 에이전트 시스템")
    print("=" * 50)
    print("\n💬 질문을 입력해주세요 (종료: 'quit' 또는 '종료'):")
    
    while True:
        try:
            # 사용자 입력 받기
            user_input = input("\n🍽️ 사용자: ").strip()
            
            # 종료 명령 체크
            if user_input.lower() in ["종료", "exit", "quit", "q", "나가기", "끝"]:
                print("\n👋 시스템을 종료합니다. 좋은 하루 되세요!")
                break
            
            if not user_input:
                print("❓ 질문을 입력해주세요.")
                continue
            
            print("\n🤖 처리 중...")
            
            # 멀티 에이전트 시스템 실행
            result = await run_food_recommendation_system(user_input)
            
            # 결과 출력
            print("\n" + "="*60)
            print(f"📝 질문: {user_input}")
            print("="*60)
            print(f"🎯 선택된 에이전트: {result.get('selected_agent', 'Unknown')}")
            
            final_response = result.get('final_response', {})
            print(f"\n🍽️ {final_response.get('agent', 'Unknown')} 응답:")
            print(f"   {final_response.get('answer', 'No response')}")
            
            if 'detail' in final_response:
                print(f"   상세: {final_response['detail']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 시스템을 종료합니다. 좋은 하루 되세요!")
            break
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {e}")
            print("다시 시도해주세요.")

if __name__ == "__main__":
    asyncio.run(main()) 