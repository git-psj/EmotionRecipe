import streamlit as st
from datetime import datetime, timedelta
from utils.etc import get_firebase_client, main, go_logout
from utils.emotion_functions import plot_emotion_data

# Firebase 연결
if "db" not in st.session_state:
    st.session_state.db = get_firebase_client()
st.session_state.pwCheck = 0

# 로그인 확인
if not "id_token" in st.session_state:
    main()
else:
    st.title("감정 레시피")
    st.markdown("<h3 style='color: gray; margin-top: -10px;'>&nbsp;- 감정통계보기</h3>", unsafe_allow_html=True)
    go_logout()
    today = datetime.now()

    # 초기 날짜 설정
    def initialize_date_state(key, date_func):
        if key not in st.session_state:
            st.session_state[key] = date_func()

    initialize_date_state("current_week_start", lambda: today - timedelta(days=today.weekday()))
    initialize_date_state("current_month_start", lambda: today.replace(day=1))
    initialize_date_state("current_year_start", lambda: today.replace(month=1, day=1))

    # 공통 버튼 처리 함수
    def handle_date_navigation(key, delta_func, reset_key=None):
        if st.button(f"이전 {reset_key or key}", key=f"prev_{key}"):
            st.session_state[key] = delta_func(st.session_state[key], -1)
            st.rerun()
        if st.button(f"이번 {reset_key or key}", key=f"curr_{key}"):
            del st.session_state[key]
            st.rerun()
        if st.button(f"다음 {reset_key or key}", key=f"next_{key}"):
            st.session_state[key] = delta_func(st.session_state[key], 1)
            st.rerun()

    # 주간 보기
    with st.tabs(["주간 보기", "월별 보기", "연도별 보기"])[0]:
        start_date, end_date = st.session_state.current_week_start, st.session_state.current_week_start + timedelta(days=6)
        handle_date_navigation("current_week_start", lambda date, delta: date + timedelta(weeks=delta), "주")
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 월별 보기
    with st.tabs(["주간 보기", "월별 보기", "연도별 보기"])[1]:
        start_date, end_date = st.session_state.current_month_start, (st.session_state.current_month_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        handle_date_navigation("current_month_start", lambda date, delta: (date.replace(day=1) + timedelta(days=delta * 31)).replace(day=1), "월")
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 연도별 보기
    with st.tabs(["주간 보기", "월별 보기", "연도별 보기"])[2]:
        start_date, end_date = st.session_state.current_year_start, st.session_state.current_year_start.replace(month=12, day=31)
        handle_date_navigation("current_year_start", lambda date, delta: date.replace(year=date.year + delta), "연도")
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)
