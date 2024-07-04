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
    st.session_state.sex_select_key += 1
    st.session_state.age_select_key += 1
    st.session_state.study_select_key += 1

# Convert MongoDB query results to DataFrame
def to_df(query_results):
    df = pd.DataFrame(query_results)
    if not df.empty:
        df['birth_date'] = pd.to_datetime(df['birth_date'])
        df['birth_date'] = df['birth_date'].dt.date
        return df
    else:
        return "No Items Match Search"

# Calculating age of subject based on birthdate
def calculate_age(birthdate):
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

# Page Setup
allData = stutil.get_collection("allData")
protocols = stutil.get_collection("protocols")
protocols_df = pd.DataFrame(protocols.find({}))
data = to_df(allData.find({}))

# All Data Section
titleCol1, titleCol2 = st.columns([0.6, 0.4])
md = """#### Welcome to the SPECTRA Metadata Repository

This demonstration will show basic functionality of uploading image metadata to the database."""
titleCol1.markdown(md)
titleCol2.image("spectra.webp", width=250)
st.header("All Data")

# if there are no documents in the collection, data will be a string type
if type(data) == str:
    st.write("No data to display.")
else:
    col1, col2 = st.columns([0.25, 0.75])
    # Filter Selection Form in the right column
    with col1.form("filters", clear_on_submit=False):
        studies = data["study_ID"].unique()

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
                query["sex"] = sex_select 
            if age_select[0] > 0 or age_select[1] < 100:
                data['age'] = data["birth_date"].apply(calculate_age)
                ids = data["_id"][(data["age"] >= age_select[0]) & (data["age"] <= age_select[1])].to_list()
                data.drop('age', axis='columns')
                sub_query = {'$in': ids}
                query["_id"] = sub_query
            if study_select != []:
                sub_query = {'$in': study_select}
                query["study_ID"] = sub_query

            # Execute Query       
            data = to_df(allData.find(query))

        # Return all data if reset is clicked... still need to reset buttons
        elif reset:
            allData = stutil.get_collection("allData")
            data = to_df(allData.find({}))

    # Displaying the DataFrame in the left column
    col2.write(data)

# Protocols Section
st.header("Protocols")
st.write(protocols_df)

md = """Feel free to check out the GitHub repository:

https://github.com/SpectraCollab/metadata_repo.git"""
st.markdown(md)
        
