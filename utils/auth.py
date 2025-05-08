# IMPORTING LIBRARIES
import streamlit as st
import requests
import base64
import hashlib
from urllib.parse import urlparse, parse_qs
from streamlit_url_fragment import get_fragment

WIX_CLIENT_ID = st.secrets["WIX_CLIENT_ID"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]  

def generate_code_verifier(length=64):
    return base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8').rstrip('=')

def generate_code_challenge(code_verifier):
    hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(hashed).decode('utf-8').rstrip('=')

def get_visitor_token():
    auth_url = "https://www.wixapis.com/oauth2/token"
    payload = {
        'client_id': WIX_CLIENT_ID,
        'grant_type': 'anonymous',
        'f': 'json'
    }
    res = requests.post(auth_url, data=payload, verify=False)
    res_json = res.json()
    visitor_token = res_json["access_token"]
    return visitor_token

def get_auth_url(visitor_token, code_challenge, state):
    url = "https://www.wixapis.com/_api/redirects-api/v1/redirect-session"
    headers = {
    "Authorization": f"Bearer {visitor_token}",
    "Content-Type": "application/json",
    }
    payload = {
        "auth": {
            "authRequest": {
                "redirectUri": REDIRECT_URI,
                "clientId": WIX_CLIENT_ID,
                "codeChallenge": code_challenge,
                "codeChallengeMethod": "S256",
                "responseMode": "fragment",
                "responseType": "code",
                "scope": "offline_access",
                "state": state,
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    login_url = response.json().get("redirectSession", {}).get("fullUrl")

    return login_url

def get_query_params():
    url_with_fragment = get_fragment()

    parsed_url = urlparse(url_with_fragment)
    fragment = parsed_url.fragment
    fragment_params = parse_qs(fragment)

    code = fragment_params.get("code", [None])[0]
    state = fragment_params.get("state", [None])[0]

    return code, state

def get_member_token(code, code_verifier):
    url = "https://www.wixapis.com/oauth2/token"
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'grantType': 'authorization_code',
        'clientId': WIX_CLIENT_ID,
        'redirectUri': REDIRECT_URI,
        'code': code,
        'codeVerifier': code_verifier,
        'f': 'json'
    }
    res = requests.post(url, headers=headers, json=payload, verify=False)
    res_json = res.json()
    member_token = res_json["access_token"]
    return member_token

def get_member_info(member_token):
    url = "https://www.wixapis.com/members/v1/members/my?fieldSet=FULL"
    headers = {
        'Authorization': f'Bearer {member_token}', 
        'Content-Type': 'application/json' 
    }
    res = requests.get(url, headers=headers, verify=False)
    member = res.json()
    return member
