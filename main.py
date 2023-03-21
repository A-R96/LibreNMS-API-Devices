from dotenv import load_dotenv
import pandas as pd
import requests
import sys
import os
from rich.console import Console

console = Console()

# Load the URL and TOKEN from .env
load_dotenv()
URL = os.getenv('URL')
TOKEN = os.getenv('TOKEN')


def get_devices(token, url):

    # Send the request to the API
    try:
        headers = {'X-Auth-Token': token}
        devices_url = f'{url}/api/v0/devices/'
        response = requests.get(devices_url, headers=headers)
        response.raise_for_status()
        response = response.json()

        # If the API gives an ok code. Get all the devices and the values we want
        if response['status'] == 'ok':
            console.log(f'Success - LibreNMS Devices count: {response["count"]}\n')
            devices = pd.json_normalize(response['devices'])
            devices = devices.sort_values('hostname').reset_index(drop=True)
            selected_cols = ['hostname', 'device_id', 'hardware', 'os', 'ip', 'sysName',
                             'sysObjectID', 'serial', 'location', 'location_id', 'uptime',
                             'sysDescr', 'status', 'last_polled_timetaken']
            return devices[selected_cols]

        else:
            console.print('Failed to get LibreNMS Devices list via API', style='bold red')
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        console.print(f'An error occurred: {e}', style='bold red')
        sys.exit(1)


def main():
    # Main function that runs the full script
    try:
        console.rule('Getting LibreNMS Devices from API')
        console.log(f'LibreNMS URL: {URL}', '\n')

        # Get devices
        df_devices = get_devices(TOKEN, URL)
        
        # Export device list to excel sheet
        with pd.ExcelWriter('device_list.xlsx', engine='xlsxwriter') as writer:
            df_devices.to_excel(writer, sheet_name='Sheet1', index=False)
            
        # Alternatevly write to a csv
        #df_devices.to_csv('devices.csv')

        # Print the DataFrame to the console
        print(df_devices.tail(6))
        sys.exit(0)

    except Exception as e:
        console.print(f'An error occurred: {e}', style='bold red')
        sys.exit(1)



main()
