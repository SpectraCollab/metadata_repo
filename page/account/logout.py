import streamlit as st

st.header("See you soon!")

if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()