import streamlit as st
from datetime import datetime, timedelta
from utils.etc import get_firebase_client, main, go_logout
from utils.emotion_functions import plot_emotion_data

# Firebase 연결
if "db" not in st.session_state:
    st.session_state.db = get_firebase_client()
st.session_state.pwCheck = 0


 def handle_date_navigation(key, delta_func, period_label, disable_next_check=None):
    start_date = st.session_state[key]
    end_date = delta_func(start_date)
    # 이전 버튼
    if st.button(f"이전 {period_label}", key=f"prev_{key}"):
        st.session_state[key] = delta_func(start_date, -1)
        st.rerun()
    # 현재 버튼 (초기화)
    if st.button(f"이번 {period_label}", key=f"curr_{key}"):
        del st.session_state[key]
        st.rerun()
    # 다음 버튼 (비활성화 조건 포함)
    next_disabled = disable_next_check(start_date) if disable_next_check else False
    if st.button(f"다음 {period_label}", key=f"next_{key}", disabled=next_disabled):
        st.session_state[key] = delta_func(start_date, 1)
        st.rerun()
    # 날짜 범위 출력 및 감정 데이터 시각화
    st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    plot_emotion_data(start_date, end_date)


# 로그인 확인
if not "id_token" in st.session_state:
    main()
else:
    st.title("감정 레시피")
    st.markdown("<h3 style='color: gray; margin-top: -10px;'>&nbsp;- 감정통계보기</h3>", unsafe_allow_html=True)
    go_logout()
    today = datetime.now()

    # 초기 날짜 설정
    if "current_week_start" not in st.session_state:
        st.session_state.current_week_start = today - timedelta(days=today.weekday())  # 이번 주 시작일
    if "current_month_start" not in st.session_state:
        st.session_state.current_month_start = today.replace(day=1)  # 이번 달 시작일
    if "current_year_start" not in st.session_state:
        st.session_state.current_year_start = today.replace(month=1, day=1)  # 이번 연도 시작일

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["주간 보기", "월별 보기", "연도별 보기"])

    # 주간 보기
    with tab1:         
        handle_date_navigation("current_week_start", lambda d, s=0: d + timedelta(weeks=s, days=6 * (s == 0)), "주", lambda d: d >= datetime.now() - timedelta(weeks=1))
        
        

    # 월별 보기
    with tab2:
        start_date = st.session_state.current_month_start
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        # 이전, 다음 버튼
        if st.button("이전 달", key="previous_month"):
            prev_month_end = start_date - timedelta(days=1)
            st.session_state.current_month_start = prev_month_end.replace(day=1)
            st.rerun()
        if st.button("이번달", key="current_month"):
            del st.session_state['current_month_start']
            st.rerun()
        if st.button("다음 달", key="next_month"):
            next_month_start = (end_date + timedelta(days=1)).replace(day=1)
            st.session_state.current_month_start = next_month_start
            st.rerun()

        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 연도별 보기
    with tab3:
        start_date = st.session_state.current_year_start
        end_date = start_date.replace(month=12, day=31)

        # 이전, 다음 버튼
        if st.button("이전 연도", key="previous_year"):
            st.session_state.current_year_start = start_date.replace(year=start_date.year - 1)
            st.rerun()
        if st.button("이번 연도", key="current_year"):
            del st.session_state['current_year_start']
            st.rerun()
        if st.button("다음 연도", key="next_year"):
            st.session_state.current_year_start = start_date.replace(year=start_date.year + 1)
            st.rerun()

        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)
