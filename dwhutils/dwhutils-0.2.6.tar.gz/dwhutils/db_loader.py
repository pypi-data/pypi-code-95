import datetime
import hashlib
import os

import numpy as np
import pandas as pd
import yaml
from dotenv import load_dotenv
from dwhutils.utils import divide_chunks
from sqlalchemy import MetaData
from termcolor2 import colored


def element_is_in(comparelist, element):
    if element in comparelist:
        return element


def element_is_not_in(comparelist, element):
    if element not in comparelist:
        return element


class LoadtoDB():
    def __init__(self, data: pd.DataFrame, db_con, t_name, load_domain: str, date: str = None, schema: str = None,
                 commit_size: int = 10000, entityName: str = None, useSingeFetch=False):
        '''

        :param data: Data that should write to Database
        :param db_con: Connection to TargetDatabase (singleton)
        :param t_name: Tablename
        :param date: date to insert
        :param schema: database schema to insert
        :param commit_size: how many rows shode be insertet in parralel
        :param entityName: what entity is it? used for config read
        :param useSingeFetch: should all old data fetched in one ore in single rows? (used for update)
        '''
        load_dotenv()
        self.data = data
        self.db_con = db_con
        self.t_name = t_name
        self.schema = schema
        self.load_domain = load_domain
        self.commit_size = commit_size
        self.target_table = None
        self.entityName = entityName
        self.useSingeFetch = useSingeFetch

        config_file = os.getenv('DB_CONFIG')
        kp_path = os.getenv('KEYPASS')
        conf_r = os.getenv('ENTITY_CONFIGS')
        if date == None:
            self.processing_date_start = datetime.date.today().strftime("%Y-%m-%d")
        else:
            self.processing_date_start = date


        if entityName is None:
            with open(os.path.join(conf_r , t_name + '.yaml')) as file:
                self.documents = yaml.full_load(file)
            self.hk = self.documents[t_name]['hash_key']
            self.fields = self.documents[t_name]['fields']
        else:
            with open(os.path.join(conf_r , self.entityName + '.yaml')) as file:
                self.documents = yaml.full_load(file)
            self.hk = self.documents[entityName]['tables'][self.t_name]['hash_key']
            self.fields = self.documents[entityName]['tables'][self.t_name]['fields']

        self.metadata = MetaData(bind=self.db_con)
        self.metadata.reflect(bind=self.db_con, schema=self.schema)

        for table in [i for i in reversed(self.metadata.sorted_tables) if self.t_name == i.name]:
            self.target_table = table

            for c in self.target_table.columns:
                if self.hk in c.name:
                    col = c

        try:
            stmt = "select {0} from {1}.{2} where load_domain='{3}'".format(self.hk, self.schema, self.t_name,
                                                                            self.load_domain)
            table_hk = list(db_con.execute(stmt).fetchall())
        except:
            stmt = "select {0} from {1}.{2}".format(self.hk, self.schema, self.t_name)
            table_hk = list(db_con.execute(stmt).fetchall())

        table_hk = [i[0] for i in table_hk]
        df_hk = list(self.data[self.hk])

        table_hk_df = pd.DataFrame(data=table_hk, columns=['table_hk'])

        df_hk_df = pd.DataFrame(data=df_hk, columns=['df_hk'])

        insrt_khs = df_hk_df.merge(table_hk_df, how='left', left_on='df_hk', right_on='table_hk')
        insrt_khs = insrt_khs[insrt_khs['table_hk'].isna()]
        insrt_khs['hks'] = insrt_khs['df_hk']

        del_khs = table_hk_df.merge(df_hk_df, how='left', left_on='table_hk', right_on='df_hk')
        updt_khs = df_hk_df.merge(table_hk_df, how='inner', left_on='df_hk', right_on='table_hk')

        insrt_khs.drop(['df_hk', 'table_hk'], axis=1)

        del_khs['hks'] = del_khs['table_hk']
        del_khs.drop(['df_hk', 'table_hk'], axis=1)

        updt_khs['hks'] = updt_khs['df_hk']
        self.update_hk = updt_khs
        self.update_hk = updt_khs.drop(['df_hk', 'table_hk'], axis=1)
        self.insert_df = data.merge(insrt_khs, how='inner', left_on=self.hk, right_on='hks')
        self.insert_df.drop(['hks'], axis=1)

        self.delete_df = data.merge(del_khs, how='inner', left_on=self.hk, right_on='hks')
        self.delete_df.drop(['hks'], axis=1)

        self.update_df = data.merge(self.update_hk, how='inner', left_on=self.hk, right_on='hks')
        self.update_df.drop(['hks'], axis=1)

        del (insrt_khs, del_khs, updt_khs, table_hk_df, df_hk_df)

    def __repr__(self):
        repr_str = 'table: ' + self.target_table.name + '\n' \
                   + colored('INFO: insert: ' + str(len(self.insert_hk)), 'green') + '\n' \
                   + colored('INFO: delete:' + str(len(self.delete_hk)), 'green') + '\n' \
                   + colored('INFO: updates:' + str(self.update.shape[0]), 'green')

        return repr_str

    def insert(self):
        print("Insert")
        conn = self.db_con.connect()
        self.insert_df.drop_duplicates(inplace=True)
        self.insert_df = self.insert_df[self.insert_df[self.hk].notna()]
        if self.insert_df.shape[0] > 0:

            self.insert_df['processing_date_start'] = self.processing_date_start
            _anz = 1
            record_list = self.insert_df.to_dict('records')
            chunks = list(divide_chunks(record_list, self.commit_size))
            for i in chunks:
                self.target_table.name = self.t_name
                conn.execute(self.target_table.insert(), i)
                conn.execute('commit')
        else:
            print('Nichts zu inserten')

    def delete(self):
        print("Delete")
        if self.delete_df.shape[0] > 0:
            conn = self.db_con.connect()
            conn.close()
        else:
            print('Nichts zu loeschen')

    def compare(self, x):
        if x["diff_hk"] == self.diff_hk_lkp[x[self.hk]]:
            return 1
        else:
            return 0

    def get_old_data(self):
        conn = self.db_con.connect()
        fields = list(self.fields)

        table_u_hk = "('" + "','".join(self.update_hk) + "')"

        count_stmt = "select count(*) from " + self.schema + "." + self.target_table.name + " where " + self.hk + " in " + table_u_hk + \
                     " and processing_date_end='2262-04-11';"

        result_count = conn.execute(count_stmt).fetchall()
        result_count = result_count[0][0]
        chunks = np.ceil(result_count / self.commit_size)

        fields_with_hk = fields
        fields_with_hk.append(self.documents[self.entityName]['tables'][self.t_name]['hash_key'])
        fields_types = self.documents[self.entityName]['tables'][self.t_name]['data_types']
        fields_types.append('str')

        stmt_diffs = "select  " + ','.join(
            fields_with_hk) + " from " + self.schema + "." + self.target_table.name + " where " + self.hk + " in " + \
                     table_u_hk + " and processing_date_end='2262-04-11';"
        result = conn.execute(stmt_diffs)
        _df_list = []

        rel_types = {}
        parse_list = []
        for k, i in enumerate(fields):
            try:
                if fields_types[k] != 'DATUM':
                    rel_types[i] = fields_types[k]
                else:
                    rel_types[i] = 'str'
                    parse_list.append(i)
            except:
                if fields_types[k] != 'DATUM':
                    rel_types[i] = fields_types[k]
                else:
                    rel_types[i] = 'str'
                    parse_list.append(i)

        if self.useSingeFetch and chunks > 1:
            for i in range(int(chunks)):
                _df_list.append(pd.DataFrame(columns=fields_with_hk, data=result.fetchmany(self.commit_size)).astype(
                    dtype=rel_types))
            old_data = pd.merge(_df_list)
        else:
            old_data = pd.DataFrame(columns=fields_with_hk, data=conn.execute(stmt_diffs).fetchall()).astype(
                dtype=rel_types)
            old_data[parse_list] = old_data[parse_list].apply(lambda x: pd.to_datetime(x), axis=1)
        return old_data

    def update_v2(self):
        fields = list(self.fields)
        if len(self.update_df[self.hk]) > 0:
            conn = self.db_con.connect()
            old_data = self.get_old_data()

            merged_df = self.update_df.merge(old_data, how='inner', on=self.hk, suffixes=('', '_'))
            diff_hks = []
            for hk in list(self.update_df[self.hk]):
                for c in fields:
                    if c not in [self.hk]:
                        _temp = merged_df[merged_df[self.hk] == hk]
                        if _temp.shape[0] > 0:
                            try:
                                _t1 = round(_temp[c].values[0], 0)
                                _t2 = round(_temp[c + '_'].values[0], 0)
                            except:
                                try:
                                    _t1 = _temp[c].values[0]
                                    _t2 = _temp[c + '_'].values[0]
                                except:
                                    pass

                            if _t1 != _t2:
                                diff_hks.append(hk)

            update_df = self.update_df[self.update_df[self.hk].isin(diff_hks)]
            k = [i for i in fields if i != self.hk]
            update_df['diff_str'] = update_df[k].astype(str).agg('|'.join, axis=1)
            update_df["diff_hk"] = update_df['diff_str'].astype(str).apply(
                lambda x: hashlib.md5(x.encode()).hexdigest().upper())
            if update_df.shape[0] > 0:
                chunk_stmt = []
                for row in range(update_df.shape[0]):
                    record = update_df.iloc[row]
                    u_hk = record[self.hk]
                    set_part = []
                    for col in fields:
                        set_part.append(self.target_table.name + "." + col + "=" + "'" + str(record[col]) + "'")
                    set_part = ",\n".join(set_part)

                    stmt3 = "UPDATE " + self.schema + "." + self.target_table.name + " FOR PORTION OF business_time FROM '"\
                            + self.processing_date_start + "' TO '2262-04-11' SET " + set_part + ", mod_flg = 'U'  WHERE " \
                            + self.hk + " = '" + u_hk + "';"
                    chunk_stmt.append(stmt3)
                st = ';'.join(chunk_stmt) + ";"
                conn.execute(st)

                conn.execute('commit')
                if row % 100 == 0:
                    print('.', end=' ')
        else:
            print('Keine Updates Vorhanden')

    def update(self):
        conn = self.db_con.connect()
        fields = self.fields
        fields.append('diff_hk')
        table_u_hk = "('" + "','".join(self.update_hk) + "')"
        stmt_diffs = "select diff_hk, " + self.hk + " from " + self.schema + "." + self.target_table.name + " where " + self.hk + " in " + table_u_hk + \
                     " and processing_date_end='2262-04-11';"
        table_u_list = self.db_con.execute(stmt_diffs).fetchall()
        table_u_df = pd.DataFrame(columns=['diff_hk', self.hk])
        for i in table_u_list:
            table_u_df = table_u_df.append({'diff_hk': i[0], self.hk: i[1]}, ignore_index=True)

        self.update_df['processing_date_start'] = self.processing_date_start  # update auf bestimmtes datum
        self.update_df['diff_str'] = self.update_df.astype(str).agg('|'.join, axis=1)
        self.update_df["diff_hk"] = self.update_df['diff_str'].astype(str).swifter.apply(
            lambda x: hashlib.md5(x.encode()).hexdigest().upper())
        self.update_df.drop(inplace=True, columns='diff_str')

        join_update = self.update_df.swifter.merge(table_u_df, how='inner', on=self.hk, suffixes=['', '_tudf'])

        self.update = join_update[join_update['diff_hk'] != join_update['diff_hk_tudf']]
        print(colored('INFO: update:' + str(self.update.shape[0]), 'green'))

        if self.update.shape[0] > 0:
            for row in range(self.update.shape[0]):
                record = self.update.iloc[row]
                u_hk = record[self.hk]
                set_part = []
                for col in fields:
                    set_part.append(self.target_table.name + "." + col + "=" + "'" + str(record[col]) + "'")
                set_part = ",\n".join(set_part)
                stmt3 = "UPDATE " + self.schema + "." + self.target_table.name + " FOR PORTION OF business_time FROM '" + self.processing_date_start + "' TO '2262-04-11' SET " + set_part + ", mod_flg = 'U'  WHERE " + self.hk + " = '" + u_hk + "';"

                conn.execute(stmt3)
                if row % self.commit_size == 0:
                    conn.execute('commit')
                if row % 100 == 0:
                    print('.', end=' ')

        conn.close()
