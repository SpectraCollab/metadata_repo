import streamlit as st
import pymongo
import pandas as pd
from datetime import date
import utils
import utils.sanco_read_files_adapted
import PyPDF2

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
items = get_data()
data = to_df(items.find({}))
studies = data["study_ID"].unique()

# All Data Section
st.image("spectra.webp", width=250)
st.header("""All Data""")
col1, col2 = st.columns([0.25, 0.75])

# Filter Selection Form in the right column
with col1.form("filters", clear_on_submit=False):
        
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
col2.write(data)

col3, col4 = st.columns([0.5, 0.5])

# Image Upload Section
col3.header("""Upload Images""")
uploaded_images = col3.file_uploader("Accepted File Types: .isq", type=['isq', 'isq;1'], accept_multiple_files=True)

if uploaded_images != []:
    all_keys = []
    all_values = []

    for index, uploaded_image in enumerate(uploaded_images):

        current_keys, current_values = utils.sanco_read_files_adapted.read_isq_header(uploaded_image)

        if index == 0:
            all_keys = current_keys

        all_values.append(current_values)

    # create dataframe (=table)
    isq_headers = pd.DataFrame(all_values, columns = all_keys)

    # adding column with file names in position 0
    isq_headers.insert(0, "file_name", [uploaded_image.name for uploaded_image in uploaded_images])

    # delete column "fill" because it just contains zeros
    isq_headers = isq_headers.drop(columns = ["fill"])

    col3.write(isq_headers)

# Study Upload Section
col4.header("""Upload Subjects""")
uploaded_subjects = col4.file_uploader("Accepted File Types: .pdf", type=['pdf'], accept_multiple_files=True)

if uploaded_subjects != []:
    all_keys = []
    all_values = []

    for index, file in enumerate(uploaded_subjects):

        f = PyPDF2.PdfReader(file)
        ff = f.get_fields()

        # get keys for the current subject
        current_keys = list(ff.keys())

        # get the values for the current subject
        current_values = []
        for k,v in ff.items():
            if "/V" in v.keys():
                current_values.append(v["/V"])
            else:
                current_values.append("")
        
        # save the keys of the first subject in the variable all_keys
        if index == 0:
            all_keys = current_keys

        # add the values of the current subject to all_values
        all_values.append(current_values)
    
    # create dataframe (=table)
    subjects_info = pd.DataFrame(all_values, columns = all_keys)

    # adding column with file names in position 0
    subjects_info.insert(0, "file_name", [file.name for file in uploaded_subjects])

    col4.write(subjects_info)


