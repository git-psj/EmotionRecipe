import streamlit as st
from utils.soultion_functions import get_activity_details


activity = get_activity_details(취미 활동하기)
st.write(activity)
