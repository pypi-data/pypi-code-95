import socket

class udp_hex():
    
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
    
    # 持续监听来自127.0.01.1：60002的udp消息
    def listen(self):
        while True:
            data, address = self.sock.recvfrom(10240)
            print('收到来自 {}:{} 的消息'.format(address[0], address[1]))
            # print(type(data))
            # print(data)
            print(data.hex())
            # print(type(data.hex()))

    def listenonce(self):
            data, address = self.sock.recvfrom(10240)
            print('收到来自 {}:{} 的消息'.format(address[0], address[1]))
            # print(type(data))
            # print(data)
            print(data.hex())
            # print(type(data
            return data.hex()

    # 发送一条udp消息到127.0.01.1：60003
    def send(self):   
        x_str = '252d 3d 4d6d'
        x_bytes = bytes.fromhex(x_str)
        self.sock.sendto(x_bytes, (self.udp_server_ip, 60003))
        # sock.close()
        



    
