import streamlit as st
import pandas as pd
import utils.streamlit_utils as stutil

print("\n\tcsv_import")
stutil.print_states()
"""#### Upload CSV

Drag and drop a CSV or Excel spreadsheet that adheres to the template below."""

# button to download a template csv
template =  open("assets/spreadsheet_template.csv", "rb")
btn = st.download_button(
        label="Download Template",
        data=template,
        file_name="spreadsheet_template.csv",
        mime="text/csv"
        )

# Used to display the previous action that occured after the page was rerun
if st.session_state.prev_action == "csv":
    st.warning(st.session_state.message)

st.header("Upload Metadata CSV")
uploaded_file = st.file_uploader("Accepted File Types: CSV, XLSX", type=['csv', 'xlsx'], accept_multiple_files=False, key=st.session_state.csv_uploader_key)

# read in spreadsheet based on file type
if uploaded_file is not None:
    data = []
    if uploaded_file.type == "text/csv":
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)
        
    # Error checking for completeness and required fields
    data.drop(columns='Unnamed: 0', inplace=True, errors="ignore")
    template_df = pd.read_csv('assets/spreadsheet_template.csv')
    template_columns = set(template_df.columns)
    data_columns = set(data.columns)
    difference = template_columns-data_columns

    # checking headers match template
    if len(difference) == 0:
        # checking for null values in file name
        if (data['age'].isna().any()) or (data['study_id'].isna().any()) or (data['scan_date'].isna().any()):
            st.warning("Spreadsheet is missing information in required fields. Please fill in required fields and try again.")
        else:
            # displaying data and adding to database
            data = stutil.standardize_csv(data)
            # data = stutil.append_institution(data)
            data = stutil.create_composite_id(data)
            st.write(data)
            st.button("Add to Database", on_click=stutil.add_to_db_button_clicked)
            if st.session_state.add_to_db_button:
                stutil.insert_df_into_collection(data, "allData", "csv")
    else: 
        st.warning("Data must match template headers. Please try again.")