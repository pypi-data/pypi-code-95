from paho.mqtt import publish as publish
import socket


def publish_simgle(**kwargs):
    try:
        publish.single(**kwargs)
        return True
    except socket.error:
        return False
