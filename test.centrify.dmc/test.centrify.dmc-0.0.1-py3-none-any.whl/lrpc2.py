import sys
import os
import random
import time
import logging

if sys.platform.startswith("win"):
    import win32file
    import win32pipe
    import pywintypes
elif sys.platform.startswith("linux"):
    import socket

logger = logging.getLogger(__name__)

LRPC2_BYTEORDER = "little"
LRPC2_MAGIC_NUMBER = int(0xABCD8012).to_bytes(4, byteorder=LRPC2_BYTEORDER)
LRPC2_HEADER_LENGTH = int(34).to_bytes(2, byteorder=LRPC2_BYTEORDER)
LRPC2_VERSION_4 = int(4).to_bytes(4, byteorder=LRPC2_BYTEORDER)

# handshake messages
ANSWER_ACK = 1
ANSWER_NACK = 0

MSG_ID_ADMIN_CLIENT_GETTOKEN = int(1500).to_bytes(2, byteorder=LRPC2_BYTEORDER)

# Message data types
MSG_END = bytes([0])
MSG_DATA_TYPE_BOOL = bytes([1])
MSG_DATA_TYPE_INT32 = bytes([2])
MSG_DATA_TYPE_STRING = bytes([4])
MSG_DATA_TYPE_STRING_SET = bytes([7])


class Ipc:
    def __init__(self):
        if sys.platform.startswith("win"):
            self.handle = win32file.CreateFile(
                r'\\.\pipe\cagent_admins',
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                win32file.FILE_ATTRIBUTE_NORMAL,
                None
            )
        elif sys.platform.startswith("linux"):
            #pylint: disable=no-member
            self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.s.connect("/var/centrify/cloud/daemon2")

    def __del__(self):
        if sys.platform.startswith("win"):
            win32file.CloseHandle(self.handle)
        elif sys.platform.startswith("linux"):
            self.s.close()

    def send(self, data):
        if sys.platform.startswith("win"):
            win32file.WriteFile(self.handle, data)
            self.handle
        elif sys.platform.startswith("linux"):
            self.s.send(data)

    def recv(self, len):
        if sys.platform.startswith("win"):
            _,data = win32file.ReadFile(self.handle, len)
            return data
        elif sys.platform.startswith("linux"):
            return self.s.recv(len)

class Lrpc2:

    def connect(self):
        self.s = Ipc()
        logger.info("Connected to Centrify Client")
        self.pid = os.getpid()

        # Do handshake
        self.s.send(LRPC2_VERSION_4)
        data = self.s.recv(4)
        answer = int.from_bytes(data, byteorder=LRPC2_BYTEORDER)
        data = self.s.recv(4)
        self.max_payload_length = int.from_bytes(data, byteorder=LRPC2_BYTEORDER)
        logger.info("LRPC handshake is completed")

        if answer != ANSWER_ACK:
            raise Exception("Server doesn't support LRPC2 version 4")

    def request(self, payload):
        data = bytearray()
        data += LRPC2_MAGIC_NUMBER   # magic number        
        data += LRPC2_HEADER_LENGTH  # header length
        data += LRPC2_VERSION_4      # LRPC2 version
        data += self.pid.to_bytes(8, byteorder=LRPC2_BYTEORDER)  # pid
        
        # sequence number
        seq = random.randint(0, 0xFFFFFFFF)
        data += seq.to_bytes(4, byteorder=LRPC2_BYTEORDER)

        # timestamp
        ts = time.time() # seconds passed since epoch
        data += int(ts).to_bytes(8, byteorder=LRPC2_BYTEORDER)

        # payload length
        length = len(payload)
        if length > self.max_payload_length:
            logger.error("LRPC payload length %d exceeds the max limit %d", length, self.max_payload_length)
            raise Exception("LRPC2 payload exceed max limit")
        data += length.to_bytes(4, byteorder=LRPC2_BYTEORDER)

        # payload
        data += payload

        # send request
        self.s.send(bytes(data))

        # read response
        logger.info("Parsing LRPC response...")
        while True:
            header = self.s.recv(34)

            bmagic_number = header[0:4]
            _bheader_length =  header[4:6]
            _bversion = header[6:10]
            _bpid = header[10:18]
            bseq = header[18:22]
            _bts = header[22:30]
            blength = header[30:34]

            payload_length = int.from_bytes(blength, byteorder=LRPC2_BYTEORDER)
            payload = self.s.recv(payload_length)

            response_seq = int.from_bytes(bseq, byteorder=LRPC2_BYTEORDER)

            if bmagic_number != LRPC2_MAGIC_NUMBER:
                raise Exception("Unrecognized LRPC2 server")

            if  response_seq != seq:
                # Skip unmatched seq number.  It could be the response from
                # prevoius requests
                continue

            _command = payload[0:2]
            payload = payload[2:]
            items = []
            while len(payload) > 0:
                item_type = payload[0:1]
                if item_type == MSG_DATA_TYPE_INT32:
                    item = int.from_bytes(payload[1:5], byteorder=LRPC2_BYTEORDER, signed=True)
                    items.append(item)
                    payload = payload[5:]
                elif item_type == MSG_DATA_TYPE_STRING:
                    strlen = int.from_bytes(payload[1:5], byteorder=LRPC2_BYTEORDER, signed=True)
                    if (strlen < 0):
                        items.append(None)
                        payload = payload[5:]
                    else:
                        item = payload[5:5+strlen].decode("utf8")
                        items.append(item)
                        payload = payload[5+strlen:]
                elif item_type == MSG_DATA_TYPE_STRING_SET:
                    count = int.from_bytes(payload[1:5], byteorder=LRPC2_BYTEORDER)
                    payload = payload[5:]
                    strset = []
                    for _ in range(count):
                        strlen = int.from_bytes(payload[1:5], byteorder=LRPC2_BYTEORDER, signed=True)
                        if (strlen < 0):
                            strset.append(None)
                            payload = payload[5:]
                        else:
                            item = payload[5:5+strlen].decode("utf8")
                            strset.append(item)
                            payload = payload[5+strlen:]
                    items.append(strset)
                elif item_type == MSG_END:
                    break
                else:
                    logger.error(payload)
                    logger.error("Item type: %s", item_type)
                    raise Exception("Unrecognized data type")

            logger.info("LRPC response parsing is completed")
            return items

def gettoken(scope):
    try:
        client = Lrpc2()
        client.connect()
    except:
        raise Exception("Failed to connect to Centrify Client.  Please check\n- Cenrify Client is installed on the machine\n- Machine is enrolled to Centrify PAS\n- DMC feature is turned on\n- Run this python script with administrative privilege")

    payload = bytearray()
    payload += MSG_ID_ADMIN_CLIENT_GETTOKEN
    payload += MSG_DATA_TYPE_STRING
    payload += len(scope).to_bytes(4, byteorder=LRPC2_BYTEORDER)
    payload += scope.encode("UTF8")
    payload += MSG_END
    reply = client.request(payload)
    if reply[0]>0:
        logger.error("OAuth token request rejected")
        logger.error(reply)
        raise Exception("OAuth token request rejected by Centrify Client", reply)

    logger.info("OAuth token with scope '%s' is acquired successfully", scope)
    return reply[2]

