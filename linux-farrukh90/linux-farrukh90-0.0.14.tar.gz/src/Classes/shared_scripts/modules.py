import os
import time
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
def filechecker(FILENAME):
    if os.path.isfile(FILENAME):
        print(bcolors.OKGREEN + "%s file is created" % FILENAME + bcolors.ENDC)
        time.sleep(0.5)
    else: 
        print(bcolors.FAIL + "%s file is not created, please try again" % FILENAME + bcolors.ENDC)
        time.sleep(0.5)
        sys.exit(1)
        


def folderchecker(FOLDERNAME):
    if os.path.isdir(FOLDERNAME):
        print(bcolors.OKGREEN + "%s is created with a proper content" % FOLDERNAME + bcolors.ENDC)
        time.sleep(0.5)
    else: 
        print(bcolors.FAIL + "%s is not created with a proper content, please try again" %FOLDERNAME + bcolors.ENDC)
        time.sleep(0.5)
        sys.exit(1)



def sizechecker(FILENAME):
    if os.path.getsize(FILENAME) <= 0:
        print(bcolors.FAIL + FILENAME + " seems to be empty" + bcolors.ENDC  )
        time.sleep(0.5)
    else:
        print(bcolors.FAIL +  "Something went wrong please try again" + bcolors.ENDC)
        time.sleep(0.5)
        sys.exit(1)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


