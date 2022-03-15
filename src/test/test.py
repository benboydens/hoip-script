from hoip import Device
import command, os

# clear terminal
os.system('cls' if os.name == 'nt' else 'clear')

# send command to device
print('IP-address: 192.168.11.X')
device = Device('192.168.11.' + input('X = '))
command_payload = device.send_command(command.SET_GROUP_ID, [0x00, 0xE])


print('\nParsing Command\n==========================================')

# for GET_GROUP_ID COMMAND => 0x13, [0x00]
# result =  "READ SUCCEEDED" if not command_payload[0] else "READ FAILED"
# group_id = (command_payload[1] << 8) + command_payload[2]
# print(result)
# print(f'Group ID: {group_id}')

# for GET_LAN_STATUS COMMAND => 0xD, [0x00]
# result =  "READ SUCCEEDED" if not command_payload[0] else "READ FAILED"
# lan_status = "LINK UP" if command_payload[1] else "LINK DOWN"

# print(result)
# print(f'Link Status: {lan_status}')

# for GET_DEVICE_NAME => 0x1F, [0x00]
# name = (command_payload.decode('utf-8'))
# print(f'Device Name: {name}')

# for SET_GROUP_ID => 0x5, [0x00, 0xA] (set group id to 10)
result =  "SUCCESS" if not command_payload[0] else "FAILED"
print(result)