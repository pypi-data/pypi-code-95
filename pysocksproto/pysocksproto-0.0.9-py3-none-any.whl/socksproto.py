
from .constants import *
import socket
import time
import struct
import threading
from .tools import Tools


class socksServer():
    """
    Simple multithreaded tcp server
    """


    def __init__(self, host:str, port:int, threadclass, connect_timeout:int = 5, bind_timeout:int = 5, print_log:bool =True, require_auth = False,  valid_creds:dict = {},  version = 5) -> None:
        
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.threadclass = threadclass
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn.bind((host, port))

        self.bind_addrs = {
            socket.AF_INET:None,
            socket.AF_INET6:None
        }
        
        self.connect_timeout = connect_timeout
        self.bind_timeout = bind_timeout
        self.print_log = print_log
        self.require_auth= require_auth
        self.valid_creds = valid_creds
        self.version = version

    def set_bind_addresses(self, ipv4addr:str, ipv6addr:str):
        self.bind_addrs = {
        socket.AF_INET:ipv4addr,
        socket.AF_INET6:ipv6addr
        }
    
    def serve(self):
        """
        Start a server
        """

        self.conn.listen(1)

        while True:
            sock, ret = self.conn.accept()
            self.threadclass(sock, self).start()

class socksThread(threading.Thread):
    """
    Thread for every proxy`s client connection\n
    Just override some methods to create your own logic
    """

    def __init__(self, conn:socket.socket, server:socksServer) -> None:
        self.retaddr = conn.getpeername()
        self.server = server
        super().__init__(name = f"socksThread {self.retaddr[0]}")
        self.conn = conn

    def run(self):
        try:
            self.work()
        except Exception as e:
        #    print(e)
             pass
        self.conn.close()
    
    def printlog(self, strs):
        if not self.server.print_log:
            return
        print(f"{time.ctime()} from {self.retaddr}: {strs}")

    def work(self):
        self.simple_proxy()

    def verify_creds(self, username:str, password:str) -> bool:
        """
        invokes in auth stage from simpleproxy() function\n
        override it for your own auth 
        """
        if username in self.server.valid_creds:
            return password == self.server.valid_creds[username]
        return False
       
    def connect_request_handler(self, version:int, cmd:int, atype:int, target_address:str, target_port:int):
        """
        default CMD_CONNECT handler, works like a usually proxy\n
        override it for your own functions
        """
        with socket.socket(Tools.atype2AF[atype], socket.SOCK_STREAM, socket.IPPROTO_TCP) as connect_socket:
            connect_socket.settimeout(self.server.connect_timeout)
            try:
                connect_socket.connect((target_address, target_port))
            except Exception as w:
                self.printlog(f"Connect: Connection to {target_address}:{target_port} rejected by {w}")
                Tools.serverSendCmdResp(self.conn,  self.server.version, REPCODE_HOST_NOT_AVALIBE, atype,'0.0.0.0',0)
                return
            
            s = connect_socket.getsockname()
            Tools.serverSendCmdResp(self.conn, self.server.version, REPCODE_SUCCESS, atype, s[0], s[1])
            self.printlog(f"Connect: Connected to {target_address}:{target_port}")
            self.proxy(connect_socket)
                                
    def bind_request_handler(self, version:int, cmd:int, atype:int, target_address:str, target_port:int):
        """
        default CMD_BIND handler: binds a random port, waits connection, proxies\n
        override it for your own functions
        """
        AF_s = Tools.atype2AF[atype]
        BND_addr = self.server.bind_addrs[AF_s]
        with socket.socket(AF_s, socket.SOCK_STREAM, socket.IPPROTO_TCP) as bind_socket:
            bind_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            bind_socket.settimeout(self.server.bind_timeout)

            try:
                bind_socket.bind((BND_addr, 0))
            
            except Exception as e:
                Tools.serverSendCmdResp(self.conn, self.server.version, REPCODE_SERVER_ERROR, atype, target_address, 0)
                self.printlog(f"Bind: couldnt bind {BND_addr}:0 atype {atype} - {e}")
                return

            bind_socket.listen(1)
            _, binded_port = bind_socket.getsockname()

            self.printlog(f"Bind:  binded {BND_addr}:{binded_port} atype {atype}")
            Tools.serverSendCmdResp(self.conn, self.server.version, REPCODE_SUCCESS, atype, BND_addr, binded_port)

            try:
                target_socket, raddr = bind_socket.accept()
            except Exception as e:
                self.printlog(f"Bind: Connection accept() exception: {e}")
                return

            with target_socket:
                self.printlog(f"Bind: Connected {BND_addr}:{binded_port} <- {raddr}")
                Tools.serverSendCmdResp(self.conn, self.server.version, REPCODE_SUCCESS, atype, raddr[0], raddr[1])

                self.proxy(target_socket)

    def udp_request_handler(self, version:int, cmd:int, atype:int, target_address:str, target_port:int):
        self.printlog(f"UDP_ASSOCIATE: not supported :( ")
        Tools.serverSendCmdResp(self.conn, self.server.version, REPCODE_CMD_NOT_SUPPORTED, atype, target_address, 0)

    def simple_proxy(self, ):
        """
            Simple socks proxy\n
            bind_ip4, bind_ip6 may be NONE, in this case "BIND" request will be rejected with REPCODE_ADDRESS_NOT_SUPPORTED\n
            Not supposts UDP_ASSOCIATE method\n
            verify_creds must return true/false
        """
        version, methods = Tools.serverReadHello(self.conn)
        
        if not version == self.server.version:
            return

        if self.server.require_auth:
            if not AUTHMETHOD_USERNAME_PASSWD in methods:
                Tools.serverSendHelloResp(self.conn, self.server.version, AUTHMETHOD_NOT_AVALIBE) 
                return

            Tools.serverSendHelloResp(self.conn, self.server.version,  AUTHMETHOD_USERNAME_PASSWD)
            _, username, password = Tools.serverReadAuthCreds(self.conn)

            if not self.verify_creds(username, password):
                Tools.serverSendAuthResp(self.conn, 1, 0xff)
                return
            
            Tools.serverSendAuthResp(self.conn, 1, 0)

        else:
            Tools.serverSendHelloResp(self.conn, self.server.version, AUTHMETHOD_NOAUTH)
        
        version, cmd, atype, target_address, target_port = Tools.serverReadCmd(self.conn)
        
        if cmd == CMD_CONNECT:
            self.connect_request_handler(version, cmd, atype, target_address, target_port)
        
        if cmd == CMD_BIND:
            self.bind_request_handler(version, cmd, atype, target_address, target_port)
            
        if cmd == CMD_UDP_ASSOCIATE:
            self.udp_request_handler(version, cmd, atype, target_address, target_port)

    def proxy(self, target:socket.socket):
        """
        provide exchanging data between sockets
        """
        Tools.proxy(self.conn, target)

