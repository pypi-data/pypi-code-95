import os
import warnings

import pandas as pd
import yaml
from pymongo import MongoClient
from termcolor2 import colored
import os
from dotenv import load_dotenv
warnings.filterwarnings("ignore")


class MongoLoader:

    def __init__(self, report_name: str, bi_departement: str, date: str):
        self.report_name = report_name
        self.bi_department = bi_departement
        self.date = date
        load_dotenv()
        self.db_conf = os.getenv('DB_CONFIG')
        kp_path = os.getenv('KEYPASS')
        conf_r = os.getenv('ENTITY_CONFIGS')


    def writereport(self, report_data: pd.DataFrame):
        with open(self.db_conf) as file:
            documents = yaml.full_load(file)
        mongodb_port = documents['database']['MongoDB']['port']
        mongodb_host = documents['database']['MongoDB']['host']
        _db = documents['database']['MongoDB']['db_name'] + '_' + self.bi_department
        report_data = report_data.astype(str)
        print(colored('Write Report: {0}.{1}'.format(self.bi_department, self.report_name), 'green'))
        client = MongoClient(mongodb_host, mongodb_port)
        db = client[_db]
        collection_currency = db[self.report_name + "_" + self.date]
        data = report_data.to_dict('records')
        collection_currency.insert(data)
        print(colored('Report {0}.{1} Loaded '.format(db, self.report_name), 'green'))
