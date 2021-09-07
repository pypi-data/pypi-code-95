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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def filestructure():
    try:
        FILETOWORK="/tmp/configurations"
        # Checks if "/tmp/configurations" is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )
        try:
            configurations_content = os.listdir(FILETOWORK)
            searchstring = "resolv.conf"
            for x in (x for x in configurations_content if x in searchstring):
                print(bcolors.OKGREEN + FILETOWORK + " " + "has a proper content" + bcolors.ENDC  )
        except FileNotFoundError:
            print("message")
            sys.exit(1)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
        sys.exit(1)
filestructure()