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
    FILETOWORK = "/tmp/fruits"
    try:
        sizechecker(FILETOWORK)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)


    FILETOWORK = "/tmp/services"
    try:
        sizechecker(FILETOWORK)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)


    FILETOWORK="/tmp/top10"
    try:
        linechecker(FILETOWORK)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)





    try:
        FILETOWORK="/tmp/bottom10"
        num_lines = sum(1 for line in open(FILETOWORK))
        # Checks if /tmp/bottom10 is created
        sizechecker(FILETOWORK)
        if os.path.isfile(FILETOWORK) and num_lines == 10:
            print(bcolors.OKGREEN + FILETOWORK + " has been created and has %d lines" % num_lines + bcolors.ENDC)
        else:
            print(bcolors.FAIL +  FILETOWORK + " has not been created or has %d lines" % num_lines + bcolors.ENDC)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)

    try:
        FILETOWORK="/tmp/sorted_fruits"
        # Checks if /tmp/sorted_fruits is created
        sizechecker(FILETOWORK)
        filechecker(FILETOWORK)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)

    try:
        FILETOWORK="/tmp/counted_services"
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