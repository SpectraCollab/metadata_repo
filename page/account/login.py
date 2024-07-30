import streamlit as st
import streamlit.components.v1 as components
import utils.auth as auth

st.set_page_config(layout="centered")

st.header('Login to the Spectra Repository')

# Fetch client_id and login_url
client_id = auth.get_client_id()
login_url = auth.get_login_url()

st.write(f'<a target="_self" href="{login_url}">Google login</a>', unsafe_allow_html=True)

# Call the authentication function (ensure it handles the OAuth flow correctly)
auth.login()
