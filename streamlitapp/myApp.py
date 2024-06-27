import streamlit as st
import pymongo
import pandas as pd
from datetime import date
import utils.file_reader

st.set_page_config(layout="wide")

## SESSION STATES ##
if 'add_to_db_button' not in st.session_state:
    st.session_state.add_to_db_button = False
if 'keep' not in st.session_state:
    st.session_state.keep = False
if 'overwrite' not in st.session_state:
    st.session_state.overwrite = False
if 'cancel' not in st.session_state:
    st.session_state.cancel = False
if 'prev_action' not in st.session_state:
    st.session_state.prev_action = False
if 'message' not in st.session_state:
    st.session_state.message = ""
if "isq_uploader_key" not in st.session_state:
    st.session_state.isq_uploader_key = 0
if "pdf_uploader_key" not in st.session_state:
    st.session_state.pdf_uploader_key = 2
if "csv_uploader_key" not in st.session_state:
    st.session_state.csv_uploader_key = 0

## SESSION STATE FUNCTIONS ##
def add_to_db_button_clicked():
    st.session_state.add_to_db_button = True

def keep_clicked():
    st.session_state.keep = True
    st.session_state.prev_action = True

def overwrite_clicked():
    st.session_state.overwrite = True
    st.session_state.prev_action = True

def cancel_clicked():
    st.session_state.cancel = True
    st.session_state.prev_action = True

def reset_session_states():
    st.session_state.keep = False
    st.session_state.overwrite = False
    st.session_state.cancel = False
    st.session_state.add_to_db_button = False

    st.session_state.isq_df = False
    st.session_state.pdf_df = False
    st.session_state.form_df = False

    st.session_state.isq_uploader_key += 1
    st.session_state.pdf_uploader_key += 1
    st.session_state.csv_uploader_key += 1

def reset_prev_action():
    st.session_state.prev_action = False

def print_states():
    states = pd.DataFrame([st.session_state])
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(states, "\n")

## FUNCTIONS ##
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

def insert_df_into_collection(df, collection_name):
    """
    Inserts rows of a DataFrame as documents into a collection

    Parameters:
    df (DataFrame): Data to be inserted into collection 
    collection_name (str): Name of the collection to insert data into

    Returns:
    None

    """

    # Setting up connection to the desired db collection
    client = init_connection()
    db = client.spectra
    collection = db[collection_name]

    # searching for duplicates in the "file_name_x" column
    duplicates = pd.DataFrame(collection.find({"file_name_x": {"$in":df["file_name_x"].tolist()}}))

    # if we find duplicates
    if not duplicates.empty:
        st.warning(f"There are {duplicates.shape[0]} entries that already exist in the collection.")
        duplicates.drop(columns="_id", inplace=True)
        st.write("Existing Data")
        st.write(duplicates)

        searchfor = duplicates["file_name_x"].tolist()
        df_duplicates = df[df["file_name_x"].str.contains('|'.join(searchfor))]
        st.write("New Data")
        st.write(df_duplicates)

        col1, col2, col3 = st.columns(3)
        col1.button("Keep Existing File in Database", on_click=keep_clicked)
        col2.button("Overwrite Existing File", on_click=overwrite_clicked)
        col3.button("Cancel Upload", on_click=cancel_clicked)

        if st.session_state.keep:

            # NEED TO IMPLEMENT DB QUERY

            st.session_state.message = f"Keeping Duplicates: Inserted ... items to database."
            reset_session_states() # reset states and rerun script, essentially makes it look like the page has refreshed
            st.rerun()

        if st.session_state.overwrite:
            collection.delete_many({"file_name_x": {"$in":df["file_name_x"].tolist()}}) # delete the duplicates in the db
            try:
                insert = collection.insert_many(df.to_dict('records')) # insert all records in the new data
                st.session_state.message = f"Overwrote Duplicates: Inserted {len(insert.inserted_ids)} items to database."
            except Exception as e:
                st.write("Something went wrong...")
                st.write(e)
            reset_session_states()
            st.rerun()

        if st.session_state.cancel:
            st.session_state.message = f"Cancelled Data Upload"
            reset_session_states()
            st.rerun()
    
    # if there are no duplicates, we can go straight to uploading
    else:
        try:
            insert = collection.insert_many(df.to_dict('records')) # insert all new records into db
            st.session_state.message = f"No Duplicates Found: Inserted {len(insert.inserted_ids)} items to database!"
            st.session_state.prev_action = True
            reset_session_states()
            st.rerun()
        except Exception as e:
            st.write("Something went wrong...")
            st.write(e)

