import socket

def get_IP(hostname: str) -> str:
    """
    This method returns the first IP address string
    that responds as the given domain name
    """
    data = socket.gethostbyname(hostname)
    ip = repr(data)
    return ip

def is_bcg_network() -> bool:
    try:
        get_IP("ntp.bcg.com")
        return True
    except:
        return False