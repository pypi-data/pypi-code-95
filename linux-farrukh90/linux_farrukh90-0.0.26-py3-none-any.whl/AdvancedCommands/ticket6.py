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
        FILETOWORK="/tmp/suspicious.log"
        # Checks if "/tmp/suspicious.log" is created
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
                if "POSSIBLE BREAK-IN ATTEMPT" in x:
                    print(bcolors.OKGREEN + FILETOWORK + " " + "has a proper content" + bcolors.ENDC  )
                else:
                    print(bcolors.FAIL + FILETOWORK + " " + " doesn't have a proper content" + bcolors.ENDC  )
        except FileNotFoundError:
            print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)
    sys.exit(1)
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
