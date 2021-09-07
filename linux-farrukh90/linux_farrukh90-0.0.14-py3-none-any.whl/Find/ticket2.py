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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def filestructure():
    FILETOWORK="/mnt/secure"
    if os.path.isfile(FILETOWORK):
        print(bcolors.OKGREEN + "secure file is copied in /mnt" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "secure file isn't copied in /mnt properly, please try again" + bcolors.ENDC)
        sys.exit(1)
    time.sleep(0.5)
    if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " seems to be empty" + bcolors.ENDC  )
    elif os.path.isfile(FILETOWORK):
        print(bcolors.OKGREEN + FILETOWORK + " has been created"+ bcolors.ENDC)
    else:
        print(bcolors.FAIL +  "Something went wrong please try again" + bcolors.ENDC)
        sys.exit(1)
    time.sleep(0.5)
    FILETOWORK="/etc/yum.repos.d/Media.repo.gz"
    # Checks if /etc/yum.repos.d/Media.repo.gz is created.
    if os.path.isfile(FILETOWORK):
        print(bcolors.OKGREEN + FILETOWORK +  "is created properly" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL +  FILETOWORK + " is not created properly, please try again" + bcolors.ENDC)
        sys.exit(1)
    time.sleep(0.5)