class socksBind():

    class bind_Unsucessful_repcode(Exception):
        def __init__(self, repcode:int, *args: object) -> None:
            super().__init__(*args)
            self.repcode = repcode
        def __str__(self) -> str:
            return f"Unsucessful repcode {self.repcode}"

    class auth_exception(Exception):
        def __str__(self) -> str:
            return "Invalid Authenfication"
    
   
    def __init__(self,  socksIp:str, socksPort:int,  creds:str = "" , logging = False, version = 5) -> None:
        self.conn:socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        self.socksIp = socksIp
        self.socksPort = socksPort
        self.version = version
        self.authmethods = [AUTHMETHOD_NOAUTH]
        if len(creds) > 0:
            self.authmethods.append(AUTHMETHOD_USERNAME_PASSWD)
        self.logging = logging
        self.bound = False
        self.connected = False
        self.creds = creds
        
    
    def  _printlog(self, stss):
        if self.logging:
            print(f' > {stss}')
    
    def __del__(self):
        self.conn.close()
    
    def username_password_auth(self):
        crd = self.creds.split(":")
        
        Tools.clientSendAuth(self.conn, crd[0], crd[1])
        _, status = Tools.clientReadAuthResp(self.conn)
        return status == 0
 
    def BindProxyPort(self):
        """
        Binds a port on proxy server and return bounded port, address, atype\n
        raises bind_Unsucessful_repcode exception if server returns an error\n
        return (atype:int, address:str, port:int)
        """
        if self.bound:
            raise Exception("This cliet already bounded to a port")
        self._printlog("Connecting to proxy....")
        
        self.conn.connect((self.socksIp, self.socksPort))

        self._printlog(f"Connected to {self.socksIp}:{self.socksPort}")
        self._printlog(f"Send greetings message with authmethods {self.authmethods}")

        Tools.clientSendHello(self.conn, self.version, self.authmethods)
        version, selected = Tools.clientReadHelloResp(self.conn)

        self._printlog(f"Server version: {version} selected {selected}")
        
        if selected == AUTHMETHOD_USERNAME_PASSWD:
            if not self.username_password_auth():
                raise __class__.auth_exception()
        
        self._printlog("Sending BIND command")
        Tools.clientSendCmd (self.conn, self.version, CMD_BIND, ATYP_IPV4, self.socksIp, 0)
        version, rep, atype, address, port = Tools.clientReadCmdResp(self.conn)
        if not rep == REPCODE_SUCCESS:
            raise __class__.bind_Unsucessful_repcode(rep)
        self.bound = True
        return (atype, address, port)
            
    def WaitProxyBindConnect(self):
        """
        Waits connect to bounded on proxy port\n

        returns Atype:int, address:str, port:int
        """
        if not self.bound or self.connected:
            raise Exception("This client not bounded, or already connected")
        version, rep, atype, address, port =  Tools.clientReadCmdResp(self.conn)
        if not rep == REPCODE_SUCCESS:
            raise __class__.bind_Unsucessful_repcode(rep)
        self.connected = True
        return (atype, address, port)

    def CreateProxyRedirection(self, target_ip:str, target_port:int):
        """
            
        """
        if not self.bound:
            raise Exception("Bound client first")
        if not self.connected:
            self.WaitProxyBindConnect()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as newc:
            newc.connect((target_ip, target_port))
            Tools.proxy(newc, self.conn)
            


        