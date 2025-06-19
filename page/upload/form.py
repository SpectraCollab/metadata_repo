import streamlit as st
import pandas as pd
import utils.streamlit_utils as stutil

from utils.column_mappings import participant_columns, study_columns, img_columns

print("\n\tfillable_form")
stutil.print_states()
"""#### Fillable Form

Manually add subject level data. Users may append study protocols to the entry by selecing the appropriate study from the **Study ID** dropdown."""

if 'form_df' not in st.session_state:
    st.session_state.form_df = False

# Used to display the previous action that occured after the page was rerun
if st.session_state.prev_action == 'form':
    st.warning(st.session_state.message)

protocols = stutil.get_collection("protocols")
protocol_dict = {}
protocols_df = pd.DataFrame(protocols.find({}))
study_ids = protocols_df['study_ID'].unique().tolist()

participant_fields = {key:None for key in participant_columns}
study_fields = {key:None for key in study_columns}
img_fields = {key:None for key in img_columns}

st.header("Add Image Metadata")
with st.form("Manual Form", clear_on_submit=False):

    with st.expander("Patient Details*"):
        participant_fields['age'] = st.number_input("Age*", step=1)
        participant_fields['sex_assigned_at_birth'] = st.radio("Sex Assigned at Birth*", ["M", "F", "Other"])
        participant_fields['weight_kg'] = st.number_input("Weight (kg)*")
        participant_fields['height_cm'] = st.number_input("Height (cm)")
        participant_fields['disease_status'] = st.text_input("Disease Status")
        participant_fields['smoking_status'] = st.radio("Smoking Status", ["Y", "N"])
        participant_fields['current_treatment'] = st.text_input("Current Treatment")
        participant_fields['bone_alterting_meds'] = st.radio("Bone Altering Meds", ["Y", "N"])
        participant_fields['conventional_DMARDS'] = st.radio("Conventional DMARDS", ["Y", "N"])
        participant_fields['biological_DMARDS'] = st.radio("Biological DMARDS", ["Y", "N"])
        participant_fields['steroid_use'] = st.radio("Steriod Use", ["Y", "N"])
        participant_fields['motion_score'] = st.number_input("Motion Score")
        participant_fields['description_of_hand_scanned'] = st.text_input("Description of Hand Scanned")

    with st.expander("Study Details*"):
        study_fields['study_id'] = st.selectbox("Study ID*", study_ids)
        study_fields['time_interval_between_scans'] = st.text_input("Time Interval Between Scans")
        study_fields['groups'] = st.text_input("Groups")

    with st.expander("Image Details*"):
        img_fields['scan_date'] = st.date_input("Scan Date*", value=None)
        img_fields['file_type'] = st.text_input("File Type")
        img_fields['joint_scanned'] = st.text_input("Joint Scanned")
        col1, col2, col3 = st.columns(3)
        length_x = col1.number_input("Length of Scan Region: x")
        length_y = col2.number_input("Length of Scan Region: y")
        length_z = col3.number_input("Length of Scan Region: z")
        voxel_x = col1.number_input("Voxel Spacing: x")
        voxel_y = col2.number_input("Voxel Spacing: y")
        voxel_z = col3.number_input("Voxel Spacing: z")

    "---"

    # Submit/reset buttons
    submitted = st.form_submit_button("Submit Form")

    if submitted:
        # Basic completion checking
        if (participant_fields["age"] == 0) or (participant_fields["weight_kg"] == 0) or (study_fields["study_id"] == "-") or (img_fields["scan_date"] == None):
            st.warning("Please Fill In Required Fields. Required fields are: Age, Sex Assigned At Birth, Weight, Study ID, Scan Date")
        else:
            img_fields['length_of_scan_region'] = [length_x, length_y, length_z]
            img_fields['voxel_spacing'] = [voxel_x, voxel_y, voxel_z]

            participant_df = pd.DataFrame([participant_fields])
            study_df = pd.DataFrame([study_fields])
            img_df = pd.DataFrame([img_fields])
            participant_study_df = pd.concat([participant_df, study_df], axis=1)
            st.session_state.form_df = pd.concat([participant_study_df, img_df], axis=1)


# displaying data and adding to database
if isinstance(st.session_state.form_df, pd.DataFrame):
    if not st.session_state.form_df.empty:
        st.session_state.form_df = stutil.append_institution(st.session_state.form_df)
        if st.session_state.form_df is not None:
            st.session_state.form_df = stutil.create_composite_id(st.session_state.form_df)
            st.write(st.session_state.form_df)
            st.button("Add to Database", on_click=stutil.add_to_db_button_clicked)
            if st.session_state.add_to_db_button:
                stutil.insert_df_into_collection(st.session_state.form_df, "allData", "form")


f"""
#### How to use the Form Uploader

- Image metadata can only be uploaded one image at a time

- **Required fields** are: Age, Sex Assigned At Birth, Weight, Study ID, Scan Date

- If you do not have information for a non-required field, you can leave it blank

- Selecting "Study ID" will concatenate fields "time_interval_between_scan" and "groups" from the respective study in the **Protocols Table** to the entry

"""