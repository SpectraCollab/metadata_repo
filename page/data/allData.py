import streamlit as st
import pandas as pd
from datetime import date
import utils.streamlit_utils as stutil

st.set_page_config(layout="wide")

## PAGES ##
print("\n\thome")
stutil.reset_session_states()
stutil.reset_prev_action()
stutil.print_states()

if "sex_select_key" not in st.session_state:
    st.session_state.sex_select_key = 0
if "age_select_key" not in st.session_state:
    st.session_state.age_select_key = 3
if "study_select_key" not in st.session_state:
    st.session_state.study_select_key = 6

def update_keys():
    """
    Callback function to update the keys on the filter buttons

    Parameters:
    None

    Returns:
    None
    """
    st.session_state.sex_select_key += 1
    st.session_state.age_select_key += 1
    st.session_state.study_select_key += 1

# Convert MongoDB query results to DataFrame
def to_df(query_results):
    """
    Converts database query results to a pandas dataframe

    Parameters:
    query_results (pymongo cursor): results from database query

    Returns:
    df (DataFrame): results in DataFrame format, or string if query results is empty
    """
    df = pd.DataFrame(query_results)
    if not df.empty:
        return df
    else:
        return "No Items Match Search"

# Page Setup
allData = stutil.get_collection("allData")
protocols = stutil.get_collection("protocols")
protocols_df = pd.DataFrame(protocols.find({}))
protocols_df.drop(columns="_id", inplace=True)
data = to_df(allData.find({}))

# All Data Section
titleCol1, titleCol2 = st.columns([0.6, 0.4])
md = """#### Welcome to the SPECTRA Metadata Repository

This demonstration will show basic functionality of uploading image metadata to the database."""
titleCol1.markdown(md)
titleCol2.image("assets/spectra.webp", width=250)
st.header("All Data")

# if there are no documents in the collection, data will be a string type
if type(data) == str:
    st.write("No data to display.")
else:
    col1, col2 = st.columns([0.25, 0.75])
    # Filter Selection Form in the right column
    with col1.form("filters", clear_on_submit=False):
        studies = data["study_id"].unique()

        # Query Params selection
        with st.expander("Participant Filters"):
            sex_select = st.radio("Sex", ["All", "M", "F"], key=st.session_state.sex_select_key)
            age_select = st.slider("Age Range", 0, 100, value=(0, 100), key=st.session_state.age_select_key)

        study_select = st.multiselect("Study ID", studies, key=st.session_state.study_select_key)

        # Submit/reset buttons
        formCol1, formCol2 = st.columns([0.6,0.4])
        submitted = formCol1.form_submit_button("Submit Query")
        reset = formCol2.form_submit_button("Reset", on_click=update_keys)  

        # Run query if submit button is clicked
        if submitted:

            # Refresh data
            allData = stutil.get_collection("allData")

            # Initialize Query
            query = {}   

            # Building Query
            if sex_select != "All":
                query["sex_assigned_at_birth"] = sex_select 
            if age_select[0] > 0 or age_select[1] < 100:
                ids = data["_id"][(data["age"] >= age_select[0]) & (data["age"] <= age_select[1])].to_list()
                data.drop('age', axis='columns')
                sub_query = {'$in': ids}
                query["_id"] = sub_query
            if study_select != []:
                sub_query = {'$in': study_select}
                query["study_id"] = sub_query

            # Execute Query       
            data = to_df(allData.find(query))

        # Return all data if reset is clicked... still need to reset buttons
        elif reset:
            allData = stutil.get_collection("allData")
            data = to_df(allData.find({}))

    # Displaying the DataFrame in the left column
    data.drop(columns="_id", inplace=True)
    col2.write(data)

st.header("Definitions")
definitions  = pd.read_excel('assets/field_definitions.xlsx')
st.write(definitions)

# Protocols Section
st.header("Protocols")
st.write(protocols_df)
        
