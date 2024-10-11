import subprocess
import json
import argparse
import time
from tqdm import tqdm
import logging

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

def list_projects(org_id):
    """List all projects in the given organization using gcloud command"""
    command = f"gcloud projects list --filter='parent.id:{org_id} parent.type:organization' --format=json"
    output, errors, code = run_command(command)
    if code != 0:
        logging.error(f"Error listing projects: {errors.strip()}")
        return []
    return json.loads(output)

def handle_assets(project_id, asset_type):
    """Attempt to list assets and handle rate limiting and permission errors"""
    command = f"gcloud asset list --project={project_id} --asset-types={asset_type} --format=json"
    output, errors, code = run_command(command)
    if code != 0:
        if "Quota exceeded" in errors:
            logging.warning("Quota exceeded, waiting to retry...")
            time.sleep(60)  # Wait for 60 seconds
            return handle_assets(project_id, asset_type)  # Retry the command
        if "Permission denied" in errors:
            logging.error(f"Permission error for {project_id} - {asset_type}: {errors.strip()}")
            return None, "Permission Denied"
        logging.error(f"Command error for {project_id} - {asset_type}: {errors.strip()}")
        return None, errors
    try:
        return json.loads(output), None
    except json.JSONDecodeError:
        return None, "JSON decoding error"

def main(org_id, asset_file, debug):
    setup_logging(debug)
    projects = list_projects(org_id)
    if not projects:
        logging.error("No projects found or accessible.")
        return

    try:
        with open(asset_file, 'r') as file:
            asset_types = [line.strip() for line in file]
    except Exception as e:
        logging.error(f"Failed to read asset types file: {str(e)}")
        return

    total_assets = 0
    project_summary = {}

    with open("asset_count.txt", "w") as outfile, tqdm(total=len(projects) * len(asset_types), desc="Processing Assets", unit="asset") as pbar:
        for project in projects:
            project_id = project['projectId']
            project_assets = 0
            for asset_type in asset_types:
                assets, error = handle_assets(project_id, asset_type)
                if assets is not None:
                    count = len(assets)
                    project_assets += count
                    total_assets += count
                    outfile.write(f"{project_id}: {asset_type} - Count: {count}\n")
                else:
                    outfile.write(f"{project_id}: {asset_type} - {error}\n")
                pbar.update(1)
            project_summary[project_id] = project_assets
            outfile.write(f"Total for {project_id}: {project_assets}\n\n")

    with open("asset_count.txt", "a") as outfile:
        outfile.write(f"\nGrand Total of All Assets: {total_assets}\n")

    # Output summary to console after processing is complete
    print("\nSummary of asset counts per project:")
    for project_id, count in project_summary.items():
        print(f"{project_id}: {count}")
    print(f"Grand Total of All Assets: {total_assets}")

    print("Asset counting complete. Detailed results are in asset_count.txt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Count assets across all projects in an organization and handle API limits.')
    parser.add_argument('org_id', type=str, help='Organization ID to check assets within')
    parser.add_argument('asset_file', type=str, help='File containing asset types to be checked')
    parser.add_argument('--debug', action='store_true', help='Enable debug output for more verbose information')
    args = parser.parse_args()

    main(args.org_id, args.asset_file, args.debug)