## PAGES ##
def home():
    print("\n\thome")
    reset_session_states()
    reset_prev_action()
    print_states()

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
    print("\n\tfillable_form")
    print_states()
    """#### Fillable Form
    
Users may have the option to manually add metadata at the subject level. This method maximizes simplicity while sacrificing ability to easily upload multiple subjects."""
    if 'form_df' not in st.session_state:
        st.session_state.form_df = False

    # Used to display the previous action that occured after the page was rerun
    if st.session_state.prev_action:
        st.warning(st.session_state.message)

    st.header("Add Image Metadata")
    with st.form("filters", clear_on_submit=False):

        file_name = st.text_input("File Name*")
        date_recorded = st.date_input("Date Recorded*")
        study_id = st.selectbox("Study ID*", ["3300_SPECTRA", "3309_HAND"])
        scanner_id = st.selectbox("Scanner ID*", ["3300", "3309"])
        min_intensity = st.number_input("Min Intensity", value=-1000)
        max_intensity = st.number_input("Max Intensity", value=10000)

        "---"

        # Submit/reset buttons
        submitted = st.form_submit_button("Submit Form")

        if submitted:
            if not file_name:
                st.warning("Please Fill In Required Fields")
            else:
                entered_fields = {
                    "file_name_x": file_name,
                    "date": str(date_recorded),
                    "study_ID": study_id,
                    "scanner_id": scanner_id,
                    "min_intensity": min_intensity,
                    "max_intensity": max_intensity
                }
                all_keys = [
                    "file_name_x",
                    "time_BL",
                    "time_FU_3mo",
                    "time_FU_6mo",	
                    "birth_date",	
                    "sex",	
                    "side_per_clinician",	
                    "height_cm",	
                    "weight_kg",
                    "pat_name_x",	
                    "fractures_surgeries",	
                    "metal_in_VOI",	
                    "recent_imaging",	
                    "pregnant",	
                    "scanner_id_1",
                    "scanner_id_2",
                    "scanner_id_3",	
                    "pat_no_1",	
                    "pat_no_2",	
                    "pat_no_3",	
                    "meas_no",
                    "ctr_file_1",
                    "ctr_file_2",	
                    "ctr_file_3",	
                    "ref_line_1",	
                    "ref_line_2",	
                    "ref_line_3",	
                    "saved_scout_1",	
                    "saved_scout_2",	
                    "saved_scout_3",	
                    "side_1",	
                    "side_2",	
                    "side_3",	
                    "comments_1",	
                    "comments_2",	
                    "comments_3",	
                    "tech_1",	
                    "tech_2",	
                    "tech_3",	
                    "study_ID",	
                    "LMP",	
                    "Site",	
                    "PI",	
                    "Time points",
                    "Inclusion requirements",
                    "Organ",	
                    "Precalibration",
                    "Positioning",
                    "Scout view",	
                    "Control files", 	
                    "Protocol location",	
                    "Subject forms location",	
                    "file_name_y",	
                    "check",	
                    "data_type",	
                    "nr_of_bytes",	
                    "nr_of_blocks",	
                    "pat_no",	
                    "scanner_id",	
                    "date",	
                    "n_voxels_x",	
                    "n_voxels_y",	
                    "n_voxels_z",	
                    "total_size_um_x",	
                    "total_size_um_y",	
                    "total_size_um_z",	
                    "slice_thickness_um",	
                    "pixel_size_um",	
                    "slice_1_pos_um",	
                    "min_intensity",	
                    "max_intensity",	
                    "mu_scaling",	
                    "nr_of_samples",	
                    "nr_of_projections",	
                    "scan_dist_um",	
                    "scanner_type",	
                    "exposure_time",	
                    "site",	
                    "reference_line_um",	
                    "recon_algo",	
                    "pat_name_y",	
                    "energy_V",	
                    "intensity_uA",	
                    "data_offset"
                ]
                data_dict = {key:None for key in all_keys}
                for key in data_dict:
                    if key in entered_fields.keys():
                        data_dict[key] = entered_fields[key]
                st.session_state.form_df = pd.DataFrame([data_dict])

    if isinstance(st.session_state.form_df, pd.DataFrame):
        if not st.session_state.form_df.empty:
            st.write(st.session_state.form_df)
            st.button("Add to Database", on_click=add_to_db_button_clicked)
            if st.session_state.add_to_db_button:
                insert_df_into_collection(st.session_state.form_df, "allData")

