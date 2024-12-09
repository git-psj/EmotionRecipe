import streamlit as st
from utils.solution_functions import get_activity_details, display_content
from datetime import datetime, timedelta


# 날짜 선택 위젯
selected_date = st.date_input("날짜 선택", value=datetime.today())

# 이전/다음 날짜 버튼
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("이전"):
        selected_date -= timedelta(days=1)
with col2:
    if st.button("다음"):
        selected_date += timedelta(days=1)

# 선택된 날짜 표시
st.write(f"선택된 날짜: {selected_date.strftime('%Y-%m-%d')}")



# activities_ref = st.session_state.db.collection('activities').stream()
# st.write(activities_ref)
# st.write("---")
activity = get_activity_details("취미 활동하기")
st.write("결과다")
st.write(activity)


activity = get_activity_details("책 읽기")
st.write("결과다")
st.write(activity)

url = "https://poki.com/kr/g/sudoku"
display_content(url)
st.video(url)

# docs = st.session_state.db.collection('activities').stream()
# for doc in docs:
#     st.write(f"{doc.id} => {doc.to_dict()}")

# st.write("---")

# docs = st.session_state.db.collection('activitiesDetail').stream()
# for doc in docs:
#     st.write(f"{doc.id} =>")

# st.write("---")

# docs = st.session_state.db.collection('activitiesDetail').document("취미활동하기").collection("sub_activities").stream()
# for doc in docs:
#     st.write(f"{doc.id} => s{doc.to_dict()}")

# st.write("---")
# docs = st.session_state.db.collection('activitiesDetail').stream()

# # 각 문서의 ID 출력
# for doc in docs:
#     st.write(f"문서 ID: {doc.id}")
