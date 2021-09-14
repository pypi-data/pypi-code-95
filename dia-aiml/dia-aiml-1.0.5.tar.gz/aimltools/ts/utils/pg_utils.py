import psycopg2
from psycopg2 import extras
import logging
import pandas as pd
from deprecation import deprecated

logger = logging.getLogger(__name__)

class PGDataAccess:
    
    def __init__(self,USER,PASS,HOST,PORT,DB,SSL,SSL_CERT):
        self.__USER = USER
        self.__PASS = PASS
        self.__HOST = HOST
        self.__PORT = PORT
        self.__DB = DB
        self.__SSL = SSL
        self.__SSL_CERT = SSL_CERT

    def _get_connection(self):
        return self.__connection

    def connect(self):
        try:
            self.__connection = psycopg2.connect(user=self.__USER, password=self.__PASS, host=self.__HOST, port=self.__PORT, database=self.__DB,sslmode=self.__SSL, sslrootcert=self.__SSL_CERT)
        except (Exception, psycopg2.Error) as error:
            logger.error("Error while connecting to PostgreSQL {}".format(error))
    
    
    def disconnect(self):
        self.__connection.close()


    def execute_simple_delete(self, table_name, key_fld, key_val):
        sql_statement = "DELETE FROM {} WHERE {} = %s".format(table_name, key_fld)
        try:
            cur = self.__connection.cursor()
            cur.execute(sql_statement, [key_val])
            self.__connection.commit()
        except Exception as error:
            logger.error("Error while deleting data : {}".format(error), exc_info=True)
        finally:
            cur.close()


    def execute_select(self, sql_statement, params):
        try:
            data = pd.read_sql(sql_statement, self.__connection, params = params)
            return data
        except Exception as error:
            logger.error("Error while reading data : {}".format(error), exc_info=True)

    def execute_simple_select(self, table_name, key_fld, key_val):
        sql_statement = "SELECT * FROM {} WHERE {} = %(key_val)s".format(table_name, key_fld)
        try:
            data = pd.read_sql(sql_statement, self.__connection, params={'key_val': key_val})
            return data
        except Exception as error:
            logger.error("Error while reading data : {}".format(error), exc_info=True)

    @deprecated(deprecated_in="0.9.0", removed_in="1.0.0",
                details="Use PGDataAccess.write_results_bulk(...) from pg_utils.py instead")
    def write_results(self, df, table_name):
        str_col_list = ", ".join(df.columns)
        str_col_placeholders = ", ".join(['%s'] * len(df.columns))
        stmt = "INSERT INTO {} ({}) VALUES({})".format(table_name, str_col_list, str_col_placeholders)
        record_count = 0
        try:
            cur = self.__connection.cursor()
            for index, row in df.iterrows():
                cur.execute(stmt, row.tolist())
                record_count = record_count + cur.rowcount
        except Exception as error:
            logger.error("Error while writing data : {}".format(error), exc_info=True)
            record_count = 0
        finally:
            self.__connection.commit()
            cur.close()
            return record_count


    def write_results_bulk(self, df, table_name):
        str_col_list = ", ".join(df.columns)
        stmt = "INSERT INTO {} ({}) VALUES %s".format(table_name, str_col_list)
        record_count = len(df)
        write_list = list(df.itertuples(index=False, name=None))

        try:
            cur = self.__connection.cursor()
            extras.execute_values(cur, stmt, write_list)
        except Exception as error:
            logger.error("Error while writing data : {}".format(error), exc_info=True)
            record_count = 0
        finally:
            self.__connection.commit()
            cur.close()
            return record_count


    def vacuum_table(self, table_name, vacuum_type = 'partial'):

        if vacuum_type == 'partial':
            vacuum_type = ''

        sql_statement = "VACUUM {} {}".format(vacuum_type, table_name)
    
        try:
            self._get_connection().set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cur = self._get_connection().cursor()
            cur.execute(sql_statement)
            self._get_connection().commit()
            logger.info("Successfully executed VACUUM on table {}".format(table_name))
            self._get_connection().set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_DEFAULT)
        except Exception as error:
            logger.error("Error while performing VACUUM on table {} : {}".format(table_name, error), exc_info=True)
        finally:
            cur.close()

    
    def reindex_table(self):
        table_name = self.__table_name
        sql_statement = "REINDEX TABLE {}".format(table_name)
        try:
            cur = self._get_connection().cursor()
            cur.execute(sql_statement)
            self._get_connection().commit()
            logger.info("Successfully executed REINDEX TABLE on table {}".format(table_name))
        except Exception as error:
            logger.error("Error while performing REINDEX TABLE on table {} : {}".format(table_name, error), exc_info=True)
        finally:
            cur.close()


