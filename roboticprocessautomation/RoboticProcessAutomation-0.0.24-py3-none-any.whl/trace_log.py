from pyautogui import position, screenshot
from datetime import datetime
import traceback

def trace_log(status: str ,msg: str = None, path_log: str = "", path_img: str = ""):
    '''
    This function is to log robots trace info in the file.
    And takes screenshots while status E,B,F would occur.

    *Some statuses has been already suggested by me ;)

    Args:
        status: (str) - [S] start/stop \n
                        [T] trace \n
                        [E] error \n
                        [B] business error \n 
                        [W] warning \n
                        [F] fatal \n
        msg: (str) - custom error message, left blank will produce /traceback/ msg
    '''
    try: 
        if msg == None:
            msg = str(traceback.format_exc()).replace('\n','')
        now = datetime.today().strftime("%y%m%d %H;%M;%S")
        with open(f"{path_log}log.txt","a") as f:
            f.write(f'{now} [{status}] - {str(msg)}\n')
        if status == 'E' or status == 'B' or status =='F':
            with open("log.txt","a") as f:
                f.write(f'{now} [{status}] - SCREENSHOT {str(position())}\n')
            screenshot(f'{path_img}{now}.png') 
    except Exception as e:
        print(e)