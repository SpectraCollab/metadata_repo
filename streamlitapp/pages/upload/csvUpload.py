import streamlit as st
import pandas as pd
import utils.streamlit_utils as stutil

print("\n\tcsv_import")
stutil.print_states()
"""#### Upload CSV

Users may have the option to upload a pre-formatted CSV with the same fields as the Fillable Form. 
This may allow users to upload metadata for multiple subjects at once."""
# Used to display the previous action that occured after the page was rerun
if st.session_state.prev_action == "csv":
    st.warning(st.session_state.message)

st.header("Upload Metadata CSV")
uploaded_file = st.file_uploader("Accepted File Types: CSV, XLSX", type=['csv', 'xlsx'], accept_multiple_files=False, key=st.session_state.csv_uploader_key)

if uploaded_file is not None:
    data = []
    if uploaded_file.type == "text/csv":
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    # DO SOME ERROR CHECKING FOR REQUIRED FIELDS
    data.drop(columns='Unnamed: 0', inplace=True, errors="ignore")
    st.write(data)
    st.button("Add to Database", on_click=stutil.add_to_db_button_clicked)
    if st.session_state.add_to_db_button:
        stutil.insert_df_into_collection(data, "allData", "csv")