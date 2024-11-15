import streamlit as st

import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from utils.etc import get_firebase_client, main
from utils.solution_functions import display_solution_page, get_token_date

date, token = get_token_date()
if not "id_token" in st.session_state and token is None:
    main()
else:
    with st.spinner("솔루션 정보를 불러오는 중..."):
        # 솔루션 페이지 함수 호출
        display_solution_page(date, token)
