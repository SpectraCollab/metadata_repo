import streamlit as st
import pandas as pd
import utils.streamlit_utils as stutil

st.set_page_config(layout="centered")

st.write("Enter Login Details Below:")

email = st.text_input("Email")
password = st.text_input("Password", type='password')

if st.button("Log in"):
    if email != '' and password != '':
        users = stutil.get_collection('users')
        query = users.find({"email": email, "password": password})
        query_result = list(query)
        if len(query_result) == 1:
            user = query_result[0]
            first_name = user.get("firstName")
            last_name = user.get("lastName")
            st.session_state.logged_in = True
            st.session_state.active_user_id = user.get("_id")
            st.session_state.active_user = f"{first_name} {last_name}"
            st.session_state.active_institution = user.get("institution")
            st.rerun()
        elif len(query_result) == 0:
            st.error("Invalid Email/Password")
        else:
            st.warning("Multiple users found with these credentials. Please contact admin.")
    else:
        st.warning("Please Enter an Email and Password")