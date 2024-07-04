import streamlit as st
import pandas as pd
import utils.streamlit_utils as stutil

print("\n\tfillable_form")
stutil.print_states()
"""#### Fillable Form

Users may have the option to manually add metadata at the subject level. This method maximizes simplicity while sacrificing ability to easily upload multiple subjects."""

if 'form_df' not in st.session_state:
    st.session_state.form_df = False
if 'study_change' not in st.session_state:
    st.session_state.study_change = False

# Used to display the previous action that occured after the page was rerun
if st.session_state.prev_action == 'form':
    st.warning(st.session_state.message)

def study_change():
    st.session_state.study_change = True

protocols = stutil.get_collection("protocols")
protocol_dict = {}

st.header("Add Image Metadata")

file_name = st.text_input("File Name*")
date_recorded = st.date_input("Date Recorded*")
study_id = st.selectbox("Study ID*", ["-", "3300_SPECTRA", "3309_HAND"], on_change=study_change)

if st.session_state.study_change:
    if study_id != "-":
        query = protocols.find({"study_ID": study_id})
        match = pd.DataFrame(query)
        match.drop(columns="_id", inplace=True)
        protocol_dict = match.to_dict('records')[0]
        print(protocol_dict)
        st.write(match)

scanner_id = st.selectbox("Scanner ID*", ["-", "3300", "3309"])
min_intensity = st.number_input("Min Intensity", value=-1000)
max_intensity = st.number_input("Max Intensity", value=10000)

"---"

# Submit/reset buttons
submitted = st.button("Submit Form")

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
        if len(protocol_dict) > 0:
            entered_fields.update(protocol_dict)
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
        st.button("Add to Database", on_click=stutil.add_to_db_button_clicked)
        if st.session_state.add_to_db_button:
            stutil.insert_df_into_collection(st.session_state.form_df, "allData", "form")