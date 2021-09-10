from easyfed.cortex.main import server,client
import os
import argparse
bdir=os.path.dirname(os.path.abspath(__file__))
def fedserver(port=16668):
    parser = argparse.ArgumentParser()
    parser.add_argument('-port',  default=None, help='')
    margs = parser.parse_args() 
    if margs.port:
        port=margs.port
    server(bdir,port).run()
