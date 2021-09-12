from socket import gethostbyaddr as _gethostbyaddr


def reverse_dns(ip):
    try:
        return _gethostbyaddr(ip)[0]
    except:
        return
