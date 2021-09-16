import socket

def check_host_and_port(host, port):
    """
    Check if the port is alive for designated host.
    :param host: host name
    :param port: port to check
    :return: True or False indicate if port is alive
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # timeout as 5 seconds
        sock.settimeout(5)
        try:
            result = sock.connect_ex((host,port))
            if result == 0:
                return True
            else:
                return False
        except OSError as msg:
            # use print directly as for jupyter env the error message will displayed in cell output
            print(f"[Error] Failed to check host and port [{host}:{port}]. Error message: {msg}")
            return False