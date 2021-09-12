import socket
import os

def connection_test(host, port):
    host = host
    port = port
    s = socket.socket()
    get_client_addr = socket.gethostname()
    client_addr = socket.gethostbyname(get_client_addr)
    client_name = os.environ["COMPUTERNAME"]

    print(f"CONNECTING TO {host}:{port}")
    try:
        s.connect((host, port))  # Connects you to your server address (host) at the (port) you set
        print("[+] CONNECTED")
        s.send(f"Succesfull connection from: {client_addr}@{client_name}".encode())  # Sends a message to the server, confirming the connection
        s.close()  # Disconnects from the server
        print("[-] DISCONNECTED")
        print("[*]TEST SUCCESSFULL")
    except TimeoutError:
        print(f"Couldn't connect to {host} on port {port}")  # A connection couldn't be made to the server

def basic_server(port):
    s = socket.socket()
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = port
    BUFFER_SIZE = 4096

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)
    print(f"[SERVER] Listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, address = s.accept()
        print(f"[+] CONNECTION FROM: {address}")
        client_socket.close()
        s.close()
        