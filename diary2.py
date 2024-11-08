import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from datetime import datetime
import requests
import json
import calendar
import openai
import sys
import os
import re

# 상위 폴더 경로를 가져와서 sys.path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 상위 폴더에 있는 파일을 import
import diary

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

uemail = st.session_state.decoded_token['email']

from datetime import datetime
import calendar

# Firestore에서 특정 달의 감정 데이터를 가져오는 함수
def fetch_emotions_for_month(year, month):
    st.session_state.emotion_data = {}
    num_days = calendar.monthrange(year, month)[1]

    # 기본적으로 모든 날짜를 빈 문자열로 초기화
    for day in range(1, num_days + 1):
        date_str = f"{year}-{month:02}-{day:02}"
        st.session_state.emotion_data[date_str] = ""

    try:
        # Firestore에서 감정 데이터를 한 번에 가져옴
        docs = st.session_state.db.collection('users').document(uemail).collection('emotions').stream()
        for doc in docs:
            doc_id = doc.id
            try:
                doc_date = datetime.strptime(doc_id, "%Y-%m-%d")
                if doc_date.year == year and doc_date.month == month:
                    # 해당 날짜의 감정 데이터를 업데이트
                    st.session_state.emotion_data[doc_id] = doc.to_dict().get("이모티콘", "")
            except ValueError:
                continue  # 날짜 형식이 맞지 않는 문서 무시
    except Exception as e:
        st.write("에러가 발생했습니다:", e)

    return st.session_state.emotion_data

# 캐시에서 특정 달의 감정 데이터를 가져오거나, 없으면 Firestore에서 불러오는 함수
def get_emotions_for_month(year, month):
    cache_key = f"{year}-{month:02}"
    if cache_key not in st.session_state.emotion_cache:
        # 해당 달 데이터가 캐시에 없으면 Firestore에서 불러와서 캐시에 저장
        st.session_state.emotion_cache[cache_key] = fetch_emotions_for_month(year, month)
    return st.session_state.emotion_cache[cache_key]

# 달력 출력 함수
def display_calendar(month, year):
    if "emotion_cache" not in st.session_state:
        st.session_state.emotion_cache = {}

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("< 이전달"):
            st.session_state.current_month, st.session_state.current_year = move_month(month, year, "previous")
    with col2:
        st.write(f"### {year}년 {month}월")
    with col3:
        if st.button("다음달 >"):
            st.session_state.current_month, st.session_state.current_year = move_month(month, year, "next")

    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day in enumerate(days_of_week):
        cols[i].write(f"**{day}**")

    cal = calendar.monthcalendar(year, month)
    st.session_state.emotion_data = get_emotions_for_month(year, month)

    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write(" ")
            else:
                date_str = f"{year}-{month:02}-{day:02}"
                icon = st.session_state.emotion_data.get(date_str, "")
                if cols[i].button(f"{day}{icon}"):
                    st.session_state.selected_date = date_str

    return st.session_state.selected_date

# 달 이동 함수
def move_month(month, year, direction):
    if direction == "previous":
        if month == 1:
            return 12, year - 1
        else:
            return month - 1, year
    elif direction == "next":
        if month == 12:
            return 1, year + 1
        else:
            return month + 1, year

# 감정 분석한 내용 데이터베이스에 저장
import re

def parse_response(response, date, uemail):
    # 각 감정 요소에 대한 정규 표현식 패턴
    # 평가 부분을 추가하여, 해당 부분을 추출할 수 있도록 수정
    pattern = r"대표 감정 : (.+?)\n감정 수치 : (\d)\n(?:근거 문장\d : \"(.+?)\"\n?)+평가 : \"(.+?)\""
    
    emotions = {
        '기쁨': '😁',
        '슬픔': '😭',
        '분노': '😠',
        '공포': '😨',
        '기대': '😆',
        '놀람': '😮',
        '신뢰': '🥰',
        '혐오': '🤬'
    }
    
    match = re.search(pattern, response, re.DOTALL)
    if match:
        # 기본 데이터 추출
        parsed_data = {
            "대표 감정": match.group(1),
            "이모티콘" : emotions[match.group(1)],
            "감정 수치": int(match.group(2)),  # 수치는 정수형으로 변환
            "근거 문장": [],  # 근거 문장을 담을 리스트
            "평가": match.group(4)  # 평가 항목을 추가
        }

        # 근거 문장을 찾기 위한 추가 패턴
        reason_pattern = r"근거 문장\d : \"(.+?)\""
        reasons = re.findall(reason_pattern, response)
        
        # 근거 문장을 리스트에 추가
        parsed_data["근거 문장"].extend(reasons)

        # Firestore에 저장
        doc_ref = st.session_state.db.collection('users').document(uemail).collection('emotions').document(date)
        # 파싱된 데이터를 Firestore에 저장
        doc_ref.set(parsed_data)

        return parsed_data
    
