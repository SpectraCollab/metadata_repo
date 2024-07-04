import streamlit as st
import pandas as pd
import utils.streamlit_utils as stutil
import utils.file_reader

print("\n\timage_upload")
stutil.print_states()
"""#### Upload Image and PDF

Users have the option to upload batches of images and PDFs which can automatically be parsed for relevant metadata. 
This option comes with increased complexity regarding security and server performance."""

if 'isq_df' not in st.session_state:
    st.session_state.isq_df = False
if 'pdf_df' not in st.session_state:
    st.session_state.pdf_df = False

if st.session_state.prev_action == "isq":
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
protocols = stutil.get_collection("protocols")
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
        st.button("Add to Database", on_click=stutil.add_to_db_button_clicked)

        if st.session_state.add_to_db_button:
            stutil.insert_df_into_collection(merged_df, "allData", "isq")