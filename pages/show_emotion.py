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
        st.session_state.current_week_start = today - timedelta(days=today.weekday())

    if "current_month_start" not in st.session_state:
        st.session_state.current_month_start = today.replace(day=1)

    if "current_year_start" not in st.session_state:
        st.session_state.current_year_start = today.replace(month=1, day=1)

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["주간 보기", "월별 보기", "연도별 보기"])

    # 주간 보기
    with tab1:
        start_date = st.session_state.current_week_start
        end_date = start_date + timedelta(days=6)
        
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 월별 보기
    with tab2:
        start_date = st.session_state.current_month_start
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 연도별 보기
    with tab3:
        start_date = st.session_state.current_year_start
        end_date = start_date.replace(month=12, day=31)

        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)
