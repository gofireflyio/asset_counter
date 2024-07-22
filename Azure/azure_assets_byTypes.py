import subprocess
import json
import argparse
import time
from tqdm import tqdm
import logging
import concurrent.futures

def setup_logging(debug):
    """ Set up logging configuration """
    logging.basicConfig(filename='debug.log', level=logging.DEBUG if debug else logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    if debug:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

def run_command(command):
    """Run a shell command and return the output, handle errors"""
    logging.debug(f"Executing command: {command}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    output, errors = process.communicate()
    if process.returncode != 0:
        logging.debug(f"Command error: {errors.strip()}")
    return output, errors, process.returncode

def list_subscriptions():
    """List all subscriptions using Azure CLI"""
    command = "az account list --query '[].id' --output json"
    output, errors, code = run_command(command)
    if code != 0:
        logging.error(f"Error listing subscriptions: {errors.strip()}")
        return []
    return json.loads(output)

def list_resource_groups(subscription_id):
    """List all resource groups in a given subscription"""
    command = f"az group list --subscription {subscription_id} --query '[].name' --output json"
    output, errors, code = run_command(command)
    if code != 0:
        logging.error(f"Error listing resource groups for subscription {subscription_id}: {errors.strip()}")
        return []
    return json.loads(output)

def handle_assets(subscription_id, resource_group, asset_type):
    """Attempt to list assets and handle rate limiting and permission errors"""
    command = f"az resource list --subscription {subscription_id} --resource-group {resource_group} --resource-type {asset_type} --query '[]' --output json"
    output, errors, code = run_command(command)
    if code != 0:
        if "RateLimitExceeded" in errors:
            logging.warning("Rate limit exceeded, waiting to retry...")
            time.sleep(60)  # Wait for 60 seconds
            return handle_assets(subscription_id, resource_group, asset_type)  # Retry the command
        if "AuthorizationFailed" in errors:
            logging.error(f"Permission error for {subscription_id}/{resource_group} - {asset_type}: {errors.strip()}")
            return None, "Permission Denied"
        logging.error(f"Command error for {subscription_id}/{resource_group} - {asset_type}: {errors.strip()}")
        return None, errors
    try:
        return json.loads(output), None
    except json.JSONDecodeError:
        return None, "JSON decoding error"

def process_asset(subscription_id, resource_group, asset_type):
    assets, error = handle_assets(subscription_id, resource_group, asset_type)
    if assets is not None:
        count = len(assets)
        return subscription_id, resource_group, asset_type, count, None
    else:
        return subscription_id, resource_group, asset_type, 0, error

def main(asset_file, debug):
    setup_logging(debug)
    subscriptions = list_subscriptions()
    if not subscriptions:
        logging.error("No subscriptions found or accessible.")
        return

    try:
        with open(asset_file, 'r') as file:
            asset_types = [line.strip() for line in file]
    except Exception as e:
        logging.error(f"Failed to read asset types file: {str(e)}")
        return

    total_assets = 0
    subscription_summary = {}

    # Calculate total tasks for the progress bar
    total_tasks = sum(len(list_resource_groups(sub)) * len(asset_types) for sub in subscriptions)
    pbar = tqdm(total=total_tasks, desc="Processing Assets", unit="asset")

    with open("asset_count.txt", "w") as outfile, concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_asset = {executor.submit(process_asset, sub, rg, at): (sub, rg, at)
                           for sub in subscriptions
                           for rg in list_resource_groups(sub)
                           for at in asset_types}

        for future in concurrent.futures.as_completed(future_to_asset):
            sub, rg, at = future_to_asset[future]
            try:
                subscription_id, resource_group, asset_type, count, error = future.result()
                if error is None:
                    if subscription_id not in subscription_summary:
                        subscription_summary[subscription_id] = 0
                    subscription_summary[subscription_id] += count
                    total_assets += count
                    outfile.write(f"{subscription_id}/{resource_group}: {asset_type} - Count: {count}\n")
                else:
                    outfile.write(f"{subscription_id}/{resource_group}: {asset_type} - {error}\n")
            except Exception as exc:
                logging.error(f"Error processing {sub}/{rg}/{at}: {str(exc)}")
            finally:
                pbar.update(1)

    with open("asset_count.txt", "a") as outfile:
        outfile.write(f"\nGrand Total of All Assets: {total_assets}\n")

    # Output summary to console after processing is complete
    print("\nSummary of asset counts per subscription:")
    for subscription, count in subscription_summary.items():
        print(f"{subscription}: {count}")
    print(f"Grand Total of All Assets: {total_assets}")

    print("Asset counting complete. Detailed results are in asset_count.txt")
    pbar.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Count assets across all subscriptions and resource groups in Azure, handling rate limits and permissions.')
    parser.add_argument('asset_file', type=str, help='File containing asset types to be checked')
    parser.add_argument('--debug', action='store_true', help='Enable debug output for more verbose information')
    args = parser.parse_args()

    main(args.asset_file, args.debug)