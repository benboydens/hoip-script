# Script om alle tv's terug te zetten op de default channel
import lib.hoip as hoip
import lib.command as command
import json


# Read in JSON file
device_mapping = None
with open('mapping_devices.json', 'r') as file:
    device_mapping = json.load(file)

for entry in device_mapping['devices']:
    # create class to connect to device
    device = hoip.Device(entry['ip_address'])

    # send command to change channel to default
    try:
        payload = entry['default_group'].to_bytes(2, 'big')
        response = device.send_command(command.SET_GROUP_ID, payload)
    except TimeoutError:
        print(f'Cannot reach device {entry["name"]}')
    
    # parse response
    if not response[0]:
        print(f'Successfully set ID of device {entry["name"]}')
    elif response[0] == 0xFF:
        print(f'HDMI Sink does not exist - {entry["name"]}')
    elif response[0] == 0xFE:
        print(f'TX without connection - {entry["name"]}')
    else:
        print(f'Unknown error - {entry["name"]}')