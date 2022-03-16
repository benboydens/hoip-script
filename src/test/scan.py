import socket

##########################################################
##      Create Broadcast packets to find devices        ##
##########################################################

# create UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# enable broadcast
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# get ip adress
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
port = 9002

# create payload
bytes = bytearray()
bytes.extend(b'IPTV_CMD')
bytes.extend(socket.inet_aton(ip_address))
bytes.extend(port.to_bytes(2, 'big'))
bytes.extend(b'\x00\x74')
bytes.extend(b'\x00\xFE')
bytes.extend(int(10).to_bytes(2, 'big'))

# header checksum
checksum = bytes[-1] + bytes[-2] + bytes[-3] + bytes[-4]
bytes.append(checksum.to_bytes(2, 'big')[1])

# command payload
bytes.extend(9 * [0x0])

# command payload checksum
checksum = 0
for i in range(0, 9):
    checksum += bytes[(-1)-i]
bytes.extend(checksum.to_bytes(1, 'big'))

# destination port and ip
serverAddressPort   = ("255.255.255.255", port)

# send UDP query scan
s.sendto(bytes, serverAddressPort)
s.close()


###########################################
##       Listen to incoming packets      ##
###########################################

# create UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))
s.settimeout(1)

responses = {
    "devices": []
}

while True:
    # listen for response
    try:
        response, addr = s.recvfrom(1024)
    except:
        break

    # Payload size
    payload_size = (response[17] << 8) + response[18]

    # Header Checksum = Command ID + Payload size
    sum = (response[15] << 8) + response[16] + payload_size
    assert (sum & 0xFF) == response[19], 'Invalid Header Checksum'

    # Command Payload
    payload = response[20:(20 + payload_size - 1)]

    # Command Checksum = sum of all payload bytes
    sum = 0
    for byte in payload:
        sum += byte
    assert (sum & 0xFF) == response[20 + payload_size - 1], 'Invalid Command Payload Checksum'

    # get all the field as usefull information
    device_name = payload[:32].decode('utf-8')
    device_ip = '.'.join([str(x) for x in payload[32:36]])
    device_recv_port = int.from_bytes(payload[36:38], 'big')
    device_group_id = int.from_bytes(payload[38:40], 'big')
    device_type = 'Tx Device' if payload[40] else 'Rx Device'
    device_state = 'Up and Running' if payload[41] else 'Idle'
    device_stream_type = 'AV over RTP' if payload[42] else 'AV over UDP'
    device_streaming_mode = 'Multicast' if payload[43] else 'Not Multicast'

    # # display all the fields as usefull information
    # print('Parsing Device Response\n' + 50 * '=')
    # print(f'Device Name: {device_name}')
    # print(f'Device IP: {device_ip}')
    # print(f'Device Recv Port: {device_recv_port}')
    # print(f'Device Group ID: {device_group_id}')
    # print(f'Device Type: {device_type}')
    # print(f'Device state: {device_state}')
    # print(f'Device Streaming Type: {device_stream_type}')
    # print(f'Device Streaming Mode: {device_streaming_mode}')    
    # input("\nPress Enter to continue...")

    # save device responses to a dictionary
    responses['devices'].append({
        'name': device_name.replace("\u0000", ""),
        'ip_address': device_ip,
        'receive_port': device_recv_port,
        'group_id': device_group_id,
        'device_type': device_type,
        'status': device_state,
        'streaming_type': device_stream_type,
        'streaming_mode': device_streaming_mode
    })

s.close()


import json
with open('mapping_devices.json', 'r') as outfile:
    device_mapping = json.load(outfile)
    # print(device_mapping)
    print(device_mapping['devices'][1])

'''
if responses['devices']:
    # if input("Save responses to file? (y/n) ").lower() == 'y':
    # convert dictionary to a JSON file named response.json
    import json
    with open('response.json', 'w') as outfile:
        json.dump(responses, outfile, indent=4)
        print("Success.")
else:
    print("No devices were found.")
'''