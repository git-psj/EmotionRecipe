import streamlit as st
from firebase_admin import credentials, firestore
import plotly.graph_objects as go

from utils.mypage_functions import verify_password, mypage
from utils.etc import get_firebase_client, main

if "db" not in st.session_state:
    st.session_state.db = get_firebase_client()
st.session_state.pwCheck = 0

if not "id_token" in st.session_state:
    main()

else:
    st.title("감정 레시피")
    st.markdown("<h3 style='color: gray; margin-top: -10px;'>-- 마이페이지</h3>", unsafe_allow_html=True)
    if st.session_state.pwCheck == 0:
        verify_password()
    else:
        mypage(st.session_state.decoded_token['email'])
