import streamlit as st
import pymongo
import pandas as pd
from datetime import date
import utils.file_reader

st.set_page_config(layout="wide")

@st.cache_resource
def init_connection():
    """
    Initializes connection to MongoDB cluster

    Parameters:
    None

    Returns:
    client (MongoClient): Client for a MongoDB instance

    """
    connection_string = st.secrets['connection_string']
    client = pymongo.MongoClient(connection_string, tls=True)
    return client

@st.cache_resource(ttl=600)
def get_collection(collection_name):
    """
    Retrieves a collection from the spectra database

    Parameters:
    collection_name (str): name of collection 

    Returns:
    collection: (Collection): specified collection

    """
    client = init_connection()
    db = client.spectra
    collection = db[collection_name]
    return collection

def insert_df_into_db(df):
    """
    Inserts rows of a DataFrame as documents into a collection

    Parameters:
    df (DataFrame): Data to be inserted into collection 

    Returns:
    None

    """
    client = init_connection()
    db = client.spectra
    collection = db.allData
    try:
        insert = collection.insert_many(df.to_dict('records'))
        st.write(f"Inserted {len(insert.inserted_ids)} items to database!")
    except:
        st.write("Something went wrong...")

def all_data():
    """
    Home page to display current database

    """

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
    allData = get_collection("allData")
    protocols = get_collection("protocols")
    protocols_df = pd.DataFrame(protocols.find({}))
    data = to_df(allData.find({}))
    studies = data["study_ID"].unique()

    # All Data Section
    titleCol1, titleCol2 = st.columns([0.6, 0.4])
    md = """#### Welcome to the SPECTRA Metadata Repository

This demonstration will show basic functionality of uploading image metadata to the database."""
    titleCol1.markdown(md)
    titleCol2.image("spectra.webp", width=250)
    st.header("All Data")
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
            allData = get_collection("allData")

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
            data = to_df(allData.find(query))

        # Return all data if reset is clicked... still need to reset buttons
        elif reset:
            allData = get_collection("allData")
            data = to_df(allData.find({}))

    # Displaying the DataFrame in the left column
    col2.write(data)

    # Protocols Section
    st.header("Protocols")
    st.write(protocols_df)

    md = """Feel free to check out the GitHub repository:

    https://github.com/SpectraCollab/metadata_repo.git"""
    st.markdown(md)

def fillable_form():
    """
    Page to demonstrate uploading metadata manually through an online form

    """
    md = """#### Fillable Form
    
Users may have the option to manually add metadata at the subject level. This method maximizes simplicity while sacrificing ability to easily upload multiple subjects."""
    st.markdown(md)

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

    md = """#### Upload CSV
    
Users may have the option to upload a pre-formatted CSV with the same fields as the Fillable Form. 
This may allow users to upload metadata for multiple subjects at once."""
    st.markdown(md)

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
    md = """#### Upload Image and PDF
    
Users have the option to upload batches of images and PDFs which can automatically be parsed for relevant metadata. 
This option comes with increased complexity regarding security and server performance."""
    st.markdown(md)
    col1, col2 = st.columns([0.5, 0.5])

    isq_loaded = False
    subjects_loaded = False
    protocols_loaded = False

    # Image Upload Section
    col1.header("""Upload Images""")
    uploaded_images = col1.file_uploader("Accepted File Types: ISQ", type=['isq', 'isq;1'], accept_multiple_files=True)
    if uploaded_images != []:
        isq_df = utils.file_reader.isq_to_df(uploaded_images)
        col1.write(isq_df)
        isq_loaded = True

    # Study Upload Section
    col2.header("""Upload Subjects""")
    uploaded_subjects = col2.file_uploader("Accepted File Types: PDF", type=['pdf'], accept_multiple_files=True)
    if uploaded_subjects != []:
        subjects_df = utils.file_reader.pdf_to_df(uploaded_subjects)
        col2.write(subjects_df)
        subjects_loaded = True

    # Fetching Protocols
    protocols = get_collection("protocols")
    protocols_df = pd.DataFrame(protocols.find({}))
    protocols_df.drop(columns="_id", inplace=True)
    if not protocols_df.empty:
        protocols_loaded = True

    # Merging Uploaded Data
    if isq_loaded and subjects_loaded and protocols_loaded:
        subjects_and_protocols = pd.merge(subjects_df, protocols_df, on=['study_ID'])
        merged_df = pd.merge(subjects_and_protocols, isq_df, on=['meas_no'])
        st.header("Merged Dataset")
        if merged_df.empty:
            st.write("Unable to merge datasets...")

        # Writing new rows to database    
        else:
            st.write(merged_df)
            add_to_db_button = st.button("Add to Database")
            if add_to_db_button:
                insert_df_into_db(merged_df)

# Page and Sidebar Setup
page_names_to_funcs = {
    "Home": all_data,
    "Fillable Form": fillable_form,
    "Upload CSV": csv_import,
    "Upload Images": image_upload
}
demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
