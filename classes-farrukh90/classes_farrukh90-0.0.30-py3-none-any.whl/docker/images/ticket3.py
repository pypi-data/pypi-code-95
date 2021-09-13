import os 
import sys

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

import sys
sys.path.append('../')
from Classes.shared_scripts.modules import *
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def taskchecker():
    FILETOWORK="/tmp/configurations"
    folderchecker("/tmp/configurations")
    sizechecker("/tmp/configurations")
    try:
        configurations_content = os.listdir(FILETOWORK)
        searchstring = "resolv.conf"
        for x in (x for x in configurations_content if x in searchstring):
            print(bcolors.OKGREEN + FILETOWORK + " " + "has a proper content" + bcolors.ENDC  )
    except FileNotFoundError:
        print(bcolors.FAIL + FILETOWORK + " " + "does not have a proper content" + bcolors.ENDC  )
        sys.exit(1)
            
taskchecker()