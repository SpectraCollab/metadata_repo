import streamlit as st
import utils.streamlit_utils as stutil
import pandas as pd

stutil.print_states()
st.header("Your Profile")

active_user = st.session_state.member_info

st.markdown(f"""
    **Member Name**: {active_user['member']['contact']['firstName']} {active_user['member']['contact']['lastName']}\n
    **Email**: {active_user['member']['loginEmail']}\n
    **Member Status**: {active_user['member']['status']}""")