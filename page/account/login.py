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

# st.write(f'<a target="_self" href="{login_url}">Google login</a>', unsafe_allow_html=True)
st.link_button("Google Login", login_url)

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