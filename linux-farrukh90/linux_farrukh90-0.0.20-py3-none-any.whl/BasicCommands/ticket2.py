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
def filestructure():
    filechecker("/tmp/fruits")
    sizechecker("/tmp/services")
    linechecker("/tmp/top10")
    linechecker("/tmp/bottom10")
    sizechecker("/tmp/sorted_fruits")
    filechecker("/tmp/sorted_fruits")


    FILETOWORK="/tmp/counted_services"
    try:
        COUNTED_SERVICES="13921"
        with open(FILETOWORK) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                if COUNTED_SERVICES in x:
                    print(bcolors.OKGREEN +"Counted line is correct" + bcolors.ENDC  )
                else:
                    print("Counted line might be incorrect")
        # Checks if /tmp/counted_services is created
        sizechecker(FILETOWORK)
        filechecker(FILETOWORK)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
        sys.exit(1)
    time.sleep(0.5)

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
 

filestructure()