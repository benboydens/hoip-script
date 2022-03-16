import socket

class Device:
    def __init__(self, ip_addr, receive_port=9002):
        self.ip_addr = ip_addr
        self.recv_port = receive_port
        self.send_port = 9001 # should always be this or you get no response

    # Most GET commands use a null payload
    def send_command(self, command, payload=[0x00]):
        self.__send_data_to_device(command, payload)
        response = self.__listen_response()
        return self.__parse_response(response)

    def __send_data_to_device(self, command_id, payload):
        s = socket.socket()
        s.settimeout(10)
        s.connect((self.ip_addr, self.send_port))

        # create binary data
        bytes = bytearray()

        # 8 byte sync word
        bytes.extend(b'IPTV_CMD')

        # host ip address
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        bytes.extend(socket.inet_aton(ip_address))

        # receive port
        bytes.extend(self.recv_port.to_bytes(2, 'big'))

        # sync word
        bytes.extend(0x74.to_bytes(1, 'big'))

        # command id
        bytes.extend(command_id.to_bytes(2, 'big'))

        # payload size = command payload + command payload checksum (1 byte)
        total_size = len(payload) + 1
        bytes.extend(total_size.to_bytes(2, 'big'))

        # header check sum
        checksum = bytes[-1] + bytes[-2] + bytes[-3] + bytes[-4]
        bytes.extend(checksum.to_bytes(1, 'big'))

        # command payload
        bytes.extend(payload)

        # command payload checksum
        checksum = 0
        for i in range(0, len(payload)):
            checksum += bytes[(-1)-i]
        bytes.extend(checksum.to_bytes(1, 'big'))

        # send data
        s.send(bytes)

        # close the connection
        s.close()

    def __listen_response(self):
        s = socket.socket()
        s.bind(('', self.recv_port))        
        #print (f'socket binded to {self.recv_port}')
        
        # put the socket into listening mode
        s.listen(5)
        s.settimeout(5)

        device_response = None

        while True:
            c, addr = s.accept()
            #print('Got connection from', addr )

            device_response = c.recv(1024)
            # Close the connection with the client
            c.close()
            
            # Breaking once connection closed
            break
        return device_response

    def __parse_response(self, response):
        # device ip
        device_ip = '.'.join([ str(x) for x in response[8:12] ])

        # Payload size
        payload_size = (response[17] << 8) + response[18]

        # Header Checksum = Command ID + Payload size
        sum = (response[15] << 8) + response[16] + payload_size
        #assert (sum & 0xFF) == response[19], 'Invalid Header Checksum'

        # Command Payload
        command_payload = response[20:(20 + payload_size - 1)]

        # print('\nParsing Device Response\n==========================================')
        # print(f'Device IP {device_ip}')
        # print(f'Command ID {hex((response[15]<< 8) + response[16])}')
        # print(f'Payload size: {payload_size}')
        # print(f'Command Payload: {command_payload}')

        # Command Payload Checksum = sum of all payload bytes
        sum = 0
        for byte in command_payload:
            sum += byte
        assert (sum & 0xFF) == response[20 + payload_size - 1], 'Invalid Command Payload Checksum'

        return command_payload





# List of all the possible commands to send to a device. 
# The responses are the codes send back from the devices.


