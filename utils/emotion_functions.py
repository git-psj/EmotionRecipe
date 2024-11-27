import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from datetime import datetime
import requests
import calendar
import openai
import re
import plotly.graph_objects as go
from utils.solution_functions import recommend_and_save_solution

# parse_response, analyze_emotion, load_emotion_data, plot_emotion_data
#  parse_response(response, date, uemail), analyze_emotion(text, date), load_emotion_data(start_date, end_date),plot_emotion_data(start_date, end_date)

def parse_response(response, date, uemail):
    st.session_state.alert_message = f"감정 분석 시작"
    # 각 감정 요소에 대한 정규 표현식 패턴
    # 평가 부분을 추가하여, 해당 부분을 추출할 수 있도록 수정
   # 감정 분석을 위한 패턴 정의
    pattern = r"대표 감정\s*:\s*(.+?)\s*감정 수치\s*:\s*(\d+)\s*((?:근거 문장\d\s*:\s*\"(.+?)\"\s*)+)\s*답장\s*:\s*\"(.+?)\""
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
        emotion = match.group(1)
        emotion_score = int(match.group(2))
        reasons = re.findall(r"근거 문장\d+: \"(.+?)\"", match.group(3))
        reply = match.group(5)

        # 파싱된 데이터 구조
        parsed_data = {
            "대표 감정": emotion,
            "이모티콘": emotions.get(emotion, "❓"),  # 감정에 해당하는 이모티콘
            "감정 수치": emotion_score,
            "근거 문장1": reasons[0] if len(reasons) > 0 else "",
            "근거 문장2": reasons[1] if len(reasons) > 1 else "",
            "근거 문장3": reasons[2] if len(reasons) > 2 else "",
            "답장": reply
        }
        st.session_state.emotion_data[date] = emotions[match.group(1)]
        
        # 근거 문장을 찾기 위한 추가 패턴
        reason_pattern = r"근거 문장\d : \"(.+?)\""
        reasons = re.findall(reason_pattern, response)
        
        # 근거 문장을 리스트에 추가
        parsed_data["근거 문장"].extend(reasons)

        # Firestore에 저장
        doc_ref = st.session_state.db.collection('users').document(uemail).collection('emotions').document(date)
        st.session_state.alert_message = "감정 저장 완료"
        # st.write(match.group(1))
        # 파싱된 데이터를 Firestore에 저장
        doc_ref.set(parsed_data)
        recommend_and_save_solution(st.session_state.decoded_token['email'], date, match.group(1), int(match.group(2)))
    
