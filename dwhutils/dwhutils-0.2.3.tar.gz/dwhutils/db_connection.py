# package import
import os

import yaml
from dotenv import load_dotenv
from pykeepass import PyKeePass
from sqlalchemy.engine import create_engine
from sshtunnel import SSHTunnelForwarder


def connect_to_db(layer: str = None):
    '''
    :param layer: database layer
    :param config_fp: filepath to db config
    :param keypass_fp: filepath to keypassfile
    :return: databse connection (mariadb)
    '''
    load_dotenv()
    config_file = os.getenv('DB_CONFIG')
    kp_path = os.getenv('KEYPASS')

    with open(config_file) as file:
        documents = yaml.full_load(file)

    ssh_host = documents['database']['CoreDWH']['sshhost']

    kp = PyKeePass(kp_path, password=documents['database']['CoreDWH']['main'])
    ssh_pwd = kp.find_entries(title=ssh_host, first=True).password
    ssh_user = kp.find_entries(title=ssh_host, first=True).username
    psw = kp.find_entries(title='CoreDWH', first=True).password
    user = kp.find_entries(title='CoreDWH', first=True).username

    # user = documents['database']['user']
    # psw = documents['database']['password']
    port = documents['database']['CoreDWH']['port']
    dbname = documents['database']['CoreDWH']['db_name']
    host = documents['database']['CoreDWH']['host']
    db_type = documents['database']['CoreDWH']['type']
    # ssh_user = documents['database']['CoreDWH']['sshuser']
    # ssh_pwd = documents['database']['CoreDWH']['sshpw']
    useSSH = documents['database']['CoreDWH']['useSSH']

    if useSSH:
        tunnel = SSHTunnelForwarder((ssh_host, 22), ssh_password=ssh_pwd, ssh_username=ssh_user,
                                    remote_bind_address=(host, port))
        tunnel.start()
        local_port = str(tunnel.local_bind_port)
        c_str = "mysql+pymysql://" + str(user) + ":" + str(psw) + "@" + str(host) + ":" + str(
            local_port) + "/" + str(layer) + "?charset=utf8mb4"
    else:
        c_str = "mysql+pymysql://" + str(user) + ":" + str(psw) + "@" + str(host) + ":" + str(port) + "/" + str(
            layer) + "?charset=utf8mb4"

    con = create_engine(c_str)
    return con
