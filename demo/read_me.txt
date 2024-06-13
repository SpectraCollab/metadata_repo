In this folder you find a demo simulating various SPECTRA centers from which you want to merge information about protocols, subjects, and images.

We assume that:
- Protocol information are entered manually in a tabular file. This is a rare event that can be done manually
- Image information are automatically extracted from image headers
- Subject information and protocol do *not* correspond to reality, but are plausible

Note: In the following, the words tabular format, tabular data, and dataframe are used to indicate data in a table (e.g. same as excel)


Folder content
--------------
The folder contains: 

-> protocols: 
It contains the file:
- protocols.xlsx. Each row corresponds to a potential study. Content is partially derived from SPECTRA protocols. It would be useful to add urls of protocol and transmittal form location for consultation 

-> images: It contains:
- The folder:
   - images: folder containing subfolders, each of them containing images from a specific site 
- Files relative to each site. For the site 3300 (the same files are present for the site 3309):
  - images_3300.ipynb: Notebook collecting the headers of the images and saving them in tabular format 
  - images_3300.csv: File containing the image headers in a tabular format
  - images_3300.html: HTML version of the notebook images_3300.ipynb for fast consultation 
- Files merging information from various sites:
  - images_merge.ipynb: Notebook merging image information coming from various sites in a single table 
  - images_info.csv: File containing merged information from the different sites  
  - images_merge.html: HTML version of the notebook images_merge.ipynb for fast consultation 

-> subjects: It contains 
- The folders:
  - forms: It contains:
    - transmittal_3300_fillable.pdf and transmittal_3309_fillable.pdf. Each file corresponds to a fictitious transmittal form that can be filled out by an operator during acquisition
    - create_fillable_pdf.txt: It contains some resources on how to create a fillable form 
  - subjects: folder containing subfolders, each of them containing fictitious transmittal forms from a specific site. Each form correspond to an image in the folder ./images/images
- Files relative to each site. For the site 3300 (the same files are present for the site 3309):
  - subjects_3300.ipynb: Notebook collecting the information from filled .pdf and saves them in a tabular format
  - subjects_info_3300.csv: File containing the subjects' information in a tabular format
  - subjects_3300.html: HTML version of the notebook subjects_3300.ipynb for fast consultation
- Files merging information from various sites:
  - subjects_merge.ipynb: Notebook merging subject information coming from various sites in a single table 
  - subjects_info.csv: File containing merged information from the different sites
  - subjects_merge.html: HTML version of the notebook subjects_merge.html for fast consultation 

-> merge_and_query.ipynb: Notebook merging subject information, protocols, and image information coming from various sites in a single table. It also contains examples of queries
-> dataset_info.csv: File containing the dataset information. Each row corresponds to an image, and it contains all information about subject, protocol, and image header


Limitations
-----------
- The whole code in written in Jupyter notebooks, which are convenient for prototyping. However, it will be very straight forward to create python scripts and call them all at once, instead of running various notebook. 
- Subject information usually derive from recruitment forms (e.g. containing medical history) and transmittal forms (acquisition record). In this demo, the two forms are joined in one for simplicity


Future steps
------------
- Standardize minimum required entries for protocol and subject information. 
- Standardize .pdf form field names, especially the replicated ones that can make merging and queries more complicated (e.g. meas_no_1, meas_no_2, meas_no_3, each corresponding to a different data point)

