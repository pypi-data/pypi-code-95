from sys import argv
import importlib.util

global PROD
PROD = ""

class App():
    def __init__(self):
        print("Hello From CyroCoders")

def Run():
    if len(argv) == 1:
        loc = input(">")
    else: 
        loc = argv[1]
    while True:
        spec = importlib.util.spec_from_file_location("module.name", argv[1] if loc == None else loc)
        webapp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(webapp)

if __name__ == "__main__":
    Run()