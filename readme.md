# Cloud Asset Counter

The goal of this project is to count assets in various cloud environments, handling rate limits and permissions effectively. This project includes scripts for both Azure and Google Cloud Platform (GCP).

## Scripts

### Azure Asset Counter

This script counts assets across all subscriptions and resource groups in Azure, leveraging Azure CLI commands and Python's concurrency features.

#### Usage

1. Create a file containing the asset types to be checked. Each line in the file should represent a different asset type.

    Example `assets.txt`:

    ```
    Microsoft.Compute/virtualMachines
    Microsoft.Storage/storageAccounts
    ```

2. Run the script with the following command:

    ```bash
    python azure_asset_counter.py assets.txt
    ```

3. To enable debug output for more verbose information, use the `--debug` flag:

    ```bash
    python azure_asset_counter.py assets.txt --debug
    ```

For more information, refer to the [Azure Asset Counter README](azure_asset_counter/README.md).

### GCP Asset Counter

This script counts assets across all projects within a specified Google Cloud Platform (GCP) organization, handling API limits and permissions.

#### Usage

1. Create a file containing the asset types to be checked. Each line in the file should represent a different asset type.

    Example `assets.txt`:

    ```
    compute.googleapis.com/Instance
    storage.googleapis.com/Bucket
    ```

2. Run the script with the following command:

    ```bash
    python gcp_asset_counter.py <org_id> assets.txt
    ```

3. To enable debug output for more verbose information, use the `--debug` flag:

    ```bash
    python gcp_asset_counter.py <org_id> assets.txt --debug
    ```

For more information, refer to the [GCP Asset Counter README](gcp_asset_counter/README.md).
