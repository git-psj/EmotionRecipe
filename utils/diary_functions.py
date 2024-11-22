import streamlit as st
from firebase_admin import credentials, auth, firestore, storage
from datetime import datetime
import calendar
import streamlit as st
from datetime import datetime
from urllib.parse import urlencode
from .emotion_functions import analyze_emotion

# fetch_emotions_for_month, get_emotions_for_month, display_calendar, move_month, year_selector, diary_popup, diary_page, showDiaries

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
        docs = st.session_state.db.collection('users').document(st.session_state.decoded_token['email']).collection('emotions').stream()
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


# 달력 출력 함수
def display_calendar(month, year):
    if "emotion_cache" not in st.session_state:
        st.session_state.emotion_cache = {}

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("< 이전달"):
            st.session_state.current_month, st.session_state.current_year = move_month(month, year, "previous")
            # 즉시 상태 업데이트
            st.rerun()
    with col2:
        st.markdown(f"<h3 style='text-align: center;'>{year}년 {month}월</h3>", unsafe_allow_html=True)
    with col3:
        if st.button("다음달 >"):
            st.session_state.current_month, st.session_state.current_year = move_month(month, year, "next")
            st.rerun()

    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day in enumerate(days_of_week):
        cols[i].write(f"**{day}**")
    cal = calendar.monthcalendar(year, month)
    get_emotions_for_month(year, month)


    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write(" ")
            else:
                date_str = f"{year}-{month:02}-{day:02}"
                icon = st.session_state.emotion_data.get(date_str, "")
                
                if cols[i].button(f"{day}\n{icon}", key=day):
                    if st.session_state.selected_date == date_str:
                        st.session_state.selected_date = None  # 날짜 선택 초기화
                    else:
                        st.session_state.selected_date = date_str
                    st.rerun()


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

# 년도 선택 박스 함수
def year_selector():
    selected_year = st.selectbox("년도 ", range(2020, 2026), index=st.session_state.current_year - 2020)
    return selected_year

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
            
            with col2:
                diary_ref = st.session_state.db.collection('users').document(user_email).collection('diaries')
                diary_doc = diary_ref.document(date).get()
    
                if diary_doc.exists:
                    submit_button = st.form_submit_button(label="삭제")
                    
                    # 문서 데이터가 있으면 출력
                    diary_data = doc.to_dict()
                    st.text_area(label="일기 내용", value=diary_data['content'])
                    
                    # 이미지 URL이 있으면 표시
                    if diary_data.get('image'):
                        st.image(diary_data['image'], caption="업로드된 이미지")
                    else:
                        st.write("이미지가 없습니다.")
                        
                    st.write("작성 시간:", diary_data.get('timestamp', '시간 정보 없음'))
                    if submit_button:
                        # 일기 삭제
                        diary_ref = st.session_state.db.collection('users').document(st.session_state.decoded_token['email']).collection('diaries')
                        diary_ref.document(st.session_state.selected_date).delete()
                        st.success("일기가 삭제되었습니다.")
                        st.session_state.selected_date = None  # 삭제 후 날짜 초기화
                else:
                    submit_button = st.form_submit_button(label="저장")
                    # 내용 입력
                    content = st.text_area("내용", height=100)
                    # 이미지 업로드
                    uploaded_image = st.file_uploader("이미지 삽입", type=["png", "jpg", "jpeg"])
                
                    css = '''
                    <style>
                        [data-testid='stFileUploader'] {
                            width: max-content;
                        }
                        [data-testid='stFileUploader'] section {
                            padding: 0;
                            float: left;
                        }
                        [data-testid='stFileUploader'] section > input + div {
                            display: none;
                        }
                        [data-testid='stFileUploader'] section + div {
                            float: right;
                            padding-top: 0;
                        }
                        .stButton>button {
                            white-space: nowrap;  /* 줄바꿈 방지 */
                        }
                    </style>
                    '''
                    st.markdown(css, unsafe_allow_html=True)
                    
                    # 업로드 결과 확인
                    if uploaded_image:
                        st.image(uploaded_image, caption="업로드된 이미지")
 
                    # 폼 제출 버튼이 눌린 경우
                    if submit_button:
                        if content:
                            
                            # 사용자 이메일 가져오기                        
                            image_url = None
    
                            # 이미지가 업로드된 경우 Firebase Storage에 저장
                            if uploaded_image:
                                bucket = storage.bucket(st.session_state.firebase_credentials['storageBucket'])
    
                                # 고유한 파일 이름 생성 (사용자 이메일 + 날짜)
                                image_filename = f"{st.session_state.decoded_token['email']}_{date}_{uploaded_image.name}"
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
                            st.session_state.alert_message = "일기가 성공적으로 저장되었습니다!"
                            with st.spinner("감정 분석 중..."):
                                analyze_emotion(content, date)
                        else:
                            st.session_state.alert_message = "내용을 입력해 주세요."

