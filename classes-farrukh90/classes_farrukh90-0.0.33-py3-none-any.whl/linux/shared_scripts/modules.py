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
    else: 
        print(bcolors.FAIL + "%s file is not created, please try again" % FILENAME + bcolors.ENDC)
    time.sleep(0.5)
   
   

def folderchecker(FOLDERNAME):
    if os.path.isdir(FOLDERNAME):
        print(bcolors.OKGREEN + "%s is created" % FOLDERNAME + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "%s is not created, please try again" %FOLDERNAME + bcolors.ENDC)
    time.sleep(0.5)


def sizechecker(FILENAME):
    try:
        if os.path.getsize(FILENAME) <= 0:
            print(bcolors.FAIL + "%s"  + " seems to be empty" % FILENAME + bcolors.ENDC  )
        else:
            print(bcolors.OKGREEN + "The %s is not empty" % FILENAME + bcolors.ENDC) 
        time.sleep(0.5)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILENAME + " is not created"+ bcolors.ENDC)


def linechecker(FILENAME):
    try:
        num_lines = sum(1 for line in open(FILENAME))
        sizechecker(FILENAME)
        if os.path.isfile(FILENAME) and num_lines == 10:
            print(bcolors.OKGREEN + FILENAME + " has been created and has %d lines" % num_lines + bcolors.ENDC)
        else:
            print(bcolors.FAIL +  FILENAME + " has not been created or has %d lines" % num_lines + bcolors.ENDC)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILENAME + " is not created"+ bcolors.ENDC)


def linetotalchecker(FILENAME,TOTALNUMBER):
    try:
        with open(FILENAME) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                if TOTALNUMBER in x:
                    print(bcolors.OKGREEN +"Counted line is correct" + bcolors.ENDC  )
                
    except FileNotFoundError:
        print(bcolors.FAIL +  FILENAME + " is not created"+ bcolors.ENDC)
        sys.exit(1)
    time.sleep(0.5)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