def analyze_emotion(text, date):
    openai_api_key = OPEN_API_KEY

    # 플루치크의 감정의 바퀴의 기본감정

    prompt = f"""
    문장을 분석하여 감정과 감정 수치를 추출하고, 근거 문장을 5개 이내로 찾아주세요.
    감정은 기쁨과 슬픔, 분노와 공포, 기대와 놀람, 신뢰와 혐오가 있습니다.
    입력된 문장: "{text}"

    답변은 다음 형식으로 해주세요:
    대표 감정 : [감정]
    감정 수치 : [1-10]
    근거 문장1 : "[문장1]"
    근거 문장2 : "[문장2]"
    근거 문장3 : "[문장3]"
    평가 : "[평가]"
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        api_key=openai_api_key
    )
    st.write(response['choices'][0]['message']['content'])
    parse_response(response['choices'][0]['message']['content'], date)
    # return response['choices'][0]['message']['content']


# 일기 작성 폼 함수
def diary_popup(selected_date):
    # 날짜가 선택된 경우
    if selected_date:
        date = selected_date
        
        # Form 사용
        with st.form(key='diary_form', clear_on_submit=True):
            # 날짜와 내용을 위한 열 레이아웃 설정
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"##### {date}")            
            # 폼 내에서 저장 버튼 추가
            with col2:
                submit_button = st.form_submit_button(label="저장")

            doc_ref = st.session_state.db.collection('users').document(uemail).collection('diaries').document(date)
            doc = doc_ref.get()

            if doc.exists:
                st.write("있음")
                # 문서 데이터가 있으면 출력
                diary_data = doc.to_dict()
                st.text_area(label="일기 내용", value=diary_data['content'])
                
                # 이미지 URL이 있으면 표시
                if diary_data.get('image'):
                    st.image(diary_data['image'], caption="업로드된 이미지")
                else:
                    st.write("이미지가 없습니다.")
                    
                st.write("작성 시간:", diary_data.get('timestamp', '시간 정보 없음'))
            else:
                st.write("없음")
                # 내용 입력
                content = st.text_area("내용", height=100)
                # 이미지 업로드
                uploaded_image = st.file_uploader("이미지 삽입", type=["png", "jpg", "jpeg"])

                # 폼 제출 버튼이 눌린 경우
                if submit_button:
                    if content:
                        st.session_state.alert_message = "일기가 성공적으로 저장되었습니다!"

                        # 사용자 이메일 가져오기
                        
                        image_url = None

                        # 이미지가 업로드된 경우 Firebase Storage에 저장
                        if uploaded_image:
                            bucket = storage.bucket(st.session_state.firebase_credentials['storageBucket'])

                            # 고유한 파일 이름 생성 (사용자 이메일 + 날짜)
                            image_filename = f"{uemail}_{date}_{uploaded_image.name}"
                            blob = bucket.blob(image_filename)
                            blob.upload_from_file(uploaded_image, content_type=uploaded_image.type)
                            blob.make_public()
                            image_url = blob.public_url

                        # Firestore에 일기 저장
                        doc_ref.set({
                            "content": content,
                            "image": image_url if uploaded_image else None,
                            'timestamp': firestore.SERVER_TIMESTAMP
                        })
                        # 성공 메시지 출력
                        st.success("일기가 저장되었습니다.")
                        st.write("openai에게 전달")
                        analyze_emotion(content, date)
                        st.write("openai에게 전달")
                    else:
                        st.session_state.alert_message = "내용을 입력해 주세요."

# 년도 선택 박스 함수
def year_selector():
    selected_year = st.selectbox("년도 선택", range(2020, 2026), index=st.session_state.current_year - 2020)
    return selected_year

try:
    # Streamlit 레이아웃 설정
    st.title("달력과 일기 작성")
    st.write(st.session_state.decoded_token['email'])

    # 초기 레이아웃 설정
    if st.session_state.selected_date is None:
        dcol1, dcol2, dcol3 = st.columns([2, 0.2, 1])
        st.session_state.current_year = year_selector()  # 년도 선택
        display_calendar(st.session_state.current_month, st.session_state.current_year)
    else:
        dcol1, dcol2 = st.columns([2, 1])  # 두 개의 열
        with dcol1:
            display_calendar(st.session_state.current_month, st.session_state.current_year)
        with dcol2:
            diary_popup(st.session_state.selected_date)

    # 알림 메시지 표시
    if st.session_state.alert_message:
        st.success(st.session_state.alert_message)
        st.session_state.alert_message = ""  # 메시지를 표시한 후 초기화
except Exception as e:
    st.write("로그인을 하세요.")
    diary.login_page()
    st.write(st.session_state.alert_message)
    st.write(e)