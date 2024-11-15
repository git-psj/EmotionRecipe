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

if __name__ == "__main__":
    main()
