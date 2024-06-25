import os
import struct
import datetime

def read_isq_header(isq_file):


    """
    This function reads an .isq file header and returns its content as two lists of strings: "keys" and "values"
    The list "keys" contains the data labels (e.g. pixel_size_um).
    The list "value" contains the actual values (e.g. 82)
    The keys are from the Scanco documentation at http://www.scanco.ch/en/support/customer-login/faq-customers.html, under "general" -> "ISQ Header format"

    Input:
        - isq_file_name: name of the isq file (type: str)
    Outputs:
        - keys: contains the data labels (type: list of strings)
        - values: contains the actual values (type: list of strings)
    """

    # check that files exists
    # if the file does not exist, print error to screen and stop the function
    # if not os.path.exists(isq_file_name):
    #     print("----------------------------------------------------------------------------------------")
    #     print("ERROR: The file %s does not exist" % (isq_file_name) )
    #     print("----------------------------------------------------------------------------------------")
    #     return

    # # check that the file contains .isq in its extension (sometimes files are save as .isq;1, etc.)
    # name, extension = os.path.splitext(isq_file_name)
    # extension = extension.lower() # sometimes the extension is in capital letters
    # if ".isq" not in extension:
    #     print("----------------------------------------------------------------------------------------")
    #     print("ERROR: The file %s does not have .isq extension" % (isq_file_name) )
    #     print("----------------------------------------------------------------------------------------")
    #     return

    # # check if you can open the file
    # # if you cannot open the file, print error to screen and stop the function
    # try:
    #     file = open(isq_file_name, "rb")
    # except:
    #     print("----------------------------------------------------------------------------------------")
    #     print("ERROR: Cannot open the file" % (isq_file_name) )
    #     print("----------------------------------------------------------------------------------------")
    #     return

    file = isq_file

    # initialize the output lists
    values = []
    keys   = []

    # read the header

    # char check[16]
    keys.append("check")
    len_check = 16
    check = ""
    for i in range(0,len_check):
        check = check + struct.unpack('c',file.read(1))[0].decode("utf-8") # read and concatenate the 16 chars
    values.append(check)

    # int data_type
    keys.append("data_type")
    values.append(struct.unpack('i',file.read(4))[0])

    # int nr_of_bytes
    keys.append("nr_of_bytes")
    values.append(struct.unpack('i',file.read(4))[0])

    # int nr_of_blocks
    keys.append("nr_of_blocks")
    values.append(struct.unpack('i',file.read(4))[0])

    # int patient_index
    keys.append("pat_no")
    values.append(struct.unpack('i',file.read(4))[0])

    # int scanner_id
    keys.append("scanner_id")
    values.append(struct.unpack('i',file.read(4))[0])

    # int creation_date[2]
    keys.append("date")
    date_in_VMS = struct.unpack('Q',file.read(8))[0]    # time since 17th Nov 1858 (for OpenVMS systems)
    date_in_unix = date_in_VMS / 10000 - 3506716800000  # time since 1st Jan 1970 (for Unix systems)
    date_in_unix_sec = date_in_unix / 1000              # from ms to seconds
    values.append(datetime.datetime.fromtimestamp(date_in_unix_sec).strftime('%Y_%m_%d')) # keep only day, not time

    # int dimx_p
    keys.append("n_voxels_x")
    values.append(struct.unpack('i',file.read(4))[0])

    # int dimy_p
    keys.append("n_voxels_y")
    values.append(struct.unpack('i',file.read(4))[0])

    # int dimz_p
    keys.append("n_voxels_z")
    values.append(struct.unpack('i',file.read(4))[0])

    # int dimx_um
    keys.append("total_size_um_x")
    values.append(struct.unpack('i',file.read(4))[0])

    # int dimy_um
    keys.append("total_size_um_y")
    values.append(struct.unpack('i',file.read(4))[0])

    # int dimz_um
    keys.append("total_size_um_z")
    values.append(struct.unpack('i',file.read(4))[0])

    # int slice_thickness_um
    keys.append("slice_thickness_um")
    values.append(struct.unpack('i',file.read(4))[0])

    # int slice_increment_um
    keys.append("pixel_size_um")
    values.append(struct.unpack('i',file.read(4))[0])

    # int slice_1_pos_um
    keys.append("slice_1_pos_um")
    values.append(struct.unpack('i',file.read(4))[0])

    # int min_data_values
    keys.append("min_intensity")
    values.append(struct.unpack('i',file.read(4))[0])

    # int max_data_values
    keys.append("max_intensity")
    values.append(struct.unpack('i',file.read(4))[0])

    # int mu_scaling (p(x,y,z)/mu_scaling = value [1/cm])
    keys.append("mu_scaling")
    values.append(struct.unpack('i',file.read(4))[0])

    # int nr_of_samples
    keys.append("nr_of_samples")
    values.append(struct.unpack('i',file.read(4))[0])

    # int nr_of_projections
    keys.append("nr_of_projections")
    values.append(struct.unpack('i',file.read(4))[0])

    # int scandist_um
    keys.append("scan_dist_um")
    values.append(struct.unpack('i',file.read(4))[0])

    # int scanner_type
    keys.append("scanner_type")
    values.append(struct.unpack('i',file.read(4))[0])

    # int sampletime_us
    keys.append("exposure_time")
    values.append(struct.unpack('i',file.read(4))[0])

    # int index_measurement
    keys.append("meas_no")
    values.append(struct.unpack('i',file.read(4))[0])

    # int site
    keys.append("site")
    values.append(struct.unpack('i',file.read(4))[0])

    # int reference_line_um
    keys.append("reference_line_um")
    values.append(struct.unpack('i',file.read(4))[0])

    # int recon_alg
    keys.append("recon_algo")
    values.append(struct.unpack('i',file.read(4))[0])

    # char name[40]
    keys.append("pat_name")
    len_pat_name = 40
    pat_name = ""
    for i in range(0,len_pat_name):
        pat_name = pat_name + struct.unpack('c',file.read(1))[0].decode("utf-8") # read and concatenate the 16 chars
    values.append(pat_name)

    # int energy (V)
    keys.append("energy_V")
    values.append(struct.unpack('i',file.read(4))[0])

    # int intensity (uA)
    keys.append("intensity_uA")
    values.append(struct.unpack('i',file.read(4))[0])

    # int fill[83]
    keys.append("fill")
    fill = []
    len_fill = 83
    for i in range (0, len_fill):
        fill.append(struct.unpack('i',file.read(4))[0])
    values.append(str(fill))

    # int data_offset (in 512-byte-blocks)
    keys.append("data_offset")
    values.append(struct.unpack('i',file.read(4))[0])


    return keys, values