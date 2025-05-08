import streamlit as st
import uuid
import urllib3

from myApp import controller
from utils import auth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if "code_verifier" not in controller.getAll():
    controller.set("code_verifier", auth.generate_code_verifier())

if "auth_state" not in st.session_state:
    st.session_state["auth_state"] = uuid.uuid4().hex

code_verifier = controller.get("code_verifier")
visitor_token = auth.get_visitor_token()
code_challenge = auth.generate_code_challenge(code_verifier)
state = st.session_state["auth_state"]
login_url = auth.get_auth_url(visitor_token, code_challenge, state)

st.link_button("Login With Specta Collab", login_url)

auth_code, state = auth.get_query_params()

if auth_code is not None and state is not None:
    st.query_params.clear()
    member_token = auth.get_member_token(auth_code, code_verifier)    
    st.session_state.member_info = auth.get_member_info(member_token)

    if st.session_state.member_info["member"]["status"] == "APPROVED":
        st.session_state.logged_in = True
        st.rerun()
    else:
        st.warning("Uh oh! You do not have premission to enter this site.")    

