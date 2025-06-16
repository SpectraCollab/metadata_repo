import streamlit as st
import pandas as pd
import utils.streamlit_utils as stutil
import utils.file_reader

print("\n\timage_upload")
stutil.print_states()
"""#### Upload Image and PDF

Drag and drop one or many images and participant transmittals to have the metadata automatically extracted and merged. Try it out with the demo data in the Google Drive link below:

"""

st.link_button("Demo Files", 'https://drive.google.com/drive/folders/1Hkk2Coo7mfz6Xl-4MKItVvJxCxbEKw_D?usp=sharing_eip&ts=66c50ec3')

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

    if st.session_state.img_df['scan_date'].isna().any() or st.session_state.img_df['file_type'].isna().any():
        st.warning("Image headers must contain scan_date and file_name. One or more images are missing this info.")
        st.session_state.img_df = None

    if st.session_state.img_df is not None:
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
            filenames = [subject.name.split(".")[0] for subject in uploaded_subjects]
            st.session_state.pdf_df['file_name'] = filenames
    else:
        print("PDFs detected... reading images")
        st.session_state.pdf_df = utils.file_reader.pdf_to_df(uploaded_subjects)
        filenames = [subject.name.split(".")[0] for subject in uploaded_subjects]
        st.session_state.pdf_df['file_name'] = filenames

    if st.session_state.pdf_df['age'].isna().any() or st.session_state.pdf_df['sex_assigned_at_birth'].isna().any() or st.session_state.pdf_df['weight_kg'].isna().any():
        st.warning("All transmittals must contain age, sex_assigned_at_birth, weight_kg and file_name. One or more transmittals is missing this info.")
        st.session_state.pdf_df = None

    if st.session_state.pdf_df is not None:
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
        if merged_df.shape[0] == 0:
            st.warning("Unable to merge datasets. Ensure files are named appropriately.")
        else: 
            # Writing new rows to database    
            merged_df = stutil.append_institution(merged_df)
            if merged_df is not None:
                merged_df = stutil.create_composite_id(merged_df)
                st.write(merged_df)
                st.button("Add to Database", on_click=stutil.add_to_db_button_clicked)

                if st.session_state.add_to_db_button:
                    stutil.insert_df_into_collection(merged_df, "allData", "isq")
    else:
        st.warning("Unable to merge datasets. Ensure files are named appropriately.")


"""
#### How to use the Image Uploader

- **IMPORTANT**: to successfully merge Image and Transmittal data, each corresponding file must end with the same numerical value and an underscore ("_") prior to that value (ie. "image_1.dcm" & "transmittal_1.pdf")

- Currently the supported file types are .ISQ, .DCM

- When using a DCM image series, please only upload the **LAST** image in the series

- One PDF transmittal matching that of the Transmittal Template must be uploaded for each image file

- Fields from the respective Study IDs are concatenated to the data entry from the **Protocols Table** based on the Study ID of the Transmittal 

"""