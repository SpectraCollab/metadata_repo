import streamlit as st
import uuid
import urllib3
import base64
import time

from myApp import controller
from utils import auth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
if "code_verifier" not in controller.getAll():
    controller.set("code_verifier", auth.generate_code_verifier())
    time.sleep(5)

if "auth_state" not in st.session_state:
    st.session_state["auth_state"] = uuid.uuid4().hex

login_image = get_base64_image("assets/login.png")

code_verifier = controller.get("code_verifier")
visitor_token = auth.get_visitor_token()
code_challenge = auth.generate_code_challenge(code_verifier)
state = st.session_state["auth_state"]
login_url = auth.get_auth_url(visitor_token, code_challenge, state)

st.header("Welcome to the SPECTRA Image Metadata Repository")
st.write("The SPECTRA repository is web app designed to enable researchers to share image metadata accross multiple studies relating to arthritis research. The intent of this repository is to promote collaboration and encourage researchers to connect with each other if they find image metadata from another institution which may be useful to their research.")

info_md = """
To access the repository, you must currently be registered as a SPECTRA member. If you are not registered, go to [spectra-collab.org](https://www.spectra-collab.org/) to create an account. If you are already a member, login using the button below.

Please refer to the [Usage Instructions and FAQ Powerpoint](https://docs.google.com/presentation/d/1BybJdAy9LMRceH0rDgo4Mpslq9Jl4nNr/edit?usp=drive_link&ouid=100577848524603341913&rtpof=true&sd=true) before using the site.
"""
st.write(info_md)
html = f"""
<a href="{login_url}">
    <img src="data:image/png;base64,{login_image}" width="300">
</a>
"""
st.markdown(html, unsafe_allow_html=True)

auth_code, state = auth.get_query_params()

if auth_code is not None and state is not None:
    st.query_params.clear()
    st.session_state.member_token = auth.get_member_token(auth_code, code_verifier)    
    st.session_state.member_info = auth.get_member_info(st.session_state.member_token)
    
    if st.session_state.member_info["member"]["status"] == "APPROVED":
        st.session_state.member_cms = auth.get_member_cms_info(st.session_state.member_token, st.session_state.member_info["member"]["id"])
        st.session_state.logged_in = True
        st.rerun()
    else:
        st.warning("Uh oh! You do not have premission to enter this site.")    