import streamlit as st
import utils.streamlit_utils as stutil
import utils.auth as auth

stutil.print_states()
st.header("Your Profile")

active_user = st.session_state.member_info
try:
    institution = st.session_state.member_cms["dataItems"][0]["data"]["universityInstitution"]
except:
    institution = None
    md = """Please add a University/Institution to your profile here: [Update Profile](https://www.spectra-collab.org/members/update)"""
    st.warning(md)

try:
    position = st.session_state.member_cms["dataItems"][0]["data"]["position"]
except:
    position = None

st.markdown(f"""
    **Member Name**: {active_user['member']['contact']['firstName']} {active_user['member']['contact']['lastName']}\n
    **Email**: {active_user['member']['loginEmail']}\n
    **Member Status**: {active_user['member']['status']}\n
    **Institution**: {institution}\n
    **Position**: {position}""")