import time
from random import randint
import uuid


def add(m, n):
    return m + n

def sleep(n):
    time.sleep(n)
    return None

class demo:
    def __init__(self):
        print("init")
        self.a = 0

    def print_a(self):
        print(self.a)

    def get_id(self):
        time.sleep(10)
        return id(self)

    def test(self):
        self.a += 1
        return self.a
from setup_demo.Serializer import *
