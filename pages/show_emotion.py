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
    if "current_week_start" not in st.session_state:
        st.session_state.current_week_start = today - timedelta(days=today.weekday())  # 이번 주 시작일
    if "current_month_start" not in st.session_state:
        st.session_state.current_month_start = today.replace(day=1)  # 이번 달 시작일
    if "current_year_start" not in st.session_state:
        st.session_state.current_year_start = today.replace(month=1, day=1)  # 이번 연도 시작일

    # "다음 주" 버튼 비활성화 상태 관리
    if "next_disabled" not in st.session_state:
        # "다음 주" 버튼이 처음 비활성화 상태로 시작하도록 설정
        st.session_state.next_disabled = False

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["주간 보기", "월별 보기", "연도별 보기"])

    # 주간 보기
    with tab1:         
        start_date = st.session_state.current_week_start
        end_date = start_date + timedelta(days=6)

        # 오늘 날짜가 주의 시작일일 경우 "다음 주" 버튼 비활성화
        if start_date >= today - timedelta(weeks=1):
            st.session_state.next_disabled = True
        else:
            st.session_state.next_disabled = False

        # 이전, 이번 주, 다음 주 버튼
        if st.button("이전 주", key="previous_week"):
            st.session_state.current_week_start -= timedelta(weeks=1)
            st.rerun()
        if st.button("이번주", key="current_week"):
            del st.session_state['current_week_start']
            st.rerun()
        if st.button("다음 주", key="next_week", disabled=st.session_state.next_disabled):
            st.session_state.current_week_start += timedelta(weeks=1)
            st.rerun()

        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 월별 보기
    with tab2:
        start_date = st.session_state.current_month_start
        next_month_start = (start_date + timedelta(days=31)).replace(day=1)
        end_date = next_month_start - timedelta(days=1)

        # "다음 달" 버튼 비활성화
        if start_date.month >= today.month and start_date.year >= today.year:
            next_month_disabled = True
        else:
            next_month_disabled = False

        # 이전, 다음 달 버튼
        if st.button("이전 달", key="previous_month"):
            prev_month_end = start_date - timedelta(days=1)
            st.session_state.current_month_start -= prev_month_end.replace(day=1)
            st.rerun()
        if st.button("이번달", key="current_month"):
            del st.session_state['current_month_start']
            st.rerun()
        if st.button("다음 달", key="next_month", disabled=next_month_disabled):
            next_month_start = (end_date + timedelta(days=1)).replace(day=1)
            st.session_state.current_month_start += next_month_start
            st.rerun()

        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 연도별 보기
    with tab3:
        start_date = st.session_state.current_year_start
        end_date = start_date.replace(month=12, day=31)

        # "다음 연도" 버튼 비활성화
        if start_date.year >= today.year:
            next_year_disabled = True
        else:
            next_year_disabled = False

        # 이전, 다음 연도 버튼
        if st.button("이전 연도", key="previous_year"):
            st.session_state.current_year_start -= start_date.replace(year=start_date.year - 1)
            st.rerun()
        if st.button("이번 연도", key="current_year"):
            del st.session_state['current_year_start']
            st.rerun()
        if st.button("다음 연도", key="next_year", disabled=next_year_disabled):
            st.session_state.current_year_start += start_date.replace(year=start_date.year + 1)
            st.rerun()

        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)
