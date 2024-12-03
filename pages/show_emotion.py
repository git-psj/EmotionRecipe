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

    today = datetime.now().date()  # 시간 제거를 위해 date() 사용

    # 상태 초기화
    if "current_week_start" not in st.session_state:
        st.session_state.current_week_start = today - timedelta(days=today.weekday())
    if "current_month_start" not in st.session_state:
        st.session_state.current_month_start = today.replace(day=1)
    if "current_year_start" not in st.session_state:
        st.session_state.current_year_start = today.replace(month=1, day=1)

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["주간 보기", "월별 보기", "연도별 보기"])

    # 주간 보기
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("이전 주", key="previous_week"):
                st.session_state.current_week_start -= timedelta(weeks=1)
        with col2:
            if st.button("이번 주로 이동", key="current_week"):
                st.session_state.current_week_start = today - timedelta(days=today.weekday())
        with col3:
            disabled_next_week = st.session_state.current_week_start + timedelta(weeks=1) > today
            if st.button("다음 주", key="next_week", disabled=disabled_next_week):
                st.session_state.current_week_start += timedelta(weeks=1)

        start_date = st.session_state.current_week_start
        end_date = start_date + timedelta(days=6)
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 월별 보기
    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("이전 달", key="previous_month"):
                prev_month_end = st.session_state.current_month_start - timedelta(days=1)
                st.session_state.current_month_start = prev_month_end.replace(day=1)
        with col2:
            if st.button("이번 달로 이동", key="current_month"):
                st.session_state.current_month_start = today.replace(day=1)
        with col3:
            disabled_next_month = st.session_state.current_month_start.month == today.month
            if st.button("다음 달", key="next_month", disabled=disabled_next_month):
                next_month_start = (st.session_state.current_month_start + timedelta(days=31)).replace(day=1)
                st.session_state.current_month_start = next_month_start

        start_date = st.session_state.current_month_start
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 연도별 보기
    with tab3:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("이전 연도", key="previous_year"):
                st.session_state.current_year_start = st.session_state.current_year_start.replace(
                    year=st.session_state.current_year_start.year - 1
                )
        with col2:
            if st.button("이번 연도로 이동", key="current_year"):
                st.session_state.current_year_start = today.replace(month=1, day=1)
        with col3:
            disabled_next_year = st.session_state.current_year_start.year == today.year
            if st.button("다음 연도", key="next_year", disabled=disabled_next_year):
                st.session_state.current_year_start = st.session_state.current_year_start.replace(
                    year=st.session_state.current_year_start.year + 1
                )

        start_date = st.session_state.current_year_start
        end_date = start_date.replace(month=12, day=31)
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)
