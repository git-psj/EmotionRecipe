import streamlit as st
from EmotionRecipe.utils.solution_functions import (
    recommend_and_save_solution,
    get_latest_diary_and_emotion,
)

# Streamlit 앱 시작
st.title("감정 레시피 테스트 페이지")
st.write("이 페이지는 감정에 따른 추천 활동을 테스트하기 위한 페이지입니다.")

# 세션 상태 초기화
if 'db' not in st.session_state:
    st.session_state.db = None  # Firebase DB 연결 필요

# 사용자 이메일 입력
user_email = st.text_input("사용자 이메일을 입력하세요:")

# 일기 및 감정 데이터 가져오기
if st.button("최근 일기 가져오기"):
    if user_email:
        latest_date, diary_data, emotion_data, _ = get_latest_diary_and_emotion(user_email)
        if latest_date:
            st.write(f"최근 일기 날짜: {latest_date}")
            st.write(f"일기 내용: {diary_data.get('content', '내용 없음')}")
            st.write(f"감정: {emotion_data.get('emotion', '알 수 없음')}, 점수: {emotion_data.get('score', 0)}")
        else:
            st.warning("최근 일기를 가져올 수 없습니다.")
    else:
        st.warning("이메일을 입력하세요.")

# 감정 및 점수 입력
emotion = st.selectbox("감정을 선택하세요:", ["기쁨", "슬픔", "분노", "사랑", "욕망", "혐오"])
score = st.slider("감정 점수를 선택하세요:", 1, 10)

# 활동 추천 및 저장 실행
if st.button("활동 추천 및 저장"):
    if user_email:
        recommend_and_save_solution(user_email, "2024-11-27", emotion, score)
        st.success("활동이 성공적으로 추천되고 저장되었습니다!")
    else:
        st.warning("이메일을 입력하세요.")
