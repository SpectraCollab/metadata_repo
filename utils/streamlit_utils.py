import streamlit as st
import pymongo
import pandas as pd

from utils.column_mappings import img_columns, participant_columns, study_columns

## CALLBACK FUNCTIONS ##

def add_to_db_button_clicked():
    """
    Callback function to set add to db clicked to be true

    Paramaters:
    None

    Returns:
    None
    """
    st.session_state.add_to_db_button = True

def keep_clicked():
    """
    Callback function to set keep clicked to be true

    Paramaters:
    None

    Returns:
    None
    """
    st.session_state.keep = True

def overwrite_clicked():
    """
    Callback function to set overwrite clicked to be true

    Paramaters:
    None

    Returns:
    None
    """
    st.session_state.overwrite = True

def cancel_clicked():
    """
    Callback function to set cancel clicked to be true

    Paramaters:
    None

    Returns:
    None
    """
    st.session_state.cancel = True

def reset_prev_action():
    """
    Callback function to reset the previous action session state

    Parameters:
    None

    Returns:
    None
    """
    st.session_state.prev_action = False

## OTHER FUNCTIONS ##

def reset_session_states():
    """
    Resets most session states in order to keep website flow looking normal

    Parameters:
    None

    Returns:
    None
    """
    st.session_state.keep = False
    st.session_state.overwrite = False
    st.session_state.cancel = False
    st.session_state.add_to_db_button = False

    st.session_state.img_df = False
    st.session_state.pdf_df = False
    st.session_state.form_df = False

    st.session_state.isq_uploader_key += 1
    st.session_state.pdf_uploader_key += 1
    st.session_state.csv_uploader_key += 1

def print_states():
    """
    Prints all session states to console in dataframe format

    Parameters:
    None

    Returns:
    None
    """
    states = pd.DataFrame([st.session_state])
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(states, "\n")

def create_composite_id(df):
    """
    Creates a composite id by concatenating fields from dataframe

    Paramaters:
    df (DataFrame): initial DataFrame

    Returns:
    df (DataFrame): updated DataFrame
    """
    df["composite_id"] = df["sex_assigned_at_birth"] + df["age"].astype(str) + df["weight_kg"].astype(str) + "_" + df["study_id"] + "_" + df["scan_date"].astype(str) + "_" + df["institution"]
    last_column = df.pop('composite_id')  
    df.insert(len(df.columns), 'composite_id', last_column)
    return df

def merge_dataframes(subjects, protocols, images):
    """
    Merges subjects, protocols, and images data into 1 dataframe

    Paramaters:
    subjects (DataFrame): subject level information 
    protocols (DataFrame): study level information
    images (DataFrame): image metadata

    Returns:
    merged_df (DataFrame): all 3 dataframes merged into 1
    """

    def extract_series_num(filename_str):
        list = filename_str.split("_")
        num = list[-1]
        return num

    images['series_num'] = images['file_name'].apply(extract_series_num)
    subjects['series_num'] = subjects['file_name'].apply(extract_series_num)

    try:
        subjects_and_images = pd.merge(subjects, images, on=['series_num'])
        
        if 'age_x' in subjects_and_images.columns:
            subjects_and_images['age'] = subjects_and_images['age_x']
            subjects_and_images.drop(columns=['age_x', 'age_y'], inplace=True)

        if 'study_id_x' in subjects_and_images.columns:
            subjects_and_images['study_id'] = subjects_and_images['study_id_x']
            subjects_and_images.drop(columns=['study_id_x', 'study_id_y'], inplace=True)

        if 'scan_date_x' in subjects_and_images.columns:
            subjects_and_images['scan_date'] = subjects_and_images['scan_date_x']
            subjects_and_images.drop(columns=['scan_date_x', 'scan_date_y'], inplace=True)
    except:
        return None

    try:
        merged_df = pd.merge(subjects_and_images, protocols, on=['study_id'])
    except:
        return None
    
    merged_df.drop(columns=['file_name_x', 'file_name_y', 'series_num'], inplace=True)
    return merged_df