def analyze_emotion(text, date):
    openai_api_key = st.secrets['open_api_key']
  
    # 플루치크의 감정의 바퀴의 기본감정
    prompt = f"""
    문장을 분석하여 대표 감정과 감정 수치를 추출하고, 근거 문장을 5개 이내로 찾아줘.
    감정은 기쁨, 슬픔, 분노, 공포, 기대, 놀람, 신뢰, 혐오이 있고 이 외의 감정은 고려하지 마.
    답장은 상담사가 얘기하듯이 공감과 위로의 3문장이야.
    입력된 문장: "{text}"

    답변은 다음 형식으로 해주세요:
    대표 감정 : [감정]
    감정 수치 : [1-10]
    근거 문장1 : "[문장1]"
    근거 문장2 : "[문장2]"
    근거 문장3 : "[문장3]"
    답장 : "[답장]"
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            api_key=openai_api_key
        )
        st.session_state.alert_message = f"감정 분석 완료"
        st.write(response['choices'][0]['message']['content'])
        with st.spinner("감정 데이터 저장 중..."):
            parse_response(response['choices'][0]['message']['content'], date, st.session_state.decoded_token['email'])
    except Exception as e:
        st.error("분석을 실패했습니다.")
        st.session_state.db.collection('users').document(st.session_state.decoded_token['email']).collection('diaries').document(date).delete()
        st.session_state.emotion_data[date] = ""
        return


# 감정 데이터를 불러오는 함수
def load_emotion_data(start_date, end_date):
    # 시작 날짜와 종료 날짜를 문자열 형식으로 변환
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Firestore에서 문서 이름(ID)이 날짜인 일기 데이터 불러오기
    emotions_ref = st.session_state.db.collection('users').document(st.session_state.decoded_token['email']).collection('emotions')
    docs = emotions_ref.stream()
    emotion_counts = {'😁': 0, '😭': 0, '😠': 0, '😨': 0, '😆': 0, '😮': 0, '🥰': 0, '🤬': 0}
    
    for emotion in docs:
        diary = emotion.to_dict()
        doc_id = emotion.id  # 문서 ID를 날짜로 사용
        
        # 날짜 필터링 (for문 내에서 비교)
        if start_date_str <= doc_id <= end_date_str:
            emotion_data = emotion.to_dict()
            emoji = emotion_data.get('이모티콘')
            if emoji in emotion_counts:
                emotion_counts[emoji] += 1
    
    return emotion_counts

# 그래프를 시각화하는 함수
def plot_emotion_data(start_date, end_date):
    emotion_names = {
        '😁': '기쁨',
        '😭': '슬픔',
        '😠': '분노',
        '😨': '공포',
        '😆': '기대',
        '😮': '놀람',
        '🥰': '신뢰',
        '🤬': '혐오'
    }   
    emotion_counts = load_emotion_data(start_date, end_date)

    total = sum(emotion_counts.values())
    if total == 0:
        st.warning("감정 데이터가 없습니다.")
        return
    
    # 감정별 백분율 계산
    emotion_percentage = {key: (value / total) * 100 for key, value in emotion_counts.items() if value > 0}
    emotion_colors = {
        '😁': '#FFEB99',  # 파스텔 노랑
        '😭': '#A8D5E2',  # 파스텔 블루
        '😠': '#FFADAD',  # 파스텔 레드
        '😨': '#D3D3D3',  # 파스텔 그레이
        '😆': '#FFD9B3',  # 파스텔 오렌지
        '😮': '#CBAACB',  # 파스텔 퍼플
        '🥰': '#B5EAD7',  # 파스텔 그린
        '🤬': '#E4C1F9',  # 파스텔 브라운
    }

    # 도넛차트 생성
    fig1 = go.Figure(go.Pie(
        labels=list(emotion_percentage.keys()),
        values=list(emotion_percentage.values()),
        hole=0.4,
        textinfo="label+percent",
        hoverinfo="label+percent",
        marker=dict(colors=[emotion_colors[emotion] for emotion in emotion_percentage.keys()])
    ))
    fig1.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        template="plotly_white",
        height=150,
        showlegend=False
    )

    # 막대그래프 생성
    sorted_emotion_counts = dict(sorted(emotion_counts.items(), key=lambda item: item[1], reverse=False))
    colors = [emotion_colors[emotion] for emotion in sorted_emotion_counts.keys()]

    fig2 = go.Figure(go.Bar(
        y=list(sorted_emotion_counts.keys()),
        x=list(sorted_emotion_counts.values()),
        orientation='h',
        marker=dict(color=colors),
    ))
    fig2.update_layout(
        template="plotly_white",
        margin=dict(t=10, b=20, l=10, r=10),
        height=338,
        showlegend=False,
        dragmode=False,  # 확대/축소 비활성화
        yaxis=dict(tickfont=dict(size=20))  # y축 (감정) 글씨 크기 조정
    )

    # 1:2 비율의 컬럼 레이아웃 설정
    
    col1, col2 = st.columns([1, 2], gap="small")

    # 도넛차트
    with col1:
        with st.container(height=370, border=True):
            # 도넛차트 표시
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
            
            # 도넛차트 아래에 이모티콘과 색상 정보를 flexbox로 표시
            st.markdown(
                """
                <div style="display: flex; flex-wrap: wrap; gap: 5px; justify-content: center;">
                    {}
                </div>
                """.format( 
                    "".join([
                        f'<div style="background-color: {color}; color: {"white" if color != "yellow" else "black"}; padding: 5px; border-radius: 5px; width: 45%; text-align: center;">{emoji} {name}</div>'
                        for emoji, name in emotion_names.items() for color in [emotion_colors[emoji]]
                    ])
                ), unsafe_allow_html=True)



    # 막대그래프
    with col2:
        with st.container(height=370, border=True):
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
