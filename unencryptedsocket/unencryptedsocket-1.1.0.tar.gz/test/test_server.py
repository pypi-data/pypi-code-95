from unencryptedsocket import *


def test(data):
    return "Data:\t{}, len: {}".format(data, len(data))


functions = dict(test_command=test)
SS(functions=functions).start()
print("test socket server started.", flush=True)

