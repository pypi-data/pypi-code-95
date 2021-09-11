import time
import pyfiglet
import socket
import threading
from tqdm import tqdm
from colorama import Fore, Style

def create_user():
    welcome = pyfiglet.figlet_format("Welcome !")
    print(welcome)

    _name = input("Name : ")
    user = input("Username : ")
    create_password = input("Password : ")
    repeat_password = input("Repeat Password : ")

    accept = input("Do you want to create account ? [y or n]")
    if accept == "y":
        if create_password == repeat_password:
            user_entry = pyfiglet.figlet_format("Global Server")
            print(user_entry)

            f = open(f"{_name} account", "a")
            f.write(f"Name : {_name}\n")
            f.write(f"Username : {user}\n")
            f.write(f"Password : {create_password}\n")
            f.close()

            print("---------------------------------------------------------------------------")
            print(f"Hello {_name} ! Welcome to Global Server ")
            print("Successfully created account in Global Server, now you can connect !")
            print("------------------------------------------------------------------")

            print("*******************************************************************************")
            print("NOTE : ")
            print(f"You can also find a txt with title {_name} account.txt , you can go \n through the txt file if you forget username or password in the future")
            print("*******************************************************************************")
        else:
            print(Fore.RED + f'\nSorry {_name} ! Account is not created , because of password which is not matching ')

