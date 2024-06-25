import streamlit as st
import pymongo
import pandas as pd
from datetime import date
import utils
import utils.sanco_read_files_adapted
import PyPDF2

st.set_page_config(layout="wide")

def all_data():
    """
    Home page to display current database

    """
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

    @st.cache_resource(ttl=600)
    def get_protocols():
        client = init_connection()
        db = client.spectra
        items = db.protocols
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
    items = get_data()
    protocols = get_protocols()
    protocols_df = pd.DataFrame(protocols.find({}))
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

    # Protocols Section
    st.header("Protocols")
    st.write(protocols_df)

def fillable_form():
    """
    Page to demonstrate uploading metadata manually through an online form

    """
    st.header("Add Image Metadata")
    with st.form("filters", clear_on_submit=False):

        field1 = st.text_input("Field 1")

        "---"

        # Submit/reset buttons
        submitted = st.form_submit_button("Submit Form")

        if submitted:
            st.write(field1)

def csv_import():
    """
    Page to demonstrate uploading metadata from pre-compiled csv

    """

    st.header("Upload Metadata CSV")
    uploaded_file = st.file_uploader("Accepted File Types: CSV, XLSX", type=['csv', 'xlsx'], accept_multiple_files=False)

    if uploaded_file is not None:
        data = []
        if uploaded_file.type == "text/csv":
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        # DO SOME ERROR CHECKING FOR REQUIRED FIELDS

        st.write(data)

def image_upload():
    """
    Page to demonstrate extracting image headers and pdf data automatically

    """
    col1, col2 = st.columns([0.5, 0.5])

    # Image Upload Section
    col1.header("""Upload Images""")
    uploaded_images = col1.file_uploader("Accepted File Types: ISQ", type=['isq', 'isq;1'], accept_multiple_files=True)

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

        col1.write(isq_headers)

    # Study Upload Section
    col2.header("""Upload Subjects""")
    uploaded_subjects = col2.file_uploader("Accepted File Types: PDF", type=['pdf'], accept_multiple_files=True)

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

        col2.write(subjects_info)

# Page and Sidebar Setup
page_names_to_funcs = {
    "Home": all_data,
    "Fillable Form": fillable_form,
    "Upload CSV": csv_import,
    "Upload Images": image_upload
}
demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
