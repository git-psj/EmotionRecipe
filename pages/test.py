from utils.solution_functions import recommend_and_save_solution

def main():
    # 사용자가 직접 입력한 감정과 감정 점수
    emotion = "기쁨"  # 예시: '기쁨', '슬픔', '분노' 등
    emotion_score = 8  # 예시: 1에서 10 사이의 값

    # 솔루션 추천 함수 호출
    solution = recommend_and_save_solution(emotion, emotion_score)

    # 추천된 솔루션 출력
    print("추천된 솔루션:")
    print(f"감정: {emotion}")
    print(f"감정 점수: {emotion_score}")
    print(f"솔루션: {solution}")

if __name__ == "__main__":
    main()
