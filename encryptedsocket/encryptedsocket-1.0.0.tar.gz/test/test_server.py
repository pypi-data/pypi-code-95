from encryptedsocket import *
from easyrsa import *


kp = EasyRSA(bits=1024).gen_key_pair()
def test(data):
    return "Data:\t{}, len: {}".format(data, len(data))
functions = dict(test_command=test)
SS(functions=functions, key_pair=kp).start()
print("test socket server started.", flush=True)

