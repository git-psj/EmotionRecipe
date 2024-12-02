import streamlit as st
from datetime import datetime, timedelta
from urllib.parse import urlencode
from utils.diary_functions import showDiaries
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

    # 각 탭에 맞는 날짜 범위 설정
    with tab1:      
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
    with tab2:
        start_date = today.replace(day=1)                     # 월간 시작일
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)  # 월간 종료일
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)
    with tab3:
        start_date = today.replace(month=1, day=1)            # 연도 시작일
        end_date = today.replace(month=12, day=31)            # 연도 종료일
        st.write(f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        plot_emotion_data(start_date, end_date)
