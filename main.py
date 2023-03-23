import argparse
import logging
import os
import sys

import pandas as pd
import requests
from dotenv import load_dotenv
from rich.console import Console


console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
URL = os.getenv("URL")
TOKEN = os.getenv("TOKEN")


def get_devices(token, url):
    """Get a list of devices from the LibreNMS API.

    Args:
        token (str): API token.
        url (str): API URL.

    Returns:
        pd.DataFrame: DataFrame containing device information.
    """
    try:
        headers = {"X-Auth-Token": token}
        devices_url = f"{url}/api/v0/devices/"
        response = requests.get(devices_url, headers=headers)
        response.raise_for_status()
        response = response.json()

        if response["status"] == "ok":
            console.log(f'Success - LibreNMS Devices count: {response["count"]}\n')
            devices = pd.json_normalize(response["devices"])
            devices = devices.sort_values("hostname").reset_index(drop=True)
            selected_cols = [
                "hostname",
                "device_id",
                "hardware",
                "os",
                "ip",
                "sysName",
                "serial",
                "location",
                "sysDescr",
            ]
            return devices[selected_cols]

        else:
            logger.error("Failed to get LibreNMS Devices list via API")
            raise requests.exceptions.RequestException(response["message"])

    except requests.exceptions.RequestException as e:
        logger.exception("An error occurred")
        raise


def export_devices(df, output_format, output_file):
    """Export a DataFrame to a file.

    Args:
        df (pd.DataFrame): DataFrame to export.
        output_format (str): Output format ('csv' or 'excel').
        output_file (str): Output file name.
    """
    if output_format == "csv":
        output_file = (
            output_file if output_file.endswith(".csv") else f"{output_file}.csv"
        )
        df.to_csv(output_file, index=False)
    elif output_format == "excel":
        output_file = (
            output_file if output_file.endswith(".xlsx") else f"{output_file}.xlsx"
        )
        with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)
    else:
        raise ValueError(f"Invalid output format: {output_format}")


def main():
    parser = argparse.ArgumentParser(
        description="Get a list of devices from the LibreNMS API."
    )
    parser.add_argument(
        "--format",
        choices=["csv", "excel"],
        default="excel",
        help="Output format (default: excel)",
    )
    parser.add_argument(
        "--outfile",
        default="device_list.xlsx",
        help="Output file name (default: device_list.xlsx)",
    )
    args = parser.parse_args()

    try:
        console.rule("Getting LibreNMS Devices from API")
        console.log(f"LibreNMS URL: {URL}\n")

        # Get devices
        df_devices = get_devices(TOKEN, URL)

        # Export the devices to a file
        export_devices(df_devices, args.format, args.outfile)

        # Print the DataFrame to the console
        print(df_devices.tail(6))
        sys.exit(0)

    except Exception as e:
        console.print(f"An error occurred: {e}", style="bold red")
        sys.exit(1)


main()
