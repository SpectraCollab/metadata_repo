import streamlit as st
import pymongo
import pandas as pd

def add_to_db_button_clicked():
    st.session_state.add_to_db_button = True

def keep_clicked():
    st.session_state.keep = True

def overwrite_clicked():
    st.session_state.overwrite = True

def cancel_clicked():
    st.session_state.cancel = True

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
            st.session_state.prev_action = page_name
            st.session_state.message = f"Keeping Duplicates: Inserted ... items to database."
            reset_session_states() # reset states and rerun script, essentially makes it look like the page has refreshed
            st.rerun()

        if st.session_state.overwrite:
            collection.delete_many({"file_name_x": {"$in":df["file_name_x"].tolist()}}) # delete the duplicates in the db
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
