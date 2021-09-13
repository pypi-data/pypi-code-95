import os
import json


config_file_path = (os.environ.get('NPAWS_CONFIG_FILE_PATH') or 
                    os.path.join(os.path.expanduser("~"), 'npaws.cfg'))
CONFIG = json.load(open(config_file_path, 'r'))


AWS_ACC_KEY_ID = CONFIG.get("AWS_ACC_KEY_ID")
AWS_SEC_ACC_KEY = CONFIG.get("AWS_SEC_ACC_KEY")
AWS_REGION_NAME = CONFIG.get("AWS_REGION_NAME")
USER_POOL_ID = CONFIG.get("USER_POOL_ID")
CLIENT_ID = CONFIG.get("CLIENT_ID")
CLIENT_SECRET = CONFIG.get("CLIENT_SECRET")
DB_HOST = CONFIG.get("DB_HOST")
DB_USER = CONFIG.get("DB_USER")
DB_PASSWORD = CONFIG.get("DB_PASSWORD")