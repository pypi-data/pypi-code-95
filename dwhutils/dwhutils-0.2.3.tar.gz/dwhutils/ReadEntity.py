import os

import yaml
from termcolor2 import colored
from dwhutils.TableReader import read_raw_sql_hub as r_hub
from dwhutils.TableReader import read_raw_sql_sat as r_sat
from dwhutils.db_connection import connect_to_db
import os
from dotenv import load_dotenv

class ReadEntity:

    def __init__(self, entity_name: str, p_date: str, exclude_sat_list: list = [], layer: str = None):
        load_dotenv()
        self.db_conf = os.getenv('DB_CONFIG')
        self.kp_path = os.getenv('KEYPASS')
        self.conf_r = os.getenv('ENTITY_CONFIGS')
        self.entity_name = entity_name.lower()
        self.p_date = p_date
        self.exclude_sat_list = exclude_sat_list
        self.layer = layer
        self.RC = 0
        self.read_config()
        self.test_table_existance()

    def read_config(self):
        conf_r = self.conf_r

        with open(os.path.join(conf_r,  self.entity_name + '.yaml')) as file:
            self.config = yaml.full_load(file)

    def test_table_existance(self):
        tables = self.config[self.entity_name]['tables']

        for i in tables:
            if self.config[self.entity_name]['tables'][i]['table_type'] == 'hub' or \
                    self.config[self.entity_name]['tables'][i]['table_type'] == 'link':
                _hub = i

        error_tables = [i for i in self.exclude_sat_list if i not in tables]
        if len(error_tables) > 0:
            print(colored('Die Folgenden Tabellen gibt es nicht in der entitaet: {0}'.format(', '.join(error_tables)),
                          'red'))
            self.RC += 1
        if (_hub in self.exclude_sat_list):
            print(colored('Der Hub darf nicht ausgeschlossen werden! {0}'.format(_hub),
                          'red'))
            self.RC += 1

    #    db_con, t_name: str, date: str, schema: str

    @property
    def read_entity(self):
        if self.RC < 1:
            con = connect_to_db(layer=self.layer)
            tables = self.config[self.entity_name]['tables']
            _tables = sorted([i for i in tables.keys() if i not in self.exclude_sat_list])
            hk = self.config[self.entity_name]['tables'][_tables[0]]['hash_key']
            dataframes = {}
            for t in _tables:
                if self.config[self.entity_name]['tables'][t]['table_type'] == 'hub' or \
                        self.config[self.entity_name]['tables'][t]['table_type'] == 'link':
                    entity = r_hub(date=self.p_date, t_name=t, db_con=con, schema=self.layer)
                    entity.drop(columns=['index'], inplace=True)
                elif self.config[self.entity_name]['tables'][t]['table_type'] == 'satellit':
                    _r_sat = r_sat(date=self.p_date, t_name=t, db_con=con, schema=self.layer)
                    _r_sat.drop(
                        columns=['index', 'processing_date_start', 'processing_date_end', 'createte_at', 'modified_at',
                                 'record_source', 'diff_hk', 'mod_flg', 'load_domain'], inplace=True)
                    dataframes[t] = _r_sat

            for k, v in dataframes.items():
                entity = entity.merge(v, how='left', on=hk, suffixes=('', '_' + k))

            return entity
        else:
            return None
