import streamlit as st
from datetime import datetime, timedelta
from utils.etc import get_firebase_client, main, go_logout
from utils.emotion_functions import plot_emotion_data

if "db" not in st.session_state:
    st.session_state.db = get_firebase_client()
st.session_state.pwCheck = 0

if not "id_token" in st.session_state:
    main()

else:
    st.title("감정 레시피")
    st.markdown("<h3 style='color: gray; margin-top: -10px;'>&nbsp;- 감정통계보기</h3>", unsafe_allow_html=True)
    go_logout()

    # 보기 옵션을 탭으로 구성
    tab1, tab2, tab3 = st.tabs(["주간 보기", "월별 보기", "연도별 보기"])

    # 현재 날짜 기준으로 필터링 범위 설정
    today = datetime.now()

    # 주간 보기 탭
    with tab1:
        # 주간 시작일과 종료일 계산
        start_date = today - timedelta(days=today.weekday())  # 주간 시작일
        end_date = start_date + timedelta(days=6)             # 주간 종료일
        
        # 날짜 변경을 위한 버튼
        if st.button("이전"):
            start_date -= timedelta(weeks=1)  # 이전 주로 이동
            end_date -= timedelta(weeks=1)
        if st.button("다음"):
            start_date += timedelta(weeks=1)  # 다음 주로 이동
            end_date += timedelta(weeks=1)
        
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 월별 보기 탭
    with tab2:
        # 월간 시작일과 종료일 계산
        start_date = today.replace(day=1)                     # 월간 시작일
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)  # 월간 종료일
        
        # 날짜 변경을 위한 버튼
        if st.button("이전"):
            start_date -= timedelta(days=30)  # 이전 달로 이동
            end_date -= timedelta(days=30)
        if st.button("다음"):
            start_date += timedelta(days=30)  # 다음 달로 이동
            end_date += timedelta(days=30)
        
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 연도별 보기 탭
    with tab3:
        # 연도 시작일과 종료일 계산
        start_date = today.replace(month=1, day=1)            # 연도 시작일
        end_date = today.replace(month=12, day=31)            # 연도 종료일
        
        # 날짜 변경을 위한 버튼
        if st.button("이전"):
            start_date -= timedelta(days=365)  # 이전 년도로 이동
            end_date -= timedelta(days=365)
        if st.button("다음"):
            start_date += timedelta(days=365)  # 다음 년도로 이동
            end_date += timedelta(days=365)
        
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)
