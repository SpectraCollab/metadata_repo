import streamlit as st
import utils.auth as auth
import utils.streamlit_utils as stutil

st.set_page_config(layout="centered")

st.header('Login to the Spectra Repository')

# Fetch client_id and login_url
client_id = auth.get_client_id()
login_url = auth.get_login_url()

approved_users_collection = stutil.get_collection('users')

st.write("Enter Login Details Below:")

email = st.text_input("Email")
password = st.text_input("Password", type='password')

if st.button("Log in"):
    if email != '' and password != '':
        approved_users = list(approved_users_collection.find({"email": email, "password": password}))
        if len(approved_users) == 1:
            user = approved_users[0]

            id = user.get("_id")
            first_name = user.get("firstName")
            last_name = user.get("lastName")
            institution = user.get("institution")
            
            st.session_state.active_user = {
                'id': id,
                'email': email,
                'firstName': first_name,
                'lastName': last_name,
                'institution': institution
            }

            st.session_state.logged_in = True
            st.rerun()
        elif len(approved_users) == 0:
            st.error("Invalid Email/Password")
        else:
            st.warning("Multiple users found with these credentials. Please contact admin.")
    else:
        st.warning("Please Enter an Email and Password")

st.header("Or")

login_html = f"""<a
    href="{login_url}" 
    type="button" 
    class="login-with-google-btn" 
    style="padding: 12px 16px 12px 42px;
        border: none;
        border-radius: 3px;
        box-shadow: 0 -1px 0 rgba(0, 0, 0, .04), 0 1px 1px rgba(0, 0, 0, .25);
        color: #757575;
        font-size: 14px;
        font-weight: 500;
        background-image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGcgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIj48cGF0aCBkPSJNMTcuNiA5LjJsLS4xLTEuOEg5djMuNGg0LjhDMTMuNiAxMiAxMyAxMyAxMiAxMy42djIuMmgzYTguOCA4LjggMCAwIDAgMi42LTYuNnoiIGZpbGw9IiM0Mjg1RjQiIGZpbGwtcnVsZT0ibm9uemVybyIvPjxwYXRoIGQ9Ik05IDE4YzIuNCAwIDQuNS0uOCA2LTIuMmwtMy0yLjJhNS40IDUuNCAwIDAgMS04LTIuOUgxVjEzYTkgOSAwIDAgMCA4IDV6IiBmaWxsPSIjMzRBODUzIiBmaWxsLXJ1bGU9Im5vbnplcm8iLz48cGF0aCBkPSJNNCAxMC43YTUuNCA1LjQgMCAwIDEgMC0zLjRWNUgxYTkgOSAwIDAgMCAwIDhsMy0yLjN6IiBmaWxsPSIjRkJCQzA1IiBmaWxsLXJ1bGU9Im5vbnplcm8iLz48cGF0aCBkPSJNOSAzLjZjMS4zIDAgMi41LjQgMy40IDEuM0wxNSAyLjNBOSA5IDAgMCAwIDEgNWwzIDIuNGE1LjQgNS40IDAgMCAxIDUtMy43eiIgZmlsbD0iI0VBNDMzNSIgZmlsbC1ydWxlPSJub256ZXJvIi8+PHBhdGggZD0iTTAgMGgxOHYxOEgweiIvPjwvZz48L3N2Zz4=);
        background-color: white;
        background-repeat: no-repeat;
        background-position: 12px 11px;" 
    >
  Sign in with Google
</a>"""

st.write(login_html, unsafe_allow_html=True)

# st.link_button("Google Login", login_url)

# Call the authentication function (ensure it handles the OAuth flow correctly)
auth.login()

if st.session_state.oauth_email:
    approved_users_collection = stutil.get_collection('users')
    approved_users = list(approved_users_collection.find({'email': st.session_state.oauth_email}))
    if len(approved_users) == 1:
        user = approved_users[0]

        id = user.get("_id")
        first_name = user.get("firstName")
        last_name = user.get("lastName")
        institution = user.get("institution")
        
        st.session_state.active_user = {
            'id': id,
            'email': email,
            'firstName': first_name,
            'lastName': last_name,
            'institution': institution
        }

        st.session_state.logged_in = True
        st.rerun()
    else:
        st.warning("Oops, it looks like this Gmail account hasn't been approved by the Spectra Administrators. Please contact ... to get access to this repository.")