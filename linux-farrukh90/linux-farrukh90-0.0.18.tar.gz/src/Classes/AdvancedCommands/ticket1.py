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

FILETOWORK="/tmp/userdata"
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def filestructure():
    try:
        FILETOWORK="/tmp/userdata"
        # Checks if "/tmp/userdata" is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
            
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )
        
        with open(FILETOWORK) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                if "312" and "847" and "773" and "ID" and "First" and  "Last" "E-mail" in x:
                    print(bcolors.OKGREEN +  FILETOWORK + " has the necessary content"+ bcolors.ENDC)
                else:
                    print(bcolors.FAIL +  FILETOWORK + " does not have the necessary content"+ bcolors.ENDC)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    try:
        FILETOWORK="/tmp/phone"
        # Checks if "/tmp/phone" is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )
        
        with open(FILETOWORK) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                if "312" and "847" and "773" in x:
                    print(bcolors.OKGREEN +  FILETOWORK + " has the necessary content"+ bcolors.ENDC)
                else:
                    print(bcolors.FAIL +  FILETOWORK + " does not have the necessary content"+ bcolors.ENDC)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    try:    
        FILETOWORK="/tmp/email"
        # Checks if "/tmp/email" is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )
        
        with open(FILETOWORK) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                if "abc@gmail.com" and "rob@gmail.com" and "ben@gmail.com" in x:
                    print(bcolors.OKGREEN +  FILETOWORK + " has the necessary content"+ bcolors.ENDC)
                else:
                    print(bcolors.FAIL +  FILETOWORK + " does not have the necessary content"+ bcolors.ENDC)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 