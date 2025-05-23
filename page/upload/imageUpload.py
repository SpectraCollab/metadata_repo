import streamlit as st
import pandas as pd
import utils.streamlit_utils as stutil
import utils.file_reader

print("\n\timage_upload")
stutil.print_states()
"""#### Upload Image and PDF

Drag and drop one or many images and participant transmittals to have the metadata automatically extracted and merged. Try it out with the demo data in the OneDrive link below:

[Demo Files](https://drive.google.com/drive/folders/1Hkk2Coo7mfz6Xl-4MKItVvJxCxbEKw_D?usp=sharing_eip&ts=66c50ec3)
"""

def process_images(uploaded_images):
    """
    Enumerates through each file in uploaded images and maps columns to standard dataframe in img_df

    Parameters:
    uploaded_images (list(Uploaded_File)): Data to be processed

    Returns:
    None
    """
    for i, file in enumerate(uploaded_images):
        fileName = file.name
        fileType = fileName.split(".")[1].lower()
        if fileType == 'dcm':
            standardized_data = utils.file_reader.dcm_to_df([file])
            if i == 0:
                st.session_state.img_df = standardized_data
            else: 
                st.session_state.img_df = pd.concat([st.session_state.img_df, standardized_data], ignore_index=True)
        elif fileType == 'isq' or fileType == "isq;1":
            standardized_data = utils.file_reader.isq_to_df([file])
            if i == 0:
                st.session_state.img_df = standardized_data
            else: 
                st.session_state.img_df = pd.concat([st.session_state.img_df, standardized_data], ignore_index=True)
            st.session_state.img_df['scan_date'] = pd.to_datetime(st.session_state.img_df['scan_date'], format='%Y_%m_%d').dt.date
        else:
            st.error("Unrecognized File Type")
            return None
    first_column = st.session_state.img_df.pop('scan_date')  
    st.session_state.img_df.insert(0, 'scan_date', first_column) 

if 'img_df' not in st.session_state:
    st.session_state.img_df = False
if 'pdf_df' not in st.session_state:
    st.session_state.pdf_df = False

# Used to display a message based on the previous action of the user (ie. user uploaded data, cancelled upload, etc)
if st.session_state.prev_action == "isq":
    st.warning(st.session_state.message)

images_loaded = False
subjects_loaded = False
protocols_loaded = False

col1, col2 = st.columns([0.5, 0.5])
# Image Upload Section
col1.header("""Upload Images""")
uploaded_images = col1.file_uploader("Accepted File Types: ISQ, DCM", accept_multiple_files=True, key=st.session_state.isq_uploader_key)
# uploaded_images = col1.file_uploader("Accepted File Types: ISQ, DCM", type=['.isq', '.isq;1', 'dcm', 'dcm;1'], accept_multiple_files=True, key=st.session_state.isq_uploader_key)
if uploaded_images != []:
    if isinstance(st.session_state.img_df, pd.DataFrame):
        if st.session_state.img_df.shape[0] == len(uploaded_images):
            print("Images already read and number has not changed")
        else:
            print("Number of images has changed... Re-reading images")
            process_images(uploaded_images)
    else:
        print("Images detected... reading images")
        process_images(uploaded_images)

    col1.write(st.session_state.img_df)
    images_loaded = True

# Study Upload Section
col2.header("""Upload Subjects""")
uploaded_subjects = col2.file_uploader("Accepted File Types: PDF", type=['pdf'], accept_multiple_files=True, key=st.session_state.pdf_uploader_key)
if uploaded_subjects != []:
    if isinstance(st.session_state.pdf_df, pd.DataFrame):
        if st.session_state.pdf_df.shape[0] == len(uploaded_subjects):
            print("PDFs already read and number has not changed")
        else:
            print("Number of PDFs has changed... Re-reading PDFs")
            st.session_state.pdf_df = utils.file_reader.pdf_to_df(uploaded_subjects)
    else:
        print("PDFs detected... reading images")
        st.session_state.pdf_df = utils.file_reader.pdf_to_df(uploaded_subjects)

    col2.write(st.session_state.pdf_df)
    subjects_loaded = True

# Fetching Protocols
protocols = stutil.get_collection("protocols")
protocols_df_raw = pd.DataFrame(protocols.find({}))
if not protocols_df_raw.empty:
    protocols_df = stutil.standardize_protocols(protocols_df_raw)
    protocols_loaded = True

# Merging Uploaded Data
if images_loaded and subjects_loaded and protocols_loaded:

    merged_df = stutil.merge_dataframes(st.session_state.pdf_df, protocols_df, st.session_state.img_df)

    st.header("Merged Dataset")
    if isinstance(merged_df, pd.DataFrame):
        # Writing new rows to database    
        merged_df = stutil.append_institution(merged_df)
        merged_df = stutil.create_composite_id(merged_df)
        st.write(merged_df)
        st.button("Add to Database", on_click=stutil.add_to_db_button_clicked)

        if st.session_state.add_to_db_button:
            stutil.insert_df_into_collection(merged_df, "allData", "isq")
    else:
        st.write("Unable to merge datasets")