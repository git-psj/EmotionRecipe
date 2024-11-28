import streamlit as st
from utils.solution_functions import get_activity_details

# activities_ref = st.session_state.db.collection('activities').stream()
# st.write(activities_ref)
# st.write("---")
# activity = get_activity_details("취미 활동하기")
# st.write(activity)
docs = st.session_state.db.collection('activities').stream()
for doc in docs:
    st.write(f"{doc.id} => {doc.to_dict()}")

st.write("---")

docs = st.session_state.db.collection('activitiesDetail').stream()
for doc in docs:
    st.write(f"{doc.id} =>")

st.write("---")

docs = st.session_state.db.collection('activitiesDetail').document("취미 활동하기").collection("sub_activities").stream()
for doc in docs:
    st.write(f"{doc.id} => s{doc.to_dict()}")
