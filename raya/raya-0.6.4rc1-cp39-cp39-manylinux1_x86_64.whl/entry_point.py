import json
import os

from src.app import RayaApplication
from raya.exceptions import RayaApplicationException
from raya.logger import LogLevel, create_logger

def entry_point(app_path: str) -> None:
    exec_info_path = os.path.join(app_path, 'exec_info.json')
    log = create_logger("RayaApp.EntryPoint")
    os.chdir(app_path)
    try:
        with open(exec_info_path) as f:
            exec_info = json.load(f)
    except FileNotFoundError:
        log(LogLevel.FATAL, '"exec_info.json" file not found')
        exit(1)
    try:
        application = RayaApplication(  app_id = exec_info['app-id'], 
                                        dev_mode = exec_info['dev-mode'], 
                                        domain_id = exec_info['robot-connection']['dds-channel'],
                                        log_to_file = exec_info['logging']['file_enabled'],
                                        log_folder = exec_info['logging']['folder']
                                    )
        application._run()
    except RayaApplicationException as e:
        log(LogLevel.FATAL, f'Could not create Raya application: {e}')
        exit(1)
