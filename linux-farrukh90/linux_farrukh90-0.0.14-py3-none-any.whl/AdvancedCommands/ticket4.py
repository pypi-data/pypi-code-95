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
        FILETOWORK="/tmp/head.txt"
        # Checks if "/tmp//head.txt" is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
            time.sleep(0.5)
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )
            time.sleep(0.5)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)



 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    try:
        FILETOWORK="/tmp/tail.txt"
        # Checks if "/tmp/tail.txt" is created
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
                if x and x[0].isdigit():
                    print(bcolors.OKGREEN + FILETOWORK + " " + "is numerated" + bcolors.ENDC  )
                else:
                    print(bcolors.FAIL + FILETOWORK + " " + "is not numerated" + bcolors.ENDC  )
        except UnboundLocalError:
                print(bcolors.FAIL + FILETOWORK + " " + "is not numerated" + bcolors.ENDC  )
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)
    sys.exit(1)
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
