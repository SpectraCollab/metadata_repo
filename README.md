# SPECTRA Image Metadata Repository

## Table of Contents
1. [Background](#1-background)
2. [Intended Usage](#2-intended-usage)
3. [Contributing](#3-contributing)

## 1. Background

Gathering medical images for research is a long, tedious task. Many institutions possess images that are highly relevant to other institutions' research areas, however, there is currently no convenient way to share information cross-institutionally about who was what kind of images. The SPECTRA Collaboration has pioneered development of an image metadata repository to share relevant metadata of their images with other members of the SPECTRA Collaboration in hopes to increase collaboration and image sharing between institutions.

## 2. Intended Usage

#### a). Navigate to the following link:

[https://repository.spectra-collab.org/](https://repository.spectra-collab.org/)

#### b). Login with Spectra Collaboration Credentials

You will be redirected to the login page of the [Spectra Collaboration Main Site](https://spectra-collab.org/) where you will be prompted to login with your Spectra member credentials. 

If you are NOT currently a member of the Spectra Collaboration you must sign up through the main site and be approved by the Spectra Admin team.

#### c). Site Usage

Refer to [Usage Instruction and FAQ Powerpoint](https://docs.google.com/presentation/d/1BybJdAy9LMRceH0rDgo4Mpslq9Jl4nNr/edit?usp=drive_link&ouid=100577848524603341913&rtpof=true&sd=true) for any questions regarding how to upload data or the meaning of any tables on the site.

## 3. Contributing

### Running the StreamLit Web App Locally for Development
#### a). Install the "spectra_repo" Anaconda Environment:
Ensure your terminal is in the /metadata_repo directory, then run:

`conda env create -f environment.yaml`

If using an Apple processor, run the following command instead:

`CONDA_SUBDIR=osx-64 conda env create -f environment.yaml`

#### b). Activate the Anaconda Environment:
`conda activate spectra_repo`

#### c). Add secrets file:
In order for the app to connect to the database, you need to manually add a file containing the MongoDB connection string. This file is hidden from the repository.

1.  Once in the /metadata_repo directory:

2.  Copy your "secrets.toml" to this directory (ie. .streamlit/secrets.toml)

    `cp <path_to_secrets.toml>/secrets.toml <path_to_repository>/.streamlit`

    Example: `cp Downloads/secrets.toml Documents/metadata_repo/.streamlit`

#### d). Run the app:
Run the command:

`streamlit run myApp.py`

The webpage should automatically open on your default browser. **(Note, if it is your first time using Streamlit, you may be prompted to enter your email. You don't have to. Instead just leave the email field blank and press enter)**

### Pushing Changes to the Google Cloud Run App

Once changes have been pushed to the main branch of this repository. Please contact Chris Brunet for instructions on pushing changes to Google Cloud.

