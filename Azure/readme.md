# Azure Asset Counter

This script is designed to count assets across all subscriptions and resource groups in Azure, handling rate limits and permissions. It leverages Azure CLI commands and Python's concurrency features to efficiently list and count assets. The results are logged and written to a file.

## Features

- Lists all subscriptions using Azure CLI.
- Lists all resource groups within each subscription.
- Counts specified types of assets in each resource group.
- Handles rate limiting and permission errors.
- Outputs detailed logs and a summary of asset counts.

## Requirements

- Python 3.6 or higher
- Azure CLI installed and configured
- Required Python packages: `subprocess`, `json`, `argparse`, `time`, `tqdm`, `logging`, `concurrent.futures`

## Installation

1. Ensure you have Python 3.6 or higher installed.
2. Install Azure CLI if not already installed: [Azure CLI Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. Install the required Python packages using pip:

    ```bash
    pip install tqdm
    ```

4. Clone or download this repository to your local machine.

## Usage

1. Create a file containing the asset types to be checked. Each line in the file should represent a different asset type.

    Example `assets.txt`:

    ```
    Microsoft.Compute/virtualMachines
    Microsoft.Storage/storageAccounts
    ```

2. Run the script with the following command:

    ```bash
    python script_name.py assets.txt
    ```

3. To enable debug output for more verbose information, use the `--debug` flag:

    ```bash
    python script_name.py assets.txt --debug
    ```

## Script Details

### Functions

- **setup_logging(debug)**: Configures logging settings based on the debug flag.
- **run_command(command)**: Executes a shell command and returns the output, errors, and return code.
- **list_subscriptions()**: Lists all subscriptions using Azure CLI.
- **list_resource_groups(subscription_id)**: Lists all resource groups in a given subscription.
- **handle_assets(subscription_id, resource_group, asset_type)**: Lists assets and handles rate limiting and permission errors.
- **process_asset(subscription_id, resource_group, asset_type)**: Processes an asset, returning the count and any errors.
- **main(asset_file, debug)**: Main function that orchestrates the asset counting process.

### Logging

Logs are written to `debug.log` with different levels of verbosity based on the debug flag.

### Output

- A detailed log file (`debug.log`).
- A summary file (`asset_count.txt`) containing counts of each asset type per resource group and subscription, along with a grand total of all assets.

## Example Output

subscription_id/resource_group: Microsoft.Compute/virtualMachines - Count: 10
subscription_id/resource_group: Microsoft.Storage/storageAccounts - Count: 5