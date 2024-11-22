import firebase_admin
import streamlit as st
from datetime import datetime
from firebase_admin import credentials, firestore
import os
import json
from utils.auth_functions import signup_page, login_page
from utils.diary_functions import diary_page
from utils.emotion_functions import analyze_emotion

def get_firebase_client():
    st.session_state.firebase_credentials = {
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
        "universe_domain" : st.secrets["firebase"]["universe_domain"],
        "apiKey" : st.secrets["firebase"]["apiKey"],
        "storageBucket": st.secrets["firebase"]["storageBucket"]
    }
    # Firebase 초기화 중복 방지
    if not firebase_admin._apps:
        cred = credentials.Certificate(st.session_state.firebase_credentials)
        firebase_admin.initialize_app(cred)

    return firestore.client()

# 메인 페이지 설정
def main():
    # 초기 상태 설정
    if "current_year" not in st.session_state:
        st.session_state.current_year = datetime.today().year
    if "current_month" not in st.session_state:
        st.session_state.current_month = datetime.today().month
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = None
    if "alert_message" not in st.session_state:
        st.session_state.alert_message = ""  # 알림 메시지 변수 초기화
    if "emotion_data" not in st.session_state:
        st.session_state.emotion_data = {}  # 알림 메시지 변수 초기화
    # 페이지 상태가 없으면 기본값을 설정
    if "page" not in st.session_state:
        st.session_state.page = "login"
    
    if not "id_token" in st.session_state and st.session_state.page != "signup":
        st.session_state.page = "login"

    st.title("감정 레시피")
    if "id_token" in st.session_state:
        go_logout()
        diary_page()
    else:
        # 페이지 상태에 따른 조건부 렌더링
        # 버튼을 클릭 시 페이지 상태를 변경하고 다시 렌더링
        if st.session_state.page == "signup":
            signup_page()
        elif st.session_state.page == "login":
            login_page()


def go_logout():
    st.markdown("""
        <div style="position: fixed; top: 50px; right: 50px; background-color: #87CEFA; padding: 10px; border-radius: 5px;">
            <a href="/main" target="_self" style="text-decoration: none; color: black;">로그아웃</a>
        </div>
    """, unsafe_allow_html=True)
