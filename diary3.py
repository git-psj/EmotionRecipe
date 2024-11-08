import streamlit as st
from datetime import datetime, timedelta
from urllib.parse import urlencode


def showDiaries(start_date, end_date):
    # 시작 날짜와 종료 날짜를 문자열 형식으로 변환
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Firestore에서 문서 이름(ID)이 날짜인 일기 데이터 불러오기
    uemail = "a@a.com"  # 사용자 이메일 (적절히 수정 필요)
    diaries_ref = st.session_state.db.collection('users').document(uemail).collection('diaries')
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
            query_params = urlencode({"id": doc_id})
            detail_page_url = f"/diary_detail?id={query_params}"

            # 카드 형태로 일기 표시
            with cols[i % 3]:  # 3열 중 하나에 배치
                st.markdown(
                    f"""
                    <a href="{detail_page_url}" style="text-decoration: none;">
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

# 보기 옵션을 탭으로 구성
tab1, tab2, tab3 = st.tabs(["주간 보기", "월별 보기", "연도별 보기"])

# 현재 날짜 기준으로 필터링 범위 설정
today = datetime.now()

# 각 탭에 맞는 날짜 범위 설정
with tab1:
    start_date = today - timedelta(days=today.weekday())  # 주간 시작일
    end_date = start_date + timedelta(days=6)             # 주간 종료일
    st.write("### 주간 보기")
    showDiaries(start_date, end_date)
with tab2:
    start_date = today.replace(day=1)                     # 월간 시작일
    end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)  # 월간 종료일
    st.write("### 월별 보기")
    showDiaries(start_date, end_date)
with tab3:
    start_date = today.replace(month=1, day=1)            # 연도 시작일
    end_date = today.replace(month=12, day=31)            # 연도 종료일
    st.write("### 연도별 보기")
    showDiaries(start_date, end_date)
