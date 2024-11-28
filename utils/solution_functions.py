import random
import jwt
import streamlit as st
from datetime import datetime
from urllib.parse import urlencode

# recommend_activity(emotion, score), get_activity_details(recommended_activity), check_previous_solution(user_email, url), display_solution_page(), get_latest_diary_and_emotion(user_email), get_diary_and_emotion(date, user_email), recommend_and_save_solution(user_email, emotion, score), save_solution_to_db(user_email, emotion, score, recommended_activity, activity_detail)

# 감정과 점수에 맞는 랜덤 활동을 추천하는 함수
def recommend_activity(emotion, score):
    # 점수에 맞는 범위 설정
    if 1 <= score <= 4:
        score_range = "Low (1-4)"
    elif 5 <= score <= 7:
        score_range = "Medium (5-6)"
    elif 8 <= score <= 10:
        score_range = "High (7-10)"
    else:
        st.error("점수는 1에서 10 사이여야 합니다.")
        return None
    
    # Firestore에서 활동 데이터를 가져오기
    activities_ref = st.session_state.db.collection('activities')
    
    # 감정과 score_range에 맞는 활동을 필터링하여 목록을 가져옴
    activities_query = activities_ref.where("emotion", "==", emotion).where("score", "==", score_range).get()
    
    if not activities_query:
        return None
    
    # 활동 목록을 리스트로 변환하여 랜덤으로 하나 선택
    activities_list = [activity.to_dict()['activity'] for activity in activities_query]
    recommended_activity = random.choice(activities_list)
    return recommended_activity

# 활동에 대한 상세 정보를 랜덤으로 가져오는 함수
def get_activity_details(recommended_activity):
    st.write("상세정보")
    docs = st.session_state.db.collection('activitiesDetail').document(recommended_activity).collection("sub_activities").stream()
    for doc in docs:
        st.write(f"{doc.id} => s{doc.to_dict()}")

    sub_activities_docs = list(docs)

    # 하위 컬렉션이 비어 있는 경우 처리
    if not sub_activities_docs:
        print(f'"{recommended_activity}" 문서의 하위 컬렉션이 비어 있습니다.')
        return None

    activity_detail = random.choice(sub_activities_docs)
    st.write(activity_detail)
    return activity_detail

# 중복된 활동이 있는지 확인하는 함수
def check_previous_solution(user_email, url):
    solutions_ref = st.session_state.db.collection('users').document(user_email).collection('solutions')
    
    # 이전 솔루션에서 같은 활동이 있는지 확인 (문서 ID로 확인)
    existing_solutions_query = solutions_ref.where("url", "==", url).get()
    
    # 중복되는 활동이 있으면 True를 반환
    if existing_solutions_query:
        return True
    return False

