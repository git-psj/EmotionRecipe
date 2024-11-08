import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from datetime import datetime
import requests
import json

# # secrets.toml에서 Firebase 자격 증명 정보 가져오기
firebase_credentials = {
    "type": st.secrets["firebase"]["type"],
    "project_id": st.secrets["firebase"]["project_id"],
    "private_key_id": st.secrets["firebase"]["private_key_id"],
    "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["firebase"]["client_email"],
    "client_id": st.secrets["firebase"]["client_id"],
    "auth_uri": st.secrets["firebase"]["auth_uri"],
    "token_uri": st.secrets["firebase"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
}

# # Firebase 초기화 중복 방지
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

# Firestore 초기화
st.session_state.db = firestore.client()

# 회원가입 처리 함수
def register_user(email, password, nickname, age_group, gender, address):
    try:
        user = auth.create_user(email=email, password=password)
        st.success(f"회원가입 성공! 사용자 ID: {user.uid}")
        
        user_data = {
            "email": email,
            "nickname": nickname,
            "age_group": age_group,
            "gender": gender,
            "address": address
        }
        db.collection("users").document(email).set(user_data)
        st.success("사용자 정보가 Firestore에 저장되었습니다.")
    except Exception as e:
        st.error(f"오류 발생: {e}")

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
        data = response.json()
        return data['idToken']
    else:
        raise Exception(response.json().get('error', {}).get('message', '로그인 실패'))

# 회원가입 페이지
def signup_page():
    st.title("회원가입")
    email = st.text_input("이메일")
    password = st.text_input("비밀번호", type="password")
    password_confirm = st.text_input("비밀번호 확인", type="password")
    nickname = st.text_input("닉네임")
    age_group = st.selectbox("연령대", ["10대", "20대", "30대", "40대", "50대 이상"])
    gender = st.selectbox("성별", ["남성", "여성", "기타"])
    address = st.text_input("주소 (시/도)")

    if st.button("회원가입"):
        if password != password_confirm:
            st.error("비밀번호가 일치하지 않습니다.")
        else:
            register_user(email, password, nickname, age_group, gender, address)
    if st.button("로그인 하러 가기"):
                st.session_state.page = "login"

# 로그인 페이지
def login_page():
    st.title("로그인 페이지")
    email = st.text_input("이메일")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        try:
            id_token = sign_in_with_email_and_password(email, password)
            st.session_state.decoded_token = auth.verify_id_token(id_token)
            st.success(f"로그인 성공! ID 토큰: {id_token} , 몰라: {id_token}")
            st.write(st.session_state.decoded_token['email'])
            st.session_state.page = "diary"
        except Exception as e:
            st.error(f"로그인 실패: {str(e)}")
    if st.button("회원가입 하러 가기"):
                st.session_state.page = "signup"

# 로그아웃
def firebase_logout():
    try:
        # 현재 로그인된 사용자 정보 확인
        try:
            user = auth.get_user_by_email(st.session_state.decoded_token['email'])
   
            # st.write(st.session_state.decoded_token)
            # 로그아웃 처리
            st.session_state.decoded_token.clear()
            st.session_state.page = "login"
            # 세션 변수 초기화
            # st.write(st.session_state.decoded_token)
            st.success("로그아웃되었습니다.")
        except:
            st.info("이미 로그아웃된 상태입니다.")
    except Exception as e:
        st.error(f"로그아웃 중 오류 발생: {e}")

# 일기 작성 페이지
def diary_page():
    st.write("로그인 완료! 사이드바에서 메뉴를 선택해주세요.")
    # selected_date = st.sidebar.date_input("날짜 선택", datetime.now())
    # date = selected_date.strftime("%Y-%m-%d")
    # st.markdown(f"## {selected_date} 일기 작성")
    
    # diary_text = st.text_area("일기 내용 입력", height=200)
    # uploaded_image = st.file_uploader("이미지 삽입", type=['jpg', 'png', 'jpeg'])

    # if st.button("저장"):
    #     uemail = st.session_state.decoded_token['email']
    #     image_url = None
    #     if uploaded_image:
            
    #         # Firebase Storage 버킷 참조 생성
    #         bucket = storage.bucket(st.session_state.firebase_credentials['storageBucket'])
            
    #         # 고유한 파일 이름 생성 (예: 사용자 이메일 + 날짜 + UUID)
    #         image_filename = f"{uemail}_{date}_{uploaded_image.name}"
    #         st.write(f"{bucket}/{image_filename}")
    #         blob = bucket.blob(image_filename)
    #         st.write(blob)
    #         blob.upload_from_file(uploaded_image, content_type=uploaded_image.type)
    #         blob.make_public()
    #         image_url = blob.public_url
        
    #     doc_ref = db.collection('users').document(uemail).collection('diaries').document(date)
    #     doc_ref.set({
    #         "content": diary_text,
    #         "image": image_url if uploaded_image else None,
    #         'timestamp': firestore.SERVER_TIMESTAMP
    #     })
    #     st.success("일기가 저장되었습니다.")
    #     # st.image(image_url)
    #     st.session_state.page = "login"
    #     st.write(st.session_state.page)

# 메인 페이지 설정
def main():
    # 로그인 성공 시 일기 작성 페이지로 이동

    # 위에서 정의한 로그아웃 함수 호출
    if st.button("로그아웃"):
        firebase_logout()
    if "user" in st.session_state:
        diary_page()
    else:
        # 페이지 상태가 없으면 기본값을 설정
        if "page" not in st.session_state:
            st.session_state.page = "login"

        # 페이지 상태에 따른 조건부 렌더링
        # 버튼을 클릭 시 페이지 상태를 변경하고 다시 렌더링
        if st.session_state.page == "None":
            if st.button("회원가입 하러 가기"):
                st.session_state.page = "signup"
            if st.button("로그인 하러 가기"):
                st.session_state.page = "login"
        elif st.session_state.page == "signup":
            signup_page()
        elif st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "diary":
            
            diary_page()
        

if __name__ == "__main__":
    main()
