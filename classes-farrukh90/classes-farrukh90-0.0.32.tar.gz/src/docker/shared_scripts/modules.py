import os
import time
import sys
import subprocess

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
def isserviceactive(SERVICENAME):
    STATUS = os.system("systemctl status %s 1> /dev/null" % SERVICENAME)
    print(STATUS)
    if STATUS == 0:
        print(bcolors.OKGREEN + SERVICENAME + " Seems to be running"  + bcolors.ENDC)
    elif STATUS == 768:
        print(bcolors.FAIL + SERVICENAME + " Service installed but not running"  + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + SERVICENAME + " Seems like service is not installed"  + bcolors.ENDC)
        sys.exit(1)

def isserviceenabled(SERVICENAME):
    output = subprocess.check_output("systemctl status %s" % SERVICENAME, shell=True)
    output = output.decode()
    if "enabled; vendor preset: enabled" in output and os.path.isfile("/usr/lib/systemd/system/%s.service" % SERVICENAME):
        print(bcolors.OKGREEN + SERVICENAME + " Service is enabled"  + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + SERVICENAME + " Service is not enabled"  + bcolors.ENDC)
        sys.exit(1)


