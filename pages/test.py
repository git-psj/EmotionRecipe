import streamlit as st
from utils.solution_functions import get_activity_details

activities_ref = st.session_state.db.collection('activities')
st.write(activities_ref)
st.write("---")
activity = get_activity_details("취미 활동하기")
st.write(activity)
