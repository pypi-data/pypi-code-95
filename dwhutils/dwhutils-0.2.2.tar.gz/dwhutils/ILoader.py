import os

import pandas as pd
import yaml

from termcolor2 import colored

from dwhutils.DataVaultLoader import DataVaultLoader
from dwhutils.TableReader import read_raw_sql_sat
from dwhutils.TechFields import add_technical_col
from dwhutils.db_connection import connect_to_db
from dwhutils.MongoLoader import MongoLoader
import os
from dotenv import load_dotenv


class ILoader:

    def __init__(self, date: str, load_domain:str, loader_type: str = None, target_connection: connect_to_db = None,
                 loading_entity: str = None,
                 loading_sat: str = None, schema: str = None, report_name: str = None, bi_departement=None,
                 build_hash_key: bool = False):
        load_dotenv()
        self.config_file = os.getenv('DB_CONFIG')
        self.kp_path = os.getenv('KEYPASS')
        self.conf_r = os.getenv('ENTITY_CONFIGS')
        self.loader_type = loader_type
        self.target_connection = target_connection
        self.loading_sat = loading_sat
        self.date = date
        self.load_domain = load_domain
        self.loading_entity = loading_entity
        self.schema = schema
        self.report_name = report_name
        self.bi_departement = bi_departement
        self.build_hash_key = build_hash_key
        #self.conf_r = config_file


    def load(self, data: pd.DataFrame):
        print(colored('Load {0}'.format(self.loading_entity),'red'))
        if self.loader_type.upper() == 'DATAVAULT':
            self._datavault(data=data)
        elif self.loader_type.upper() == 'MONGO':
            self._mongo(data=data)
        elif self.loader_type.upper() == 'ADHOC':
            pass
        elif self.loader_type.upper() == 'FLAT':
            self._flatload(data=data)
        elif self.loader_type.upper() == 'EXPORT':
            pass
        else:
            print(colored('no permissible loader specified!', "red"))

    def _flatload(self, data: pd.DataFrame):
        data = add_technical_col(data=data, t_name=self.loading_entity, date=self.date, entity_name=self.loading_entity,
                                 buildHashKey=self.build_hash_key)
        dvl = DataVaultLoader(data=data, t_name=self.loading_entity, date=self.date, db_con=self.target_connection,
                              entity_name=self.loading_entity, schema=self.schema, commit_size=1000,load_domain=self.load_domain)
        dvl.load

    def _datavault(self, data: pd.DataFrame):
        sat_data = add_technical_col(data=data, t_name=self.loading_sat, date=self.date,
                                     entity_name=self.loading_entity, buildHashKey=self.build_hash_key)
        sat_data.drop_duplicates(inplace=True)
        with open(os.path.join(self.conf_r , self.loading_entity + '.yaml')) as file:
            documents = yaml.full_load(file)
        tables = documents[self.loading_entity]['tables']
        for i in tables:

            if documents[self.loading_entity]['tables'][i]['table_type'] == 'hub' or \
                    documents[self.loading_entity]['tables'][i]['table_type'] == 'link':
                hub_target_fields = documents[self.loading_entity]['tables'][i]['fields']
                hub_target_fields.append(documents[self.loading_entity]['tables'][i]['hash_key'])
                hub_target_fields = list(set(hub_target_fields))
                hub_name = i

        hub_res_data = pd.DataFrame(columns=hub_target_fields)

        hub_res_data[hub_target_fields] = data[hub_target_fields]

        dv_sat = DataVaultLoader(data=sat_data, db_con=self.target_connection, entity_name=self.loading_entity,
                                 t_name=self.loading_sat, date=self.date, schema=self.schema,load_domain=self.load_domain)
        dv_hub = DataVaultLoader(data=hub_res_data, db_con=self.target_connection, entity_name=self.loading_entity,
                                 t_name=hub_name,load_domain=self.load_domain,
                                 date=self.date, schema=self.schema)

        dv_sat.load
        dv_hub.load

    def _mongo(self, data: pd.DataFrame):
        mloader = MongoLoader(report_name=self.report_name, bi_departement=self.bi_departement, date=self.date)
        mloader.writereport(data)