def standardize_csv(csv_fields):
    """
    Maps fields from CSV upload to the standard database schema set in column_mappings.py 

    Paramaters:
    csv_fields (DataFrame): raw data from csv upload

    Returns:
    df (DataFrame): standardized dataframe to match db schema
    """
    # creating empty standardized dataframe and adding apprpriate values from dcm_headers
    csv_columns = participant_columns + study_columns + img_columns
    df = pd.DataFrame(columns=csv_columns)
    
    special_columns = ['length_of_scan_region', 'voxel_spacing']

    for col in csv_columns:
        if col not in special_columns:
            df[col] = csv_fields[col]
            
    def safe_numeric_conversion(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return False

    # --- Handling 'length_of_scan_region' ---
    required_len_cols = ['length_of_scan_region_x', 'length_of_scan_region_y', 'length_of_scan_region_z']
    if all(col in csv_fields.columns for col in required_len_cols):
        def process_length_row(row):
            x_val = safe_numeric_conversion(row['length_of_scan_region_x'])
            y_val = safe_numeric_conversion(row['length_of_scan_region_y'])
            z_val = safe_numeric_conversion(row['length_of_scan_region_z'])

            if x_val and y_val and z_val:
                return [round(x_val, 3), round(y_val, 3), round(z_val, 3)]
            else:
                invalid_components = []
                if not x_val: invalid_components.append('x')
                if not y_val: invalid_components.append('y')
                if not z_val: invalid_components.append('z')
                st.warning(f"Row {row.name}: 'length_of_scan_region' has non-numeric/missing values for {', '.join(invalid_components)}. Setting to None.")
                return [None, None, None]

        df['length_of_scan_region'] = csv_fields.apply(process_length_row, axis=1)

    else:
        st.warning("Required columns for 'length_of_scan_region' (x, y, z) are missing. Setting to None for all rows.")
        df['length_of_scan_region'] = [None, None, None]

    # --- Handling 'voxel_spacing' ---
    required_voxel_cols = ['voxel_spacing_x', 'voxel_spacing_y', 'voxel_spacing_z']
    if all(col in csv_fields.columns for col in required_voxel_cols):
        def process_voxel_row(row):
            x_val = safe_numeric_conversion(row['voxel_spacing_x'])
            y_val = safe_numeric_conversion(row['voxel_spacing_y'])
            z_val = safe_numeric_conversion(row['voxel_spacing_z'])

            if x_val and y_val and z_val:
                return [round(x_val, 3), round(y_val, 3), round(z_val, 3)]
            else:
                invalid_components = []
                if not x_val: invalid_components.append('x')
                if not y_val: invalid_components.append('y')
                if not z_val: invalid_components.append('z')
                st.warning(f"Row {row.name}: 'voxel_spacing' has non-numeric/missing values for {', '.join(invalid_components)}. Setting to None.")
                return [None, None, None]

        df['voxel_spacing'] = csv_fields.apply(process_voxel_row, axis=1)

    else:
        st.warning("Required columns for 'voxel_spacing' (x, y, z) are missing. Setting to None for all rows.")
        df['voxel_spacing'] = [None, None, None]

    return df

def standardize_protocols(df):
    """
    Maps fields from protocols upload to the standard database schema set in column_mappings.py 

    Paramaters:
    df (DataFrame): raw data from protocols upload

    Returns:
    df (DataFrame): standardized dataframe to match db schema
    """
    standard_columns = {key: None for key in study_columns}
    standardized_df = pd.DataFrame([standard_columns] * len(df))
    standardized_df['study_id'] = df['study_ID']
    standardized_df['time_interval_between_scans'] = df['Time points'].astype(str)
    standardized_df['groups'] = df['Control files']
    return standardized_df

def standardize_dcm(dcm_headers):
    """
    Maps fields from dicom image header upload to the standard database schema set in column_mappings.py 

    Paramaters:
    csv_fields (DataFrame): raw data from dicom upload

    Returns:
    df (DataFrame): standardized dataframe to match db schema
    """
    # creating empty standardized dataframe and adding apprpriate values from dcm_headers
    standard_columns = {key:None for key in img_columns}
    df = pd.DataFrame([standard_columns])

    df['scan_date'] = pd.to_datetime(dcm_headers['SeriesDate']).dt.date
    df['file_type'] = dcm_headers['file_type']
    
    df['length_of_scan_region'] = dcm_headers.apply(
        lambda row: [
            round(row["Columns"] * row["PixelSpacing"][0], 3), 
            round(row["Rows"] * row["PixelSpacing"][1], 3),
            None 
            ], 
        axis=1
    )

    if "SliceThickness" in dcm_headers.columns:
        df['voxel_spacing'] = dcm_headers.apply(
            lambda row: [
                round(row["PixelSpacing"][0], 3), 
                round(row["PixelSpacing"][1], 3),
                round(row["SliceThickness"], 3) 
                ], 
            axis=1
        )
    else:
        df['voxel_spacing'] = dcm_headers.apply(
            lambda row: [
                round(row["PixelSpacing"][0], 3), 
                round(row["PixelSpacing"][1], 3),
                None 
                ], 
            axis=1
        )

    if "SeriesDescription" in dcm_headers.columns:
        df['joint_scanned'] = dcm_headers['SeriesDescription']

    df['file_name'] = dcm_headers['file_name']
    if 'PatientAge' in dcm_headers.columns:
        df['age'] = dcm_headers["PatientAge"]
    else: 
        df['age'] = None
    df['study_id'] = dcm_headers['StudyID']

    return df

def standardize_isq(isq_headers):
    """
    Maps fields from isq image headers upload to the standard database schema set in column_mappings.py 

    Paramaters:
    csv_fields (DataFrame): raw data from isq upload

    Returns:
    df (DataFrame): standardized dataframe to match db schema
    """
    # creating empty standardized dataframe and adding apprpriate values from isq_headers
    standard_columns = {key:None for key in img_columns}
    df = pd.DataFrame([standard_columns])

    df['scan_date'] = isq_headers['date']
    df['file_type'] = isq_headers['file_type']

    df['length_of_scan_region'] = isq_headers.apply(
        lambda row: [round(row["total_size_um_x"] * 0.001, 3), round(row["total_size_um_y"] * 0.001, 3), round(row["total_size_um_z"] * 0.001, 3)], 
        axis=1
    )
    df['voxel_spacing'] = isq_headers.apply(
        lambda row: [round(row["pixel_size_um"] * 0.001, 3), round(row["pixel_size_um"] * 0.001, 3), round(row["pixel_size_um"] * 0.001, 3)], 
        axis=1
    )

    # appdend to df
    df['file_name'] = isq_headers['file_name']
    df['age'] = None
    df['study_id'] = isq_headers['scanner_id']

    return df

def standardize_pdf(pdf_fields):
    """
    Maps fields from PDF upload to the standard database schema set in column_mappings.py 

    Paramaters:
    csv_fields (DataFrame): raw data from pdf upload

    Returns:
    df (DataFrame): standardized dataframe to match db schema
    """
    # creating standardized datafram and populating with relevant fields from pdf
    standard_columns = {key:None for key in participant_columns}
    df = pd.DataFrame([standard_columns] * len(pdf_fields))

    df['age'] = pdf_fields.apply(
            lambda row: row['date'].year - row['birth_date'].year - ((row['date'].month, row['date'].day) < (row['birth_date'].month, row['birth_date'].day)),
            axis=1
    )
    df['sex_assigned_at_birth'] = pdf_fields['sex']
    df['weight_kg'] = pd.to_numeric(pdf_fields['weight_kg'], errors='coerce')    
    df['height_cm'] = pd.to_numeric(pdf_fields['height_cm'], errors='coerce')    

    df['scan_date'] = pdf_fields['date']
    df['study_id'] = pdf_fields['study_id']

    return df

def append_institution(df):
    """
    Appends user's institution to the first column in a DataFrame

    Paramaters:
    df (DataFrame): initial DataFrame

    Returns:
    df (DataFrame): updated DataFrame
    """
    try:
        df['institution'] = st.session_state.member_cms["dataItems"][0]["data"]["universityInstitution"]
        first_column = df.pop('institution')  
        df.insert(0, 'institution', first_column)
        return df
    except:
        md = """You must have an University/Institution on you Spectra Member profile. You can update this here: [Update Profile](https://www.spectra-collab.org/members/update)"""
        st.warning(md)
        return None

## DATABASE FUNCTIONS ##

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

def insert_df_into_collection(df, collection_name, page_name):
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

    if "scan_date" in df.columns:
        df["scan_date"] = df["scan_date"].astype(str)

    # searching for duplicates in the "file_name_x" column
    duplicates = pd.DataFrame(collection.find({"composite_id": {"$in":df["composite_id"].tolist()}}))

    # if we find duplicates
    if not duplicates.empty:
        st.warning(f"There are {duplicates.shape[0]} entries that already exist in the collection.")
        duplicates.drop(columns="_id", inplace=True)
        st.write("Existing Data")
        st.write(duplicates)

        searchfor = duplicates["composite_id"].tolist()
        df_duplicates = df[df["composite_id"].str.contains('|'.join(searchfor))]
        st.write("New Data")
        st.write(df_duplicates)

        col1, col2, col3 = st.columns(3)
        col1.button("Keep Existing File in Database", on_click=keep_clicked)
        col2.button("Overwrite Existing File", on_click=overwrite_clicked)
        col3.button("Cancel Upload", on_click=cancel_clicked)

        if st.session_state.keep:
            df_non_duplicates = df[~df["composite_id"].str.contains('|'.join(searchfor))]
            if df_non_duplicates.empty:
                st.session_state.message = f"Keeping Duplicates: Inserted 0 items to database."
            else:
                insert = collection.insert_many(df_non_duplicates.to_dict('records')) # insert all records in the new data
                st.session_state.message = f"Keeping Duplicates: Inserted {len(insert.inserted_ids)} items to database."
            st.session_state.prev_action = page_name
            reset_session_states() # reset states and rerun script, essentially makes it look like the page has refreshed
            st.rerun()

        if st.session_state.overwrite:
            collection.delete_many({"composite_id": {"$in":df["composite_id"].tolist()}}) # delete the duplicates in the db
            try:
                insert = collection.insert_many(df.to_dict('records')) # insert all records in the new data
                st.session_state.prev_action = page_name
                st.session_state.message = f"Overwrote Duplicates: Inserted {len(insert.inserted_ids)} items to database."
            except Exception as e:
                st.write("Something went wrong...")
                st.write(e)
            reset_session_states()
            st.rerun()

        if st.session_state.cancel:
            st.session_state.prev_action = page_name
            st.session_state.message = f"Cancelled Data Upload"
            reset_session_states()
            st.rerun()
    
    # if there are no duplicates, we can go straight to uploading
    else:
        try:
            insert = collection.insert_many(df.to_dict('records')) # insert all new records into db
            st.session_state.message = f"No Duplicates Found: Inserted {len(insert.inserted_ids)} items to database!"
            st.session_state.prev_action = page_name
            reset_session_states()
            st.rerun()
        except Exception as e:
            st.write("Something went wrong...")
            st.write(e)