# RX and TX commands
SET_DHCP_MODE=0x0001
SET_IP_ADDRESS=0x0003
SET_GROUP_ID=0x0005
SET_UART_BAUD_RATE=0x0007
SET_MAC_ADDRESS=0x0009
SET_SESSION_KEY=0x000B
GET_LAN_STATUS=0x000D
GET_SOURCE_HDCP_STATUS=0x000F
GET_VIDEO_LOCK_STATUS=0x0011
GET_GROUP_ID=0x0013
GET_DHCP_MODE=0x0015
GET_UART_BAUD_RATE=0x0017
GET_IP_ADDRESS=0x0019
GET_MAC_ADDRESS=0x001B
SET_DEVICE_NAME=0x001D
GET_DEVICE_NAME=0x001F
GET_DEVICE_IP=0x0021
FACTORY_RESET=0x0023
UPGRADE_FIRMWARE=0x0025
GET_UPGRADE_STATE=0x0027
GET_IP_CONFIG=0x0029
SET_COMPANY_ID=0x002B
GET_COMPANY_ID=0x002D
SET_STREAMING_MODE=0x002F
GET_STREAMING_MODE=0x0031
REBOOT=0x00F0
# responses
SET_DHCP_MODE_RET=0x0002
SET_IP_ADDRESS_RET=0x0004
SET_GROUP_ID_RET=0x0006
SET_UART_BAUD_RATE_RET=0x0008
SET_MAC_ADDRESS_RET=0x000A
SET_SESSION_KEY_RET=0x000C
GET_LAN_STATUS_RET=0x000E
GET_SOURCE_HDCP_STATUS_RET=0x0010
GET_VIDEO_LOCK_STATUS_RET=0x0012
GET_GROUP_ID_RET=0x0014
GET_DHCP_MODE_RET=0x0016
GET_UART_BAUD_RATE_RET=0x0018
GET_IP_ADDRESS_RET=0x001A
GET_MAC_ADDRESS_RET=0x001C
SET_DEVICE_NAME_RET=0x001E
GET_DEVICE_NAME_RET=0x0020
GET_DEVICE_IP_RET=0x0022
FACTORY_RESET_RET=0x0024
UPGRADE_FIRMWARE_RET=0x0026
GET_UPGRADE_STATE_RET=0x0028
GET_IP_CONFIG_RET=0x002A
SET_COMPANY_ID_RET=0x002C
GET_COMPANY_ID_RET=0x002E
SET_STREAMING_MODE_RET=0x0030
GET_STREAMING_MODE_RET=0x0032
REBOOT_RET=0x00F1


# RX only commands
SET_SCREEN_MODE=0x0101
GET_SCREEN_MODE=0x0105
GET_TX_DEVICE_IP=0x0107
SET_INFO_DISPLAY_MODE=0x0109
GET_INFO_DISPLAY_MODE=0x010B
GET_RX_FIRMWARE_VERSION=0x010D
# responses
SET_SCREEN_MODE_RET=0x0102
GET_SCREEN_MODE_RET=0x0106
GET_TX_DEVICE_IP_RET=0x0108
SET_INFO_DISPLAY_MODE_RET=0x010A
GET_INFO_DISPLAY_MODE_RET=0x010C
GET_RX_FIRMWARE_VERSION_RET=0x010E


# TX only commands
SET_GROUP_VIDEO_BIT_RATE=0x0101
SET_VIDEO_OUT_MODE=0x0105
SET_VIDEO_DOWN_SCALE_MODE=0x0107
GET_GROUP_VIDEO_BIT_RATE=0x0109
GET_VIDEO_OUT_MODE=0x010B
GET_DOWN_SCALE_MODE=0x010D
GET_TX_FIRMWARE_VERSION=0x010F
# responses
SET_GROUP_VIDEO_BIT_RATE_RET=0x0102
SET_VIDEO_OUT_MODE_RET=0x0106
SET_VIDEO_DOWN_SCALE_MODE_RET=0x0108
GET_GROUP_VIDOE_BIT_RATE_RET=0x010A
GET_VIDEO_OUT_MODE_RET=0x010C
GET_DOWN_SCALE_MODE_RET=0x010E
GET_TX_FIRMWARE_VERSION_RET=0x0110


# Error Responses
TIMEOUT_COMMAND_ID=0xFFFD
UNSUPPORT_COMMAND_ID=0xFFFE
CORRUPTED_COMMAND_ID=0xFFFF


# UDP query commands
DEV_INFO_QUERY=0x00FE
DEV_INFO_QUERY_RET=0x00FF