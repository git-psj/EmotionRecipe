import streamlit as st
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials, firestore
import plotly.graph_objects as go

from utils.auth_functions import sign_in_with_email_and_password

# verify_password, get_user_info, update_user_info, delete_user_account, mypage
# get_user_info(email), verify_password(), update_user_info(email, nickname, age_group, gender), delete_user_account(email),mypage(email)

# 비밀번호 확인 함수
def verify_password():
    email = st.session_state.decoded_token['email']
    password = st.text_input("비밀번호 확인", type="password")
    if st.button("확인"):
        st.session_state.pwCheck = sign_in_with_email_and_password(email, password)
        if st.session_state.pwCheck == 0:
            return False
        else:
            return True
            
# 사용자 정보 가져오기
def get_user_info(email):
    try:
        user_doc = st.session_state.db.collection("users").document(email).get()
        if user_doc.exists:
            return user_doc.to_dict()
        else:
            st.error("사용자 정보를 찾을 수 없습니다.")
            return None
    except Exception as e:
        st.error(f"오류 발생: {e}")
        return None
    
# 사용자 정보 수정 함수
def update_user_info(email, nickname, age_group, gender):
    try:
        st.session_state.db.collection("users").document(email).update({
            "nickname": nickname,
            "age_group": age_group,
            "gender": gender
        })
        st.success("사용자 정보가 성공적으로 수정되었습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")

# 회원 탈퇴 함수
def delete_user_account(email):
    try:
        # Firebase Authentication에서 사용자 삭제
        user = auth.get_user_by_email(email)
        auth.delete_user(user.uid)
        
        # Firestore에서 사용자 데이터 삭제
        st.session_state.db.collection("users").document(email).delete()
        st.success("회원 탈퇴가 완료되었습니다.")
        # 세션 초기화
        st.session_state.clear()
        st.session_state.page = "signup"  # 탈퇴 후 회원가입 페이지로 이동
        st.rerun()
    except Exception as e:
        st.error(f"오류 발생: {e}")

# 마이페이지 함수
def mypage(email):
    st.title("마이페이지")
    user_info = get_user_info(email)
    
    if user_info:
        st.text(f"이메일: {email}")
        nickname = st.text_input("닉네임", value=user_info.get("nickname", ""))
        age_group = st.selectbox("연령대", ["10대", "20대", "30대", "40대", "50대 이상"], index=["10대", "20대", "30대", "40대", "50대 이상"].index(user_info.get("age_group", "10대")))
        gender = st.selectbox("성별", ["남성", "여성", "기타"], index=["남성", "여성", "기타"].index(user_info.get("gender", "남성")))
        if st.button("정보 수정"):
            update_user_info(email, nickname, age_group, gender)
        
        st.write("---")
        if st.button("회원 탈퇴"):
            st.write("회원 탈퇴 시 모든 정보를 복원할 수 없습니다.")
            if verify_password():
                delete_user_account(email)
