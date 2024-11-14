import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore
import os
import json
from utils.auth_functions import signup_page, login_page
from utils.diary_functions import diary_page
from utils.emotion_functions import analyze_emotion

def get_firebase_client():
    try:
        with open('./firebase_credentials.json') as f:
            st.session_state.firebase_credentials = json.load(f)
        # Firebase 초기화 중복 방지
        if not firebase_admin._apps:
            cred = credentials.Certificate('./firebase_credentials.json')
            firebase_admin.initialize_app(cred)
    except:
        if not firebase_admin._apps:
            cred = credentials.Certificate('../firebase_credentials.json')
            firebase_admin.initialize_app(cred)

    return firestore.client()

# 메인 페이지 설정
def main():
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
        elif st.session_state.page == "diary":
            diary_page()


def go_logout():
    st.markdown("""
        <div style="position: fixed; top: 50px; right: 50px; background-color: #87CEFA; padding: 10px; border-radius: 5px;">
            <a href="/main" target="_self" style="text-decoration: none; color: black;">로그아웃</a>
        </div>
    """, unsafe_allow_html=True)