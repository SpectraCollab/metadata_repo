import streamlit as st

st.write("Please Click the Button to Log In")

if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()