# IMPORTING LIBRARIES
import streamlit as st
import requests
import base64
import hashlib
import os
from urllib.parse import urlparse, parse_qs
from streamlit_url_fragment import get_fragment

WIX_CLIENT_ID = st.secrets["WIX_CLIENT_ID"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]  

def generate_code_verifier(length=64):
    """
    Generate random code verifier string for PKCE flow

    """
    return base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8').rstrip('=')

def generate_code_challenge(code_verifier):
    """
    Transforms code verifier using SHA-256
    
    """
    hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(hashed).decode('utf-8').rstrip('=')

def get_visitor_token():
    """
    Gets visitor token from Wix API
    
    Paramaters:
    None

    Returns:
    visitor_token (String) : token needed to generate an auth url 
    """
    auth_url = "https://www.wixapis.com/oauth2/token"
    payload = {
        'client_id': WIX_CLIENT_ID,
        'grant_type': 'anonymous',
        'f': 'json'
    }
    try:
        res = requests.post(auth_url, data=payload, verify=False)
        res.raise_for_status()
        res_json = res.json()
        visitor_token = res_json["access_token"]
        return visitor_token
    except requests.exceptions.RequestException as e:
        print(f"Error requesting visitor token: {e}")
        return None

def get_auth_url(visitor_token, code_challenge, state):
    """
    Generates an authentication url from Wix API
    
    Paramaters:
    visitor_token (String) : token to validate request
    code_challenge (String) : required for PKCE flow
    state (String) : used for additional security

    Returns:
    login_url (String) : url where user can login with Spectra Collab account
    """
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

    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        login_url = res.json().get("redirectSession", {}).get("fullUrl")
        return login_url
    except requests.exceptions.RequestException as e:
        print(f"Error requesting login url: {e}")
        return None
    
def get_query_params():
    """
    Gets query parameters from header. Needed since code fragment.
    
    """
    url_with_fragment = get_fragment()

    parsed_url = urlparse(url_with_fragment)
    fragment = parsed_url.fragment
    fragment_params = parse_qs(fragment)

    code = fragment_params.get("code", [None])[0]
    state = fragment_params.get("state", [None])[0]

    return code, state

def get_member_token(code, code_verifier):
    """
    Gets member access token from Wix API
    
    Paramaters:
    code (String) : auth code returned by wix with redirect uri after successful login
    code_verifier (String) : used to match with code_challenge on Wix server for PKCE flow

    Returns:
    member_token (String) : access_token to make API requests 
    """
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
    try:
        res = requests.post(url, headers=headers, json=payload, verify=False)
        res.raise_for_status()
        res_json = res.json()
        member_token = res_json["access_token"]
        return member_token
    except requests.exceptions.RequestException as e:
        print(f"Error requesting access token: {e}")
        return None

def get_member_info(member_token):
    """
    Gets member information
    
    Paramaters:
    member_token (String) : required to access API

    Returns:
    member (JSON) : JSON list of member information
    """
    url = "https://www.wixapis.com/members/v1/members/my?fieldSet=FULL"
    headers = {
        'Authorization': f'Bearer {member_token}', 
        'Content-Type': 'application/json' 
    }
    try:
        res = requests.get(url, headers=headers, verify=False)
        res.raise_for_status()
        res_json = res.json()
        return res_json
    except requests.exceptions.RequestException as e:
        print(f"Error requesting member info: {e}")
        return None
    
def get_member_cms_info(member_token, member_id):
    """
    Queries data items from the 'PostedMembers' collection to retrieve their info.

    Parameters:
    member_token (str): Required to access the Wix Data API.

    Returns:
    res_json: json list of given member details from the 'PostedMembers' collection,
          or None if the request fails.
    """
    url = "https://www.wixapis.com/wix-data/v2/items/query"
    headers = {
        'Authorization': f'Bearer {member_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "dataCollectionId": "PostedMembers",
        "query": {"filter": {
                        "_owner": {
                            "$eq": f"{member_id}"
                        }
                    }},
        "returnTotalCount": False,
        "consistentRead": False,
        "appOptions": {},
        "publishPluginOptions": {},
        'f': 'json'
    }
    try:
        res = requests.post(url, headers=headers, json=payload, verify=False)
        res.raise_for_status()
        res_json = res.json()
        return res_json
    except requests.exceptions.RequestException as e:
        print(f"Error querying data items: {e}")
        return None