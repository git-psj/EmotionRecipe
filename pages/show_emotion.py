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
        start_date = today - timedelta(days=today.weekday())  # 주간 시작일
        end_date = start_date + timedelta(days=6)             # 주간 종료일
        
        # 날짜 변경을 위한 버튼
        if st.button("이전 주", key="previous_week"):
            start_date -= timedelta(weeks=1)
            end_date -= timedelta(weeks=1)
        if st.button("다음 주", key="next_week"):
            start_date += timedelta(weeks=1)
            end_date += timedelta(weeks=1)

        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 월별 보기 탭
    with tab2:
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        if st.button("이전 달", key="previous_month"):
            start_date = (start_date - timedelta(days=1)).replace(day=1)
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        if st.button("다음 달", key="next_month"):
            start_date = (end_date + timedelta(days=1)).replace(day=1)
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)

    # 연도별 보기 탭
    with tab3:
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)

        if st.button("이전 연도", key="previous_year"):
            start_date = start_date.replace(year=start_date.year - 1)
            end_date = end_date.replace(year=end_date.year - 1)
        if st.button("다음 연도", key="next_year"):
            start_date = start_date.replace(year=start_date.year + 1)
            end_date = end_date.replace(year=end_date.year + 1)

        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)
