import streamlit as st
from utils.solution_functions import recommend_and_save_solution

def main():
    st.title("솔루션 추천 시스템")
    
    # 감정 입력
    emotion = st.selectbox("감정을 선택하세요", ["기쁨", "슬픔", "분노", "사랑", "욕구"])
    emotion_score = st.slider("감정 점수", 1, 10, 5)

    if st.button("솔루션 확인"):
        solution = recommend_and_save_solution(emotion, emotion_score)
        st.write(f"**추천된 솔루션**: {solution}")

if __name__ == "__main__":
    main()
