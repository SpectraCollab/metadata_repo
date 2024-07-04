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
                query_result = pd.DataFrame(query)
                if query_result.empty:
                        st.warning("Invalid Email/Password")
                else:
                        st.session_state.logged_in = True
                        st.rerun()
        else:
                st.warning("Please Enter an Email and Password")