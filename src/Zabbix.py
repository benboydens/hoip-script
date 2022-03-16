import hoip
import json

# Read in JSON file
device_mapping = None
with open('./mapping/mapping_devices.json', 'r') as outfile:
    device_mapping = json.load(outfile)

# Create file for zabbix to send
outfile = open("./out/zabbix_out.txt", "w")


#####################################
##      Send & parse Commands      ##
#####################################

# Go over every device and check their current State
for entry in device_mapping['devices']:
    # go over every device in de JSON file
    device = hoip.Device(entry['ip_address'])

    # send command
    try:
        # Get Group ID
        group_res = device.send_command(hoip.GET_GROUP_ID)

        # Get Firmware Version
        version_res = None
        if entry['type'] == 'TX':
            version_res = device.send_command(hoip.GET_TX_FIRMWARE_VERSION)
        else:
            version_res = device.send_command(hoip.GET_RX_FIRMWARE_VERSION)

    except TimeoutError:
        outfile.write(f'"{entry["name"]}" hoip.active 0\n') # 0 => 'Not Available', 1 => 'Available'
        continue


    # parse group response
    result =  "Read succeeded" if not group_res[0] else "!!READ FAILED!!"
    group_id = (group_res[1] << 8) + group_res[2]

    # parse firmware version response
    version = version_res[:32].decode('utf-8').replace('\0', '')
    #print(f'{entry["name"]} - {result} from {dev.ip_addr} -' + (f' Group ID: {group_id}' if not group_res[0] else '') + f' - version: {version}')

    # write to output to file
    outfile.write(f'"{entry["name"]}" hoip.active 1\n') # 0 => 'Not Available', 1 => 'Available'
    outfile.write(f'"{entry["name"]}" hoip.channel {group_id}\n')
    outfile.write(f'"{entry["name"]}" hoip.version "{version}"\n')

outfile.close()


######################################
##      Send To Zabbix Server       ##
######################################

import os

# send values in out file to zabbix server
print("Sending configurations to Zabbix Server...")
os.system("zabbix_sender -z zabbix.dataline.eu -i ./out/zabbix_out.txt")