# ----------------------------------------------------------------
# myApp.py 
#
# Created by: Chris Brunet
# Created on: June 14, 2024
#
# Description: Streamlit web app for Spectra image metadata repository. 
#
# Usage: 
#     1. Follow instructions in readme.md
#     2. Run command 'streamlit run myApp.py'
# ----------------------------------------------------------------

import streamlit as st
import time
from streamlit_cookies_controller import CookieController

## SESSION STATES ##
if 'add_to_db_button' not in st.session_state:
    st.session_state.add_to_db_button = False
if 'keep' not in st.session_state:
    st.session_state.keep = False
if 'overwrite' not in st.session_state:
    st.session_state.overwrite = False
if 'cancel' not in st.session_state:
    st.session_state.cancel = False
if 'prev_action' not in st.session_state:
    st.session_state.prev_action = False
if 'message' not in st.session_state:
    st.session_state.message = ""
if "isq_uploader_key" not in st.session_state:
    st.session_state.isq_uploader_key = 0
if "pdf_uploader_key" not in st.session_state:
    st.session_state.pdf_uploader_key = 2
if "csv_uploader_key" not in st.session_state:
    st.session_state.csv_uploader_key = 0

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "member_token" not in st.session_state:
    st.session_state.member_token = None
if "member_info" not in st.session_state:
    st.session_state.member_info = None   

if 'controller' not in st.session_state:
    st.session_state.controller = CookieController()
    time.sleep(5)

controller = st.session_state.controller

login = st.Page("page/account/login.py", title="Log In", icon=":material/login:")

# setting up page navigation
if st.session_state.logged_in:

    # linking pages to .py files
    allData = st.Page("page/data/allData.py", title="All Data", icon=":material/analytics:", default=True)
    csv_upload = st.Page("page/upload/csvUpload.py", title="CSV Upload", icon=":material/table_rows:")
    fillable_form = st.Page("page/upload/form.py", title="Fillable Form", icon=":material/edit_note:")
    image_upload = st.Page("page/upload/imageUpload.py", title="Image Upload", icon=":material/add_photo_alternate:")
    profile = st.Page("page/account/profile.py", title=f"My Profile ({st.session_state.member_info["member"]["contact"]["firstName"]} {st.session_state.member_info["member"]["contact"]["lastName"]})", icon=":material/person:")
    logout = st.Page("page/account/logout.py", title="Log Out", icon=":material/logout:")

    pg = st.navigation(
            {
                "Data": [allData],
                "Upload": [csv_upload, fillable_form, image_upload],
                "Account": [profile, logout],
            }
        )
else:
    pg = st.navigation([login])

pg.run()