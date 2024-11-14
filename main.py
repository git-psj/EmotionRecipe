import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from datetime import datetime
import requests
import json
from utils.auth_functions import signup_page, login_page
from utils.diary_functions import fetch_emotions_for_month, get_emotions_for_month, display_calendar, move_month, year_selector, diary_page
from utils.emotion_functions import analyze_emotion
from utils.etc import get_firebase_client, go_logout, main

# Firestore 초기화
st.session_state.db = get_firebase_client()
st.session_state.pwCheck = 0

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

if __name__ == "__main__":
    main()