def csv_import():
    print("\n\tcsv_import")
    print_states()
    """#### Upload CSV
    
Users may have the option to upload a pre-formatted CSV with the same fields as the Fillable Form. 
This may allow users to upload metadata for multiple subjects at once."""
    # Used to display the previous action that occured after the page was rerun
    if st.session_state.prev_action:
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
        st.button("Add to Database", on_click=add_to_db_button_clicked)
        if st.session_state.add_to_db_button:
            insert_df_into_collection(data, "allData")
        
def image_upload():
    print("\n\timage_upload")
    print_states()
    """#### Upload Image and PDF
    
Users have the option to upload batches of images and PDFs which can automatically be parsed for relevant metadata. 
This option comes with increased complexity regarding security and server performance."""

    if 'isq_df' not in st.session_state:
        st.session_state.isq_df = False
    if 'pdf_df' not in st.session_state:
        st.session_state.pdf_df = False

    if st.session_state.prev_action:
        st.warning(st.session_state.message)

    isq_loaded = False
    subjects_loaded = False
    protocols_loaded = False

    col1, col2 = st.columns([0.5, 0.5])
    # Image Upload Section
    col1.header("""Upload Images""")
    uploaded_images = col1.file_uploader("Accepted File Types: ISQ", type=['isq', 'isq;1'], accept_multiple_files=True, key=st.session_state.isq_uploader_key)
    if uploaded_images != []:
        if isinstance(st.session_state.isq_df, pd.DataFrame):
            print("ISQs Already Read")
        else:
            print("Reading ISQs")
            st.session_state.isq_df = utils.file_reader.isq_to_df(uploaded_images)

        col1.write(st.session_state.isq_df)
        isq_loaded = True

    # Study Upload Section
    col2.header("""Upload Subjects""")
    uploaded_subjects = col2.file_uploader("Accepted File Types: PDF", type=['pdf'], accept_multiple_files=True, key=st.session_state.pdf_uploader_key)
    if uploaded_subjects != []:
        if isinstance(st.session_state.pdf_df, pd.DataFrame):
            print("PDFs Already Read")
        else:
            print("Reading PDFs")
            st.session_state.pdf_df = utils.file_reader.pdf_to_df(uploaded_subjects)

        col2.write(st.session_state.pdf_df)
        subjects_loaded = True

    # Fetching Protocols
    protocols = get_collection("protocols")
    protocols_df = pd.DataFrame(protocols.find({}))
    protocols_df.drop(columns="_id", inplace=True)
    if not protocols_df.empty:
        protocols_loaded = True

    # Merging Uploaded Data
    if isq_loaded and subjects_loaded and protocols_loaded:
        subjects_and_protocols = pd.merge(st.session_state.pdf_df, protocols_df, on=['study_ID'])
        merged_df = pd.merge(subjects_and_protocols, st.session_state.isq_df, on=['meas_no'])
        st.header("Merged Dataset")
        if merged_df.empty:
            st.write("Unable to merge datasets...")
        # Writing new rows to database    
        else:
            st.write(merged_df)
            st.button("Add to Database", on_click=add_to_db_button_clicked)

            if st.session_state.add_to_db_button:
                insert_df_into_collection(merged_df, "allData")

# Page and Sidebar Setup
page_names_to_funcs = {
    "Home": home,
    "Fillable Form": fillable_form,
    "Upload CSV": csv_import,
    "Upload Images": image_upload
}
demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