# 추천된 활동을 사용자의 DB에 저장하는 함수
def save_solution_to_db(user_email, date, emotion, score, recommended_activity, activity_detail):
    solutions_ref = st.session_state.db.collection('users').document(user_email).collection('solutions').document(date)

    if activity_detail == '':
        sub_activity = ''
        tags = ''
        url = ''
    else:
        sub_activity = activity_detail.get('sub_activity')
        tags = activity_detail.get('tags')
        url = activity_detail.get('url')
    # 저장할 솔루션 데이터
    solution_data = {
        "recommended_activity": recommended_activity,
        "sub_activity": sub_activity,
        "tags": tags,
        "url": url,
    }
    
    # 솔루션 저장
    solutions_ref.set(solution_data)
    st.session_state.alert_message = "추천활동이 저장되었습니다."

    query_params = urlencode({"id": date, "token": st.session_state.id_token})
    detail_page_url = f"/solution_page?{query_params}"
    st.markdown(
        f"""
        <div style="text-align: center;">
            <a href="{detail_page_url}" target="_self">
                <button style="background-color: #eee; color: gray; border: 1px solid lightgray; border-radius: 10px; 
                margin: 20px auto; padding: 10px 20px; text-align: center;
                text-decoration: none; font-size: 15px; cursor: pointer;">
                    결과 조회하러가기
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# 감정과 점수에 맞는 활동을 추천하고 중복되지 않게 저장하는 함수
def recommend_and_save_solution(user_email, date, emotion, score):
    # 1. 활동 추천 (랜덤으로 선택)
    recommended_activity = recommend_activity(emotion, score)
    
    if recommended_activity:
        st.write(recommended_activity)
        # 3. 활동의 get_activity_details 정보 가져오기 (랜덤으로 선택)
        activity_detail = get_activity_details(recommended_activity)
        if activity_detail:
            url = activity_detail.get('url')
    
            if check_previous_solution(user_email, url):
                st.warning(f"이 활동({recommended_activity})은 이미 추천된 활동입니다. 다른 활동을 추천합니다.")
                activity_detail = get_activity_details(recommended_activity)
            else:
                save_solution_to_db(user_email, date, emotion, score, recommended_activity, activity_detail)
        else:
            save_solution_to_db(user_email, date, emotion, score, recommended_activity, '')

# 일기랑 감정 가져오기
@st.cache_data(ttl=60*10)
def get_diary_and_emotion(date, user_email):
    diaries_ref = st.session_state.db.collection('users').document(user_email).collection('diaries')
    emotion_ref = st.session_state.db.collection('users').document(user_email).collection('emotions')
    solution_ref = st.session_state.db.collection('users').document(user_email).collection('solutions')

    # 일기 데이터 가져오기
    diary_doc = diaries_ref.document(date).get()
    diary_data = diary_doc.to_dict() if diary_doc.exists else '내용없음'

    # 감정 데이터 가져오기
    emotion_doc = emotion_ref.document(date).get()
    emotion_data = emotion_doc.to_dict() if emotion_doc.exists else {'emotion': '내용없음', 'score': 0}

    # 솔루션 데이터 가져오기
    solution_doc = solution_ref.document(date).get()
    solution_data = solution_doc.to_dict() if diary_doc.exists else '내용없음'

    return diary_data, emotion_data, solution_data

# 최근날짜 검색 및 데이터 가져오기
def get_latest_diary_and_emotion(user_email):
    try:
        diaries_ref = st.session_state.db.collection('users').document(user_email).collection('diaries')
        
        # 모든 일기 문서 가져오기
        diary_docs = list(diaries_ref.stream())
        
        if not diary_docs:
            st.info("등록된 일기가 없습니다.")
            return None, '내용없음', {'emotion': '알 수 없음', 'score': 0}
        
        # 문서 ID(날짜) 기준으로 최신 일기 찾기
        latest_diary_doc = max(diary_docs, key=lambda doc: datetime.strptime(doc.id, '%Y-%m-%d'))
        latest_date = latest_diary_doc.id
        diary_data, emotion_data, solution_data = get_diary_and_emotion(latest_date, user_email)
        return latest_date, diary_data, emotion_data, solution_data
    
    except Exception as e:
        st.error("저장된 일기가 없습니다.")


#url 분석
def get_token_date():
    # URL에서 날짜 정보 가져오기
    date = st.query_params.get("id", None)
    # decoded_token에서 이메일 정보 가져오기
    token = st.query_params.get('token', None)
    return date, token

# 결과 보여주기
def display_content(url):
    if url.endswith(('.jpg', '.png', '.jpeg', '.gif', '.bmp', '.webp')):
        # 이미지 표시
        st.image(url, caption="이미지 콘텐츠")
    elif "youtube.com" in url or "youtu.be" in url:
        # YouTube 동영상 표시
        st.video(url)
    else:
        # 기타 링크 iframe 삽입
        iframe_code = f"""
        <iframe width="560" height="315" src="{url}" frameborder="0" 
        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen></iframe>
        """
        st.markdown(iframe_code, unsafe_allow_html=True)

# 솔루션 페이지 함수
def display_solution_page(date, token):
    st.title("감정 레시피")
    st.markdown("<h3 style='color: gray; margin-top: -10px;'>&nbsp;- 결과 확인하기</h3>", unsafe_allow_html=True)
    if token is None and date is None:
        try: # 솔루션 페이지를 눌렀을 때
            user_email = st.session_state.decoded_token['email']
            date, diary_data, emotion_data, solution_data = get_latest_diary_and_emotion(user_email)
        except:
            st.error("유효하지 않은 토큰입니다.")
    else:
        # URL에서 받은 토큰을 디코딩
        try:
            st.session_state.id_token = token
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            st.session_state.decoded_token = decoded_token
            user_email = st.session_state.decoded_token['email']            
            if not user_email:
                st.error("이메일 정보가 없습니다.")
        except jwt.ExpiredSignatureError:
            st.error("토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            st.error("유효하지 않은 토큰입니다.")

        # Firebase에서 데이터 가져오기
        diary_data, emotion_data, solution_data = get_diary_and_emotion(date, user_email)

    # 페이지 레이아웃 설정 (좌우 컬럼)
    col1, col2 = st.columns([1, 1])

    # 좌측: 일기 내용 표시
    with col1:
        st.subheader("📝 일기 내용")

        st.markdown(f"**날짜**: {date}")
        emotion_colors = emotion_colors = {
            '😁': '#FFEB99',  # 파스텔 노랑
            '😭': '#A8D5E2',  # 파스텔 블루
            '😠': '#FFADAD',  # 파스텔 레드
            '😨': '#D3D3D3',  # 파스텔 그레이
            '😆': '#FFD9B3',  # 파스텔 오렌지
            '😮': '#CBAACB',  # 파스텔 퍼플
            '🥰': '#B5EAD7',  # 파스텔 그린
            '🤬': '#E4C1F9',  # 파스텔 브라운
        } 
        emotion_colors['알 수 없음'] = 'gray'
        emotion = emotion_data.get("대표 감정", "알 수 없음")
        emoticon = emotion_data.get("이모티콘", "")
        highlighted_content = diary_data.get('content')
        keywords = emotion_data.get("근거 문장", "")
        for keyword in keywords:
            if keyword in highlighted_content:
                # 근거 문장에 <mark> 태그 추가
                highlighted_content = highlighted_content.replace(keyword, f"<span style='background-color: {emotion_colors[emoticon]}; padding: 0.2em;'>{keyword}</span>")

        st.markdown(highlighted_content, unsafe_allow_html=True)  # 일기 내용 표시 (수정 불가)
        if diary_data.get('image'):
            st.image(diary_data.get('image'))

    # 우측: 솔루션 표시
    with col2:
        st.subheader(f"{emoticon}\t{emotion}")
        st.write(emotion_data.get("평가", ""))
        try:
            st.write(f"## 🔍추천 활동")

            recommended_activity = solution_data.get("recommended_activity")
            sub_activity = solution_data.get("sub_activity")
            url = solution_data.get("url")
            # st.write(recommended_activity, sub_activity, url)
            if url != '' :
                if sub_activity != '':
                    st.write(f"{recommended_activity}")
                    display_content(url)
                else:
                    st.write(f"{recommended_activity} - {sub_activity}")
                    # URL이 YouTube 링크인지 확인
                    display_content(url)
            else:
                st.write(f"{recommended_activity}")
        except:
            st.info("해당 감정에 대한 솔루션이 없습니다.")