"""
Used to manage PostgreSQL tables collecting time series values, having following structure:
            VNAME, VTIME, VVALUE, VSTATUS
            - VNAME: name of variable being measured in given record
            - VTIME: time when variable is measured
            - VVALUE: value of VNAME at VTIME (if numeric)
            - VSTATUS: value of VNAME at VTIME (if string or category)
"""
class PGTSTableDataAccess(PGDataAccess):
    """
        Parameters:
        - table_name: name of table
        - name_fld: name of field reporting variable name
        - time_fld: name of field reporting timestamp
        - value_fld: name of field reporting value (if numeric)
        - status_fld: name of field reporting value (if string)
    """
    def setup_mappings(self, table_name, name_fld, time_fld, value_fld, status_fld):
        self.__table_name = table_name
        self.__name_fld = name_fld
        self.__time_fld = time_fld
        self.__value_fld = value_fld
        self.__status_fld = status_fld

    """
    Parameters:
        - columns: name of table columns to be read
        - start: time filter (select records where self.__time_fld > start)
        - end: time filter (select records where self.__time_fld <= end)
        - vnames_list: filter on variable names (select records where self.__name_fld is in vnames_list)
        - order_by: list of list to specify order of records (e.g., [['event_time', 'asc']])
        - status_fld: name of field reporting value (if string) 
    """
    def read_data(self, start, end, vnames_list=[], columns=[], order_by=[]):
        try:
            cols = '*'
            if len(columns) > 0:
                cols = ','.join(columns)

            if len(vnames_list) > 0:
                vn = "('{}')".format("','".join(vnames_list))
                sql = "select {} from {} where (({} > %(start_date)s and {} <= %(end_date)s) and {} in {})".format(
                    cols,
                    self.__table_name,
                    self.__time_fld,
                    self.__time_fld,
                    self.__name_fld,
                    vn
                    )
            else:
                sql = "select {} from {} where (({} > %(start_date)s and {} <= %(end_date)s))".format(
                    cols,
                    self.__table_name,
                    self.__time_fld,
                    self.__time_fld)
            
            if len(order_by) > 0:
                oblist = []
                for itm in order_by:
                    oblist.extend(["{} {}".format(itm[0], itm[1])])
                sql += " order by " + (", ".join(oblist))

            param_dict = {'start_date': start, 'end_date': end}
            data = pd.read_sql(sql, self._get_connection(), params=param_dict)
            return data
        except Exception as error:
            logger.error("Error while reading data : {}".format(error))


    def read_data_count(self, start, end):
        try:
            sql = "select count(*) from {} where {} between %(start_date)s and %(end_date)s".format(self.__table_name, self.__time_fld)
            param_dict = {'start_date': start, 'end_date': end}
            data = pd.read_sql(sql, self._get_connection(), params=param_dict)
            return data.iloc[0][0]
        except Exception as error:
            logger.error("Error while reading data count: {}".format(error))


    def read_cycle_count(self, start, end):
        try:
            sql = "select count(distinct {}) from {} where {} between %(start_date)s and %(end_date)s".format(self.__time_fld, self.__table_name, self.__time_fld)
            param_dict = {'start_date': start, 'end_date': end}
            data = pd.read_sql(sql, self._get_connection(), params=param_dict)
            return data.iloc[0][0]
        except Exception as error:
            logger.error("Error while reading cycle count: {}".format(error))


    def delete_data(self, start, end):
        sql_statement = "DELETE FROM {} WHERE {} > %(start_date)s and {} <= %(end_date)s".format(self.__table_name, self.__time_fld, self.__time_fld)
        try:
            cur = self._get_connection().cursor()
            cur.execute(sql_statement, {"start_date": start, "end_date": end})
            self._get_connection().commit()
        except Exception as error:
            logger.error("Error while deleting data : {}".format(error), exc_info=True)
        finally:
            cur.close()
