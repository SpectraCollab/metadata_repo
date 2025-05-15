import streamlit as st
import utils.streamlit_utils as stutil
import utils.auth as auth

stutil.print_states()
st.header("Your Profile")

member_token = st.session_state.member_token
active_user = st.session_state.member_info
member_id = active_user["member"]["id"]

member_cms = auth.get_member_cms_info(member_token, member_id)

institution = member_cms["dataItems"][0]["data"]["universityInstitution"]
position = member_cms["dataItems"][0]["data"]["position"]

st.markdown(f"""
    **Member Name**: {active_user['member']['contact']['firstName']} {active_user['member']['contact']['lastName']}\n
    **Email**: {active_user['member']['loginEmail']}\n
    **Member Status**: {active_user['member']['status']}\n
    **Institution**: {institution}\n
    **Position**: {position}""")