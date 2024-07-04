import streamlit as st

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

allData = st.Page("pages/data/allData.py", title="All Data", icon=":material/analytics:", default=True)

csv_upload = st.Page("pages/upload/csvUpload.py", title="CSV Upload", icon=":material/table_rows:")
fillable_form = st.Page("pages/upload/form.py", title="Fillable Form", icon=":material/edit_note:")
image_upload = st.Page("pages/upload/imageUpload.py", title="Image Upload", icon=":material/add_photo_alternate:")

profile = st.Page("pages/account/profile.py", title="My Profile", icon=":material/person:")
logout = st.Page("pages/account/logout.py", title="Log Out", icon=":material/logout:")
login = st.Page("pages/account/login.py", title="Log In", icon=":material/login:")

if st.session_state.logged_in:
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
        
