import streamlit as st
import pymongo
import pandas as pd
from datetime import date

# Initialize connection once and use accross all users and sessions
@st.cache_resource
def init_connection():
    connection_string = st.secrets['connection_string']
    return pymongo.MongoClient(connection_string, tls=True)

# Rerun if method is called or every 10 mins
@st.cache_resource(ttl=600)
def get_data():
    client = init_connection()
    db = client.spectra
    items = db.allData
    return items

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
st.set_page_config(layout="wide")
st.image("spectra.webp", width=250)
st.header("""Data""")
items = get_data()
data = to_df(items.find({}))
studies = data["study_ID"].unique()
col1, col2 = st.columns([0.75, 0.25])

# Filter Selection Form in the right column
with col2.form("filters", clear_on_submit=False):
        
    # Query Params selection
    sex_select = st.radio("Sex", ["All", "M", "F"])
    age_select = st.slider("Minimum Age", 0, 100)
    study_select = st.multiselect("Study ID", studies)

    "---"

    # Submit/reset buttons
    formCol1, formCol2 = st.columns([0.6,0.4])
    submitted = formCol1.form_submit_button("Submit Query")
    reset = formCol2.form_submit_button("Reset")  

    # Run query if submit button is clicked
    if submitted:

        # Refresh data
        items = get_data()

        # Initialize Query
        query = {}   

        # Building Query
        if sex_select != "All":
            query["sex"] = sex_select 
        if age_select > 0:
            data['age'] = data["birth_date"].apply(calculate_age)
            ids = data["_id"][(data["age"] >= age_select)].to_list()
            data.drop('age', axis='columns')
            sub_query = {'$in': ids}
            query["_id"] = sub_query
        if study_select != []:
            sub_query = {'$in': study_select}
            query["study_ID"] = sub_query

        # Execute Query       
        data = to_df(items.find(query))

    # Return all data if reset is clicked... still need to reset buttons
    elif reset:
        items = get_data()
        data = to_df(items.find({}))

# Displaying the DataFrame in the left column
col1.write(data)

# File Upload Section
st.header("""Upload Your Data""")
uploaded_file = st.file_uploader("Accepted File Types: .csv, .xlsx")

# Placeholder for csv... much more work will be done here
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)