def connect():
    entry_word = pyfiglet.figlet_format("Global Server")
    print(entry_word)

    print("Please enter your username and password , if you forgot your username or \npassword please check your txt file saving your account details\n")
    name = input("Name : ")
    username = input("Username : ")
    password = input("Password : ")

    print("\n-------------------------------------------------------------------------")
    print("NOTE : Connecting from the Global Server with your permission")
    print("-------------------------------------------------------------------------")
    time.sleep(5)
    for _ in tqdm(range(100),desc="\n Connecting to server.....",ascii=True):
        time.sleep(0.2)
    time.sleep(2)
    print(Fore.GREEN + "\n------------------------------------------------------------------------")
    print("Connected Successfully to GS server with your permission!")
    print("------------------------------------------------------------------------\n")
    print(Style.RESET_ALL)
    print(Fore.YELLOW + f"Hi {name} ! Please be careful with you username and password, This is just a remainder not a warning.\n")
    print(Style.RESET_ALL)

    # Connection Data
    host = '127.0.0.1'
    port = 55555

    # Starting Server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    # Lists For Clients and Their Nicknames
    clients = []
    nicknames = []

    # Sending Messages To All Connected Clients
    def broadcast(message):
        for client in clients:
            client.send(message)

    # Handling Messages From Clients
    def handle(client):
        while True:
            try:
                # Broadcasting Messages
                message = client.recv(1024)
                broadcast(message)
            except:
                # Removing And Closing Clients
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast('{} left!'.format(nickname).encode('ascii'))
                nicknames.remove(nickname)
                break

    # Receiving / Listening Function
    def receive():
        while True:
            # Accept Connection
            client, address = server.accept()
            print("Connected with {}".format(str(address)))

            # Request And Store Nickname
            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            nicknames.append(nickname)
            clients.append(client)

            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname))
            broadcast("{} joined!".format(nickname).encode('ascii'))
            client.send('Connected to server!'.encode('ascii'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

    receive()

def client():
    # Choosing Nickname
    nickname = input("Choose your nickname: ")

    # Connecting To Server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 55555))

    # Listening to Server and Sending Nickname
    def receive():
        while True:
            try:
                # Receive Message From Server
                # If 'NICK' Send Nickname
                message = client.recv(1024).decode('ascii')
                if message == 'NICK':
                    client.send(nickname.encode('ascii'))
                else:
                    print(message)
            except:
                # Close Connection When Error
                print("An error occured!")
                client.close()
                break

    # Sending Messages To Server
    def write():
        while True:
            message = '{}: {}'.format(nickname, input(''))
            client.send(message.encode('ascii'))

    # Starting Threads For Listening And Writing
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()

def disconnect():
    disconnect = pyfiglet.figlet_format("Global Server")
    print(disconnect)
    print(
        "Please enter your username and password , if you forgot your username or \npassword please check your txt file saving your account details\n")
    name = input("Name : ")
    username = input("Username : ")
    password = input("Password : ")

    print("\n-------------------------------------------------------------------------")
    print("NOTE : Disconnecting from the Global Server with your permission")
    print("-------------------------------------------------------------------------")
    time.sleep(3)
    for _ in tqdm(range(100), desc="\nDisconnecting from the server.....",ascii=True):
        time.sleep(0.3)
    print(Fore.YELLOW + "\n-----------------------------------------------------")
    print("Disconnected from the GS server with your permission!")
    print("-----------------------------------------------------")
    print(Style.RESET_ALL)

def info():
    info_logo = pyfiglet.figlet_format("Global  Server")
    print(info_logo)

    print("\n---------------------------------------------------------------------------------------------------------------------------------------")
    print(Fore.YELLOW + "Information regarding GS : ")
    print(Style.RESET_ALL)
    print("GS - Global Server is a server or a room can be used by any developer for building TCP chat apps or server hosted apps in just a line\nBut this can only be used in localhost only but not in the host\n"
          "This app or software was built by Sujith Sourya Yedida , presented by TS³")
    print("---------------------------------------------------------------------------------------------------------------------------------------")
    print("\n---------------------------------------------------------------------------------------------------------------------------------------")
    print(Fore.YELLOW + "Version details : ")
    print(Style.RESET_ALL)
    print("Name : " + Fore.RED + "pyGlobServe")
    print(Style.RESET_ALL)
    print("Version : " + Fore.RED + "1.0.0")
    print(Style.RESET_ALL)
    print("Date released : " + Fore.RED + "11-09-2021")
    print(Style.RESET_ALL)
    print("Developer : " + Fore.RED + "Sujith Sourya Yedida")
    print(Style.RESET_ALL)
    print("Producer : " + Fore.RED + "TS³")
    print(Style.RESET_ALL)
    print("---------------------------------------------------------------------------------------------------------------------------------------")
    print(
        "\n---------------------------------------------------------------------------------------------------------------------------------------")
    print(Fore.YELLOW + "Developer's note : ")
    print(Style.RESET_ALL)
    print("Hi Users ! This is Sujith Sourya Yedida - the developer of this package(Global Server). Hope so that all of you would like to enjoy \nthis package in python. All the best to future programmers! \nHappy Programming !!")
    print("---------------------------------------------------------------------------------------------------------------------------------------\n")
    print(Fore.YELLOW + "@SujithSouryaYedida")
    print(Style.RESET_ALL)
def manuel():
    manuel_logo = pyfiglet.figlet_format("Global  Server")
    print(manuel_logo)
    print(Fore.YELLOW + "\n------------------------------------------------------------------------------------------------------------")
    print("NOTE : THIS MANUEL IS DEVELOPED BY SUJITH SOURYA YEDIDA")
    print("------------------------------------------------------------------------------------------------------------")
    print(Style.RESET_ALL)
    print(
        Fore.YELLOW + "\n------------------------------------------------------------------------------------------------------------")
    print("************************** GLOBAL SERVER MANUEL **************************")
    print("------------------------------------------------------------------------------------------------------------")
    print(Style.RESET_ALL)

    print("------------------------------------------------------------------------------------------------------------------\n")
    print("First of all you need to install you package for that you will use the following command in the cmd - " + Fore.YELLOW + "pip install pyGlobServe\n")
    print(Style.RESET_ALL)
    print("Then you will be having many other functions right in your package so let me go on with each of them : ")
    print("pyGlobServe.info() - to know more about this software")
    print("pyGlobServe.manuel() - it is a guide book regarding the Global Server")
    print("pyGlobServe.connect() - it is used to connect the server\n")
    print("You need to enter your username and password, then your laptop or PC is connected with the Server")
    print("pyGlobServe.client() - to to make users")
    print("For making clients you need to make to cmd terminals , there you simply need to say" + Fore.RED + " pyGlobServe.client()")
    print(Style.RESET_ALL)
    print("Then you can start chat with several clients but in localhost only \n")
    print("pyGlobServe.disconnect() - it is used to disconnect with the server")
    print("pyGlobServe.logo() - to review the logo\n")
    print("pyGlobServe.create_user() - to create a user")
    print("Then you need to create a username and a password or simply create a account for yourself")
    print("\n------------------------------------------------------------------------------------------------------------------\n")
    print(Fore.YELLOW + "@SujithSouryaYedida\n")
    print(Style.RESET_ALL)
def logo():
    logo = pyfiglet.figlet_format("Global  Server")
    print(logo)

    print(Fore.YELLOW + "\n------------------------------------------------------------------------")
    print("This logo is designed by Sujith Sourya Yedida")
    print("Presented by TS³")
    print("------------------------------------------------------------------------")
    print(Style.RESET_ALL)