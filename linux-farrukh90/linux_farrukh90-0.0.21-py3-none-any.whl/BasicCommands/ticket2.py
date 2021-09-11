import os 
import sys
import time
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


sys.path.append('../')

from Classes.shared_scripts.modules import *

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def taskchecker():
    filechecker("/tmp/fruits")
    sizechecker("/tmp/services")
    linechecker("/tmp/top10")
    linechecker("/tmp/bottom10")
    sizechecker("/tmp/sorted_fruits")
    filechecker("/tmp/sorted_fruits")

    sizechecker("/tmp/counted_services")
    filechecker("/tmp/counted_services")
    linetotalchecker("/tmp/counted_services", 13000)
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 

taskchecker()