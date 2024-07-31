import streamlit as st

if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.active_user = None
        st.session_state.oauth_email = None
        st.rerun()