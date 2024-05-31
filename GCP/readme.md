# GCP Asset Counter Script

This script counts GCP assets across all projects within a specified Google Cloud Platform (GCP) organization. It handles rate limiting and permission issues gracefully, providing detailed logs and a summary of the results.

## Summary

The `gcp_assets_byType_v1.py` script is designed to count various types of assets in all projects under a specified GCP organization. The results, including any errors encountered, are logged and a summary is provided at the end of the execution.

## Prerequisites

Before running the script, ensure you have the following:

1. **Python 3.6 or higher**: Check your Python version using `python3 --version`.
2. **Google Cloud SDK**: Install and initialize the Google Cloud SDK. Follow the [installation guide](https://cloud.google.com/sdk/docs/install) if you haven't already done so.
3. **Google API Client Libraries**: Install the required Python libraries using `pip`.

## Installation

1. **Clone the repository** (if applicable):
   ```bash
   git clone https://github.com/your-repo/gcp-asset-counter-script.git
   cd gcp-asset-counter-script

2.	**Install the required Python libraries:**
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib tqdm

3.	**Authenticate with Google Cloud:**
Ensure you are authenticated with your Google Cloud account. Run:
    ```gcloud auth application-default login

## Usage

1.	**Prepare the Asset Types file:**
Use the included asset_types.txt file to scan for all listed asset_types

2.	**Run the script:**
Use the following command to run the script, specifying your organization ID and the path to your Asset Types file:
    python3 gcp_assets_byType_v1.py <org_id> <asset_file> [--debug]

Example Command:
python3 gcp_assets_byType_v1.py 11111222233334 asset_types.txt --debug

## Outputs

1.	**Console Output:**
	•	A progress bar that shows the status of asset counting.
	•	A summary of asset counts per project and the grand total at the end of the execution.
2.	**Files:**
	•	asset_count.txt: Contains detailed counts of each asset type per project and a summary of the total assets.
	•	debug.log: Contains detailed logs of the script’s execution, including any errors encountered. This file is always generated, but more detailed logs are included when the --debug flag is used.

## Logging and Error Handling

	•	Debug Log: Detailed logs are written to debug.log for every run.
	•	Permission and API Errors: Errors related to permissions or APIs not being enabled are logged and handled gracefully, allowing the script to continue counting other assets.
