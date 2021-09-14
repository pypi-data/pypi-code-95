from os.path import isfile, isdir
from os import system
import logging
from webscp.logger.auto_logger import autolog
from ..configuration import *
LOG_FILE = False
if keep_logs == True:
    if log_path:
        with open (f"{log_path}/scraper.log", 'x'):
            pass
    
    elif isdir("src"):
        if isdir("logs"):
            LOG_FILE = True
            with open ('src/logs/scraper.log', 'x'):
                pass

    elif isdir("logs"):
        LOG_FILE = True
        with open ('logs/scraper.log', 'x'):
            pass
    
    else:
        LOG_FILE = False
        print("Log file is enabled but path doesn't exist")
        print(f"Cannot find path 'logs/' or 'src/logs/' or {log_path} ")

format_var = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
if LOG_FILE:
    logging.basicConfig(filename=f"{log_path}/scraper.log", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

console_log = logging.StreamHandler()
console_log.setLevel(logging.DEBUG)
console_log.setFormatter(format_var)
logging.getLogger("").addHandler(console_log)
