#!/usr/bin/env python3

import logging
import os
import sys
from fcntl import ioctl
from pyclui import Logger
import socket

logger = Logger(__name__, logging.DEBUG)

from scapy.layers.bluetooth import ATT_Read_By_Group_Type_Request, HCI_Hdr, HCI_ACL_Hdr, L2CAP_Hdr
from scapy.layers.bluetooth import ATT_Hdr, ATT_Read_By_Type_Request
from scapy.layers.bluetooth import BluetoothUserSocket, BluetoothSocketError

# hci_idx = 0


# class HCIConfig:
#     @staticmethod
#     def down(iface):
#         # 31 => PF_BLUETOOTH
#         # 0 => HCI_CHANNEL_USER
#         # 0x400448ca => HCIDEVDOWN
#         sock = socket.socket(31, socket.SOCK_RAW, 1)
#         ioctl(sock.fileno(), 0x400448ca, iface)
#         sock.close()
#         return True


# def get_socket(hci_idx):
#     try:
#         return BluetoothUserSocket(hci_idx)
#     except BluetoothSocketError as e:
#         logger.debug("[!] Creating socket failed: %s\n" % (repr(e)))
#         if os.getuid() > 0:
#             logger.error("[!] Are you definitely root? detected uid: %d\n" % (os.getuid()))
#             logger.debug("[+] attempting to take iface down anyways as non-root user\n")
#             HCIConfig.down(hci_idx)
#             try:
#                 return BluetoothUserSocket(hci_idx)
#             except BluetoothSocketError as e:
#                 logger.error("[!] Failed to create socket: %s" % repr(e))
#                 logger.error("[!] Giving up.\n")
#         else:
#             logger.debug("[+] have root, attempting to take iface down\n")
#             HCIConfig.down(0)
#             try:
#                 return BluetoothUserSocket(hci_idx)
#             except BluetoothSocketError as e:
#                 logger.error("[!] Failed to create socket: %s" % repr(e))
#                 logger.error("[!] Giving up.\n")
#     sys.exit(1)

ATT_CID = 4

# packet = HCI_Hdr()/HCI_ACL_Hdr(handle=64)/L2CAP_Hdr(cid=CID_ATT)/(ATT_Hdr()/ATT_Read_By_Type_Request(start=0x0000, end=0xffff,uuid=0x2803))
packet = ATT_Hdr()/ATT_Read_By_Type_Request(start=0x0000, end=0xffff,uuid=0x2803)
packet = ATT_Hdr()/ATT_Read_By_Group_Type_Request(start=0x0000, end=0xffff,uuid=0x2801)
print(packet)
# sock = get_socket(0)
# sock.send(packet)
