import streamlit as st
from firebase_admin import credentials, firestore
import plotly.graph_objects as go

from utils.mypage_functions import verify_password, mypage
from utils.etc import get_firebase_client, main


if not "id_token" in st.session_state:
    main()

else:
    if st.session_state.pwCheck == 0:
        verify_password()
    else:
        mypage(st.session_state.decoded_token['email'])
