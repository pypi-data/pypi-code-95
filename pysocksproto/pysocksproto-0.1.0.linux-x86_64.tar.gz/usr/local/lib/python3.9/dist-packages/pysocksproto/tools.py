from .exceptions import UnexpectedValue
from .constants import *

import socket, struct, threading, time
class Tools:
    atype2AF = {
            ATYP_IPV4:socket.AF_INET,
            ATYP_IPV6:socket.AF_INET6, 
            ATYP_DOMAINNAME:socket.AF_INET
            }
    def recv2(conn:socket.socket, *args):
        """
        Some wrapper, to cath empty returns from recv
        """
        try:
            data = conn.recv(*args)
            
            if not data:
                raise ConnectionResetError("Cannot receive data, socket seems closed")
        except Exception as e:
                raise ConnectionResetError(str(e))
        return data

    def serverReadCmd(conn:socket.socket) -> tuple:
        """
        Read and parse cmd message from client
        return (version:int, cmd:int, atype:int, address:str, port:int)
        """
        ver, cmd, _, atype = __class__.recv2(conn, 4, socket.MSG_WAITALL)
        if atype == ATYP_DOMAINNAME:
            length_name, = __class__.recv2(conn, 1, socket.MSG_WAITALL)
            name = __class__.recv2(conn, length_name).decode("utf-8")
        elif atype == ATYP_IPV4:
            name = socket.inet_ntop(socket.AF_INET, __class__.recv2(conn, 4, socket.MSG_WAITALL))
        elif atype == ATYP_IPV6:
            name = socket.inet_ntop(socket.AF_INET6, __class__.recv2(conn, 16, socket.MSG_WAITALL))
        else:
            raise UnexpectedValue(f"Server sent unknown address type {atype}")    
        port = int.from_bytes(__class__.recv2(conn, 2, socket.MSG_WAITALL), byteorder='big')
        return (ver, cmd, atype, name, port)
    
    def serverSendCmdResp(conn:socket.socket, version:int,  rep:int, atype:int, bnd_addr:str, bnd_port:int):
        """Send server response to cmd message"""
        if atype == ATYP_DOMAINNAME:
            bnd_addr = bnd_addr.encode("utf-8")
            data = struct.pack(f"!BBxBB{len(bnd_addr)}sH", version, rep, atype, len(bnd_addr), bnd_addr, bnd_port)
        elif atype == ATYP_IPV4:
            data = struct.pack("!BBxB4sH", version, rep, atype, socket.inet_pton(socket.AF_INET, bnd_addr), bnd_port)
        elif atype == ATYP_IPV6:
            data = struct.pack("!BBxB16sH", version, rep, atype, socket.inet_pton(socket.AF_INET6, bnd_addr), bnd_port)
        conn.send(data)
    
    def serverReadHello(conn:socket.socket) -> tuple:
        """Read and parse "greetings" message from client             
        return (version:int, methods:list[int])"""
        b = __class__.recv2(conn, 2, socket.MSG_WAITALL)
        ver = b[0]
        nm = b[1]
        b = __class__.recv2(conn, nm, socket.MSG_WAITALL)
        methods = []  
        for mtd in b:
            methods.append(mtd)
        return (ver, methods)
    
    def serverSendHelloResp(conn:socket.socket, version:int, authtype:int):
        """Send server response to greeings message """
        conn.send(struct.pack("BB", version, authtype))

    def serverReadAuthCreds(conn:socket.socket) ->tuple:
        """
        Get client creds by rfc1929 (socks username/password auth)
        return (version:int, username:str, password:str)
        """
        version, ulen = struct.unpack("BB", __class__.recv2(conn, 2, socket.MSG_WAITALL))
        username = __class__.recv2(conn, ulen, socket.MSG_WAITALL)
        plen = ord(__class__.recv2(conn, 1))
        password = __class__.recv2(conn, plen, socket.MSG_WAITALL)
        return (version, username.decode("utf-8"), password.decode("utf-8"))

    def serverSendAuthResp(conn:socket.socket, version:int, status:int):
        """
        Send response auth \n
        status greater than 0 indicates auth failture

        """
        conn.send(struct.pack('BB', version, status))

    #-------------------------------------------------------------------------------   
    
    def clientSendHello(conn:socket.socket, version:int, authtypes:list[int]):
        """
        Sends a client Greetings message to server (version, authtypes)
        """
        conn.send(struct.pack(f"BB{'B'*len(authtypes)}", version, len(authtypes), *authtypes))
    
    def clientReadHelloResp(conn:socket.socket):
        """
        Reads server Greetings message (version, selected auth type)
        returns (version:int, selectedauth:int)
        """
        version, selected_auth = __class__.recv2(conn, 2)
        return (version, selected_auth)

    def clientSendCmd(conn:socket.socket, version:int, cmd:int, atype:int, adress:str, port:str):
        """
        Sends a command  to server
        """

        if atype == ATYP_DOMAINNAME:
            conn.send(struct.pack(f"!BBxBB{len(adress)}sH", version, cmd, atype, len(adress), adress.encode("utf-8"), port))
        elif atype == ATYP_IPV4:
            conn.send(struct.pack("!BBxB4sH", version, cmd, atype, socket.inet_pton(socket.AF_INET, adress), port) )
        elif atype == ATYP_IPV6:
            conn.send(struct.pack("!BBxB16sH", version, cmd, atype, socket.inet_pton(socket.AF_INET6, adress), port))
        else:
            raise UnexpectedValue(f"Cliend sent  unknown address type {atype}")
    def clientReadCmdResp(conn:socket.socket):
        """
        Reads server command response\n
        returns (version:int, rep:int, atype:int, address:str, port:int)
        """
        b = __class__.recv2(conn, 4)
        version, rep, atype = struct.unpack("BBxB", b)
        if atype == ATYP_DOMAINNAME:
            adrsize = __class__.recv2(conn, 1)[0]
            address, port = struct.unpack(f"!{adrsize}sH",  __class__.recv2(conn, adrsize+2))
        elif atype == ATYP_IPV4:
            address, port = struct.unpack("!4sH", __class__.recv2(conn, 10))
            address = socket.inet_ntop(socket.AF_INET, address) 
        elif atype == ATYP_IPV6:
            address, port = struct.unpack("!16sH", __class__.recv2(conn, 18)) 
            address = socket.inet_ntop(socket.AF_INET6, address) 
        else:
            raise UnexpectedValue(f"Sever sent  unknown address type {atype}")
        return (version, rep, atype, address, port)
      
    def clientSendAuth(conn:socket.socket, username:str, password:str):
        """
        Sends username/pasword auth packet
        """
        s = struct.pack(f"BB{len(username)}sB{len(password)}s", 1, len(username), username.encode("utf-8"), len(password), password.encode("utf-8"))
        conn.send(s)
    
    def clientReadAuthResp(conn:socket.socket):
        """
        Reads server response on username/password auth
        return (ver:int, status:int)
        """
        ver, status = __class__.recv2(conn, 2)
        return (ver, status)


    def proxy(target1:socket.socket, target2:socket.socket):
        """
            sends data from target1  to target2 and back\n
            when at least one socket closed, returns control\n
            sets timeout both sockets to 5
        """
        def resend(from_s:socket.socket, to_s:socket.socket):
            try:
                from_s.settimeout(5)
                while True:
                    try:
                        b = from_s.recv(1024)
                        if len(b) == 0:
                            return
                        to_s.send(b)
                    except socket.timeout as e:
                        pass
                    except Exception as e:
                    #    print(f"c > t {e}")
                        return
            except:
                pass
        


        t1 = threading.Thread(target=resend, args=(target1, target2), name=f"{target1.getpeername()} client > I am > target {target2.getpeername()} ")
        t2 = threading.Thread(target=resend, args=(target2, target1), name=f"{target1.getpeername()} client < I am < target {target2.getpeername()} ")
        t1.start()
        t2.start()
        while t1.is_alive() and t2.is_alive():
            time.sleep(5)
        return
