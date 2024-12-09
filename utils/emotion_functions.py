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

# 감정 분석을 위한 패턴 정의
EMOTIONS = {
    '기쁨': '😁', '슬픔': '😭', '분노': '😠', '공포': '😨',
    '기대': '😆', '놀람': '😮', '신뢰': '🥰', '혐오': '🤬'
}
PATTERN = r"대표 감정\s*:\s*(.+?)\s*감정 수치\s*:\s*(\d+)\s*((?:근거 문장\d\s*:\s*\"(.+?)\"\s*)+)\s*답장\s*:\s*\"(.+?)\""

def parse_response(response, date, uemail):
    st.session_state.alert_message = "감정 분석 시작"
    match = re.search(PATTERN, response, re.DOTALL)
    if match:
        emotion, emotion_score = match.group(1), int(match.group(2))
        reasons = re.findall(r"근거 문장\d+: \"(.+?)\"", match.group(3))
        reply = match.group(5)
        
        # Firestore에 저장할 데이터
        parsed_data = {
            "대표 감정": emotion,
            "이모티콘": EMOTIONS.get(emotion, "❓"),
            "감정 수치": emotion_score,
            "근거 문장": reasons,
            "답장": reply
        }
        st.session_state.alert_message = f"{emotion} 저장 완료"
        
        # 감정 데이터를 Firestore에 저장
        doc_ref = st.session_state.db.collection('users').document(uemail).collection('emotions').document(date)
        doc_ref.set(parsed_data)

        # 추천 및 저장
        recommend_and_save_solution(uemail, date, emotion, emotion_score)

def analyze_emotion(text, date):
    openai_api_key = st.secrets['open_api_key']
    prompt = f"""
    문장을 분석하여 대표 감정과 감정 수치를 추출하고, 근거 문장을 5개 이내로 찾아줘.  
    대표 감정은 반드시 **아래 8개 감정 중 하나만 선택**해줘. 8개 외의 다른 감정(예: 불안, 우울, 질투 등)은 절대 사용하지 말고, 가장 가까운 감정을 선택해줘.      
    **기쁨, 슬픔, 분노, 공포, 기대, 놀람, 신뢰, 혐오**
    답장은 상담사가 얘기하듯이 공감과 위로의 3문장이야.
    입력된 문장: "{text}"
    답변은 다음 형식으로 해줘:
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
        st.session_state.alert_message = "감정 분석 완료"
        parse_response(response['choices'][0]['message']['content'], date, st.session_state.decoded_token['email'])
    except Exception as e:
        st.error("분석을 실패했습니다.")
        st.session_state.db.collection('users').document(st.session_state.decoded_token['email']).collection('diaries').document(date).delete()
        st.session_state.emotion_data[date] = ""

def load_emotion_data(start_date, end_date):
    # 날짜 필터링 및 감정 데이터 불러오기
    start_date_str, end_date_str = start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    emotions_ref = st.session_state.db.collection('users').document(st.session_state.decoded_token['email']).collection('emotions')
    docs = emotions_ref.stream()
    emotion_counts = {emoji: 0 for emoji in EMOTIONS.values()}
    
    for emotion in docs:
        doc_id = emotion.id
        if start_date_str <= doc_id <= end_date_str:
            emotion_data = emotion.to_dict()
            emoji = emotion_data.get('이모티콘')
            if emoji in emotion_counts:
                emotion_counts[emoji] += 1
    
    return emotion_counts

def plot_emotion_data(start_date, end_date):
    emotion_counts = load_emotion_data(start_date, end_date)
    total = sum(emotion_counts.values())
    if total == 0:
        st.warning("감정 데이터가 없습니다.")
        return
    
    # 감정별 백분율 계산
    emotion_percentage = {key: (value / total) * 100 for key, value in emotion_counts.items() if value > 0}
    
    # 그래프 생성
    fig1, fig2 = create_graphs(emotion_counts, emotion_percentage)
    
    # 1:2 비율의 컬럼 레이아웃 설정
    col1, col2 = st.columns([1, 2], gap="small")
    
    # 도넛차트
    with col1:
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    
    # 막대그래프
    with col2:
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

def create_graphs(emotion_counts, emotion_percentage):
    # 감정별 색상 설정
    emotion_colors = {key: color for key, color in zip(EMOTIONS.values(), ['#FFEB99', '#A8D5E2', '#FFADAD', '#D3D3D3', '#FFD9B3', '#CBAACB', '#B5EAD7', '#E4C1F9'])}

    # 도넛차트 생성
    fig1 = go.Figure(go.Pie(
        labels=list(emotion_percentage.keys()),
        values=list(emotion_percentage.values()),
        hole=0.4,
        textinfo="label+percent",
        hoverinfo="label+percent",
        marker=dict(colors=[emotion_colors[emotion] for emotion in emotion_percentage.keys()])
    ))
    fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0), template="plotly_white", height=150, showlegend=False)

    # 막대그래프 생성
    sorted_emotion_counts = dict(sorted(emotion_counts.items(), key=lambda item: item[1], reverse=False))
    colors = [emotion_colors[emotion] for emotion in sorted_emotion_counts.keys()]
    fig2 = go.Figure(go.Bar(
        y=list(sorted_emotion_counts.keys()),
        x=list(sorted_emotion_counts.values()),
        orientation='h',
        marker=dict(color=colors),
    ))
    fig2.update_layout(template="plotly_white", margin=dict(t=10, b=20, l=10, r=10), height=338, showlegend=False, dragmode=False, yaxis=dict(tickfont=dict(size=20)))
    
    return fig1, fig2
