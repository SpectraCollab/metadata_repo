import streamlit as st
import utils.streamlit_utils as stutil
import pandas as pd

stutil.print_states()

st.write("Coming soon...")

# users = stutil.get_collection('users')
# active_user = users.find_one({"_id": st.session_state.active_user_id})
# active_user = pd.DataFrame([active_user])

# st.header("Your Profile")

# if st.session_state.prev_action == 'profile':
#     st.warning("Profile Information Updated")

# with st.form("User Info", clear_on_submit=False):
#     email = st.text_input("Email", value=active_user['email'].iloc[0])
#     firstName = st.text_input("First Name", value=active_user['firstName'].iloc[0])
#     lastName = st.text_input("Last Name", value=active_user['lastName'].iloc[0])
#     institution = st.text_input("Institution", value=active_user['institution'].iloc[0])

#     if st.form_submit_button("Update Profile"):
#         users.update_one(
#             {"_id": st.session_state.active_user_id}, 
#             {"$set":
#                 {
#                     'email': email,
#                     'firstName': firstName,
#                     'lastName': lastName,
#                     'institution': institution
#                 }
#             }
#         )
#         st.session_state.active_user = f"{firstName} {lastName}"
#         st.session_state.prev_action = 'profile'
#         st.rerun()