# 일기 작성 페이지
def diary_page():
    try:
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
        st.write(st.session_state.alert_message)
        st.write(e)

# 일기 상세보기 함수 (같은 페이지에서 표시)
def show_diary_detail(diary_id):
    diaries_ref = st.session_state.db.collection('users').document(st.session_state.decoded_token['email']).collection('diaries')
    diary_doc = diaries_ref.document(diary_id).get()
    if diary_doc.exists:
        diary = diary_doc.to_dict()
        st.write(f"### {diary_id}의 일기")
        st.write(f"**내용**: {diary.get('content', '내용없음')}")
        st.write(f"**작성 날짜**: {diary_id}")
        # 추가적인 일기 내용 (예: 감정, 이미지 등) 표시
        if 'emotion' in diary:
            st.write(f"**감정**: {diary['emotion']}")
    else:
        st.write("해당 날짜의 일기가 존재하지 않습니다.")

def showDiaries(start_date, end_date):
    # 시작 날짜와 종료 날짜를 문자열 형식으로 변환
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Firestore에서 문서 이름(ID)이 날짜인 일기 데이터 불러오기
    diaries_ref = st.session_state.db.collection('users').document(st.session_state.decoded_token['email']).collection('diaries')
    docs = diaries_ref.stream()

    # CSS 스타일 추가
    st.markdown("""
        <style>
        .diary-card {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 15px;
            width: 230px;            /* 카드 가로 크기 고정 */
            height: 200px;           /* 카드 세로 크기 고정 */
            overflow: hidden;        /* 내용이 넘칠 경우 숨김 */
            position: relative;
            background-color: white; /* 기본 배경색 */
            color: black;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .diary-header {
            display: flex;
            justify-content: space-between;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .diary-content {
            flex: 1;
            overflow-y: auto;       /* 스크롤 기능 추가 */
            font-size: 14px;
        }
        hr {
            margin: 5px 0;
            border: none;
            border-top: 1px solid #ccc;
        }
        </style>
        """, unsafe_allow_html=True)

    # 일기 데이터 카드로 표시
    st.write("### 일기 목록")
    cols = st.columns(3)  # 3개의 열로 배치
    i = 0

    for doc in docs:
        diary = doc.to_dict()
        doc_id = doc.id  # 문서 ID를 날짜로 사용
        
        # 날짜 필터링 (for문 내에서 비교)
        if start_date_str <= doc_id <= end_date_str:
            try:
                emotion = st.session_state.emotion_data[doc_id]
            except:
                emotion = ''
            content = diary.get('content', '내용없음')  # 내용 전체 표시

            # 일기 상세보기 페이지 링크 생성
            query_params = urlencode({"id": doc_id, "token": st.session_state.id_token})
            detail_page_url = f"/solution_page?{query_params}"

            # 카드 형태로 일기 표시
            with cols[i % 3]:  # 3열 중 하나에 배치
                st.markdown(
                    f"""
                    <a href="{detail_page_url}" target="_self" style="text-decoration: none;">
                    <div class="diary-card">
                        <div class="diary-header">
                            <span>{doc_id}</span>
                            <span>{emotion}</span>
                        </div>
                        <hr>
                        <div class="diary-content">
                            <p>{content}</p>
                        </div>
                    </div>
                    </a>
                    """,
                    unsafe_allow_html=True
                )
            i += 1

    # 일기가 없는 경우 메시지 표시
    if i == 0:
        st.write("해당 기간에는 작성된 일기가 없습니다.")

    if "selected_diary_id" in st.session_state:
        # 이미 선택된 일기가 있는 경우 해당 일기 표시
        show_diary_detail(st.session_state.selected_diary_id)
