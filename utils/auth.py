# IMPORTING LIBRARIES
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import google.oauth2.id_token


CLIENT_SECRET = st.secrets['client_secret']
CLIENT_ID = st.secrets['client_id']
REDIRECT_URI = st.secrets['redirect_uri']
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"]

client_config = {
    "web": {
        "client_id": CLIENT_ID,
        "project_id": "oauth-430618",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
}

def get_client_id():
    return CLIENT_ID

def get_login_url():
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI)
    authorization_url, _ = flow.authorization_url(prompt='consent')
    return authorization_url

def get_credentials(code):
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI)
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return credentials

def get_user_info(credentials):
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    id_info = google.oauth2.id_token.verify_oauth2_token(
        credentials.id_token, request, CLIENT_ID)
    return id_info

def display_user():
    # Get the code from the URL
    code = st.query_params.get('code')
    st.write(f"Authorization code: {code}")

    if code:
        credentials = get_credentials(code)
        st.write(f"Credentials: {credentials}")

        if credentials:
            user_info = get_user_info(credentials)
            user_email = user_info.get("email")
            user_id = user_info.get("sub")
            st.write(f"You're logged in as {user_email} and your ID is {user_id}")
        else:
            st.write("Failed to get credentials.")
    else:
        st.write(f'You must log in first!')

def login():
    # Get the code from the URL

    code = st.query_params.get('code')
    # st.write(f"Authorization code: {code}")

    if code:
        credentials = get_credentials(code)
        # st.write(f"Credentials: {credentials}")

        if credentials:
            st.session_state.logged_in = True
            user_info = get_user_info(credentials)
            st.session_state.active_user_id = user_info.get("sub")
            st.session_state.active_user = user_info.get("email")
            st.rerun()
        else:
            st.write("Failed to get credentials.")
    else:
        st.write(f'Please use the Google Auth Link to Login')