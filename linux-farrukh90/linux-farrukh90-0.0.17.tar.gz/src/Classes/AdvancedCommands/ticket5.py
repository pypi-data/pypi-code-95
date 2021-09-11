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



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def filestructure():
    try:
        FILETOWORK="/tmp/allusers.txt"
        # Checks if "/tmp/allusers.txt" is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
            time.sleep(0.5)
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )
            time.sleep(0.5)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)
    try:
        FILETOWORK="/tmp/countedusers.txt"
        # Checks if "/tmp/countedusers.txt" is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
            time.sleep(0.5)
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )
            time.sleep(0.5)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)
    try:
        FILETOWORK="/root/userlist.txt"
        # Checks if "/root/userlist.txt" is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
            time.sleep(0.5)
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )
            time.sleep(0.5)
        try: 
            with open(FILETOWORK) as file_content:
                contents = file_content.read()
                for x in contents.splitlines():
                    x = x.strip()
                if "sam" and "john" and "mary" and "alan" and "/home/sam" and "/home/john" and "/home/mary" and "/home/alan" in x:
                    print(bcolors.OKGREEN + FILETOWORK + " " + "has a proper content" + bcolors.ENDC  )
                else:
                    print(bcolors.FAIL + FILETOWORK + " " + " doesn't have a proper content" + bcolors.ENDC  )
        except UnboundLocalError:
                print(bcolors.FAIL + FILETOWORK + " " + "is not numerated" + bcolors.ENDC  )
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)
    sys.exit(1)
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
