## Running the StreamLit Web App Locally for Development
### Step 1: Install the "spectra_repo" Anaconda Environment:
Ensure your terminal is in the /metadata_repo directory, then run:

`conda env create -f environment.yaml`

If using an Apple M1, M2, or M3 processor, run the following command instead:

`CONDA_SUBDIR=osx-64 conda env create -f environment.yaml`

### Step 2: Activate the Anaconda Environment:
`conda activate spectra_repo`

### Step 3: Add secrets file:
In order for the app to connect to the database, you need to manually add a file containing the MongoDB connection string. This file is hidden from the repository.

&nbsp;&nbsp;&nbsp;&nbsp;a. Once in the /metadata_repo directory:

&nbsp;&nbsp;&nbsp;&nbsp;b. Copy your "secrets.toml" to this directory (ie. .streamlit/secrets.toml)

&nbsp;&nbsp;&nbsp;&nbsp;`cp <path_to_secrets.toml>/secrets.toml <path_to_repository>/.streamlit`

&nbsp;&nbsp;&nbsp;&nbsp;Example: `cp Downloads/secrets.toml Documents/metadata_repo/.streamlit`

### Step 4: Run the app:
Run the command:

`streamlit run myApp.py`

The webpage should automatically open on your default browser. **(Note, if it is your first time using Streamlit, you may be prompted to enter your email. You don't have to. Instead just leave the email field blank and press enter)**

## Running the StreamLit Web App Hosted by Google Cloud Run
### Step 1: Navigate to the following link:

[https://repository.spectra-collab.org/](https://repository.spectra-collab.org/)
