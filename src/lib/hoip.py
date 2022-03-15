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
