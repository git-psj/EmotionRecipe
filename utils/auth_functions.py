import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from datetime import datetime
import requests
import json

# register_user, signup_page, sign_in_with_email_and_password, login_page, firebase_logout

# 회원가입 처리 함수
def register_user(email, password, nickname, age_group, gender):
    try:
        user = auth.create_user(email=email, password=password)
        st.success(f"회원가입 성공! 사용자 ID: {user.uid}")
        
        user_data = {
            "email": email,
            "nickname": nickname,
            "age_group": age_group,
            "gender": gender,
            # "address": address
        }
        st.session_state.db.collection("users").document(email).set(user_data)
        st.success("사용자 정보가 Firestore에 저장되었습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")

# 회원가입 페이지
def signup_page():
    st.markdown("<h3 style='color: gray; margin-top: -10px;'>&nbsp;- 회원가입</h3>", unsafe_allow_html=True)
    email = st.text_input("이메일")
    password = st.text_input("비밀번호", type="password")
    password_confirm = st.text_input("비밀번호 확인", type="password")
    nickname = st.text_input("닉네임")
    age_group = st.selectbox("연령대", ["10대", "20대", "30대", "40대", "50대 이상"])
    gender = st.selectbox("성별", ["남성", "여성", "기타"])
    # address = st.text_input("주소 (시/도)")

    if st.button("회원가입"):
        if password != password_confirm:
            st.error("비밀번호가 일치하지 않습니다.")
        else:
            register_user(email, password, nickname, age_group, gender)
    if st.button("로그인 하러 가기"):
        st.session_state.page = "login"
        st.rerun()

# 로그인 처리 함수
def sign_in_with_email_and_password(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={st.session_state.firebase_credentials['apiKey']}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json().get('idToken')
    else:
        error_message = response.json().get('error', {}).get('message', '로그인 실패')
        st.error(f"로그인 오류: {error_message}")
        return 0
        
        
# 로그인 페이지
def login_page():
    st.markdown("<h3 style='color: gray; margin-top: -10px;'>&nbsp;- 로그인</h3>", unsafe_allow_html=True)
    email = st.text_input("이메일")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        try:
            st.session_state.id_token = sign_in_with_email_and_password(email, password)
            st.session_state.decoded_token = auth.verify_id_token(st.session_state.id_token)
            st.success("로그인 성공!")
            st.session_state.page = "diary"
            st.rerun()
        except Exception as e:
            st.error(f"로그인 실패: {str(e)}")
    if st.button("회원가입 하러 가기"):
        st.session_state.page = "signup"
        st.rerun()
