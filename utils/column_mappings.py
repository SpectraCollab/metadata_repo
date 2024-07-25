# following columns NOT in delphi: study_id, scan_date, institution, file_type 
# spatial_resolution was substituted for voxel_spacing
participant_columns = [
    'age',
    'sex_assigned_at_birth',
    'weight_kg',
    'height_cm',
    'disease_status',
    'smoking_status',
    'current_treatment',
    'bone_alterting_meds',
    'conventional_DMARDS',
    'biological_DMARDS',
    'steroid_use',
    'motion_score',
    'description_of_hand_scanned',
] # in image reader, we append scan_date and study_id to use as join keys

study_columns = [
    'study_id',
    'time_interval_between_scans',
    'groups',
]

img_columns = [
    'scan_date',
    'file_type',
    'joint_scanned',
    'length_of_scan_region',
    'voxel_spacing',
] # in image reader, we append age, file_name, and study_id to use as join keys