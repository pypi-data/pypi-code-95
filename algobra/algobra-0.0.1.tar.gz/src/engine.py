import platform
import socket


def get_engine_info():
    return platform.node() or socket.gethostbyname()
