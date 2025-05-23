import streamlit as st

st.header("See you soon!")

if st.button("Log out"):
        st.session_state.member_token = None   
        st.session_state.member_info = None
        st.session_state.member_cms = None
        st.session_state.logged_in = False
        st.rerun()