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
    FILETOWORK="/tmp/service_users"
    try:
        # Checks if /tmp/service_users is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )

        with open(FILETOWORK) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                if "nologin"  in x:
                    print(bcolors.OKGREEN +  FILETOWORK + " has the necessary content"+ bcolors.ENDC)
                else:
                    print(bcolors.FAIL +  FILETOWORK + " does not have the necessary content"+ bcolors.ENDC)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    time.sleep(0.5)

    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #     
    FILETOWORK="/tmp/no_comment_config"
    try:
        # Checks if /tmp/no_comment_config is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )

        with open(FILETOWORK) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                if "#" not in x:
                    print(bcolors.OKGREEN +  FILETOWORK + " has the necessary content"+ bcolors.ENDC)
                else:
                    print(bcolors.FAIL +  FILETOWORK + " does not have the necessary content"+ bcolors.ENDC)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    time.sleep(0.5)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #     
    FILETOWORK="/tmp/tcp_services"
    try:
        # Checks if /tmp/tcp_services is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )

        num_lines = sum(1 for line in open(FILETOWORK))
        if num_lines == 25:
            print(bcolors.OKGREEN + FILETOWORK + " " + "has the necessary content" + bcolors.ENDC  )
        else:
            print(bcolors.FAIL +  FILETOWORK + " does not have the necessary content, it has %s lines" % num_lines + bcolors.ENDC)
        sys.exit(1)

    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
        sys.exit(1)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 