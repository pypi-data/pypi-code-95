import pandas as pd
from toolz import first

import sqlalchemy as sa

from zipline.utils.preprocess import preprocess
from zipline.utils.sqlite_utils import coerce_string_to_eng

from zipline.assets.asset_writer import SQLITE_MAX_VARIABLE_NUMBER
from zipline.assets.asset_writer import check_version_info, write_version_info
from zipline.assets.asset_writer import _dt_to_epoch_ns

from fsharadar.db_schema import FSHARADAR_DB_VERSION, db_table_names
from fsharadar.db_schema import metadata, tickers_tbl, version_info_tbl

class DBWriter(object):
    
    DEFAULT_CHUNK_SIZE = SQLITE_MAX_VARIABLE_NUMBER
    
    @preprocess(engine=coerce_string_to_eng(require_exists=False))
    def __init__(self, engine):
        self.engine = engine 
        
    def write_tickers(self, tickers_df, chunk_size=DEFAULT_CHUNK_SIZE):
        
        with self.engine.begin() as trans_ctx:
            
            # Create SQL tables if they do not exist.
            self.init_db(trans_ctx)
            
            if tickers_df is not None:
                self._write_df_to_table(
                    tickers_tbl,
                    tickers_df,
                    trans_ctx,
                    chunk_size,
                )
        
    def init_db(self, trans_ctx):
    
        tables_already_exist = self._all_tables_present(trans_ctx)
        
        # Create the SQL tables if they do not already exist
        metadata.create_all(trans_ctx, checkfirst=True)

        if tables_already_exist:
            check_version_info(trans_ctx, version_info_tbl, FSHARADAR_DB_VERSION)
        else:
            write_version_info(trans_ctx, version_info_tbl, FSHARADAR_DB_VERSION)

                
    def _all_tables_present(self, txn):
 
        ins = sa.inspect(self.engine)
        conn = txn.connect()
        
        for table_name in db_table_names:
            if ins.dialect.has_table(conn, table_name):
                return True
            
        return False
    
    def _write_df_to_table(self, tbl, df, trans_ctx, chunk_size):
        
        df = df.copy()
        
        for column, dtype in df.dtypes.iteritems():
            if dtype.kind == 'M':
                df[column] = _dt_to_epoch_ns(df[column])

        df.to_sql(
            tbl.name,
            trans_ctx.connection,
            index=True, 
            index_label=first(tbl.primary_key.columns).name,
            if_exists='append',
            chunksize=chunk_size,
        )
    
class DBReader(object):
    
    @preprocess(engine=coerce_string_to_eng(require_exists=False))
    def __init__(self, engine):
        self.engine = engine 
        
    def get_tickers(self):
        with self.engine.begin() as conn:
            tickers_df = pd.read_sql_table('tickers', conn)
            
        return tickers_df

def fsharadar_db_relative(bundle_name, timestr):
    return bundle_name, timestr, 'fsharadar-{}.sqlite'.format(FSHARADAR_DB_VERSION)
    
def write_db(tickers_file, table_name, db_path):

    db_writer = DBWriter(db_path)
    
    tickers_df = pd.read_csv(tickers_file)
    
    tickers_df = tickers_df[tickers_df.table == table_name]
    tickers_df = tickers_df.drop(columns=['table'])
    tickers_df.rename(columns={'permaticker': 'sid'}, inplace=True)
    tickers_df = tickers_df.dropna(subset=['ticker'])
    
    usecols = tickers_tbl.columns.keys()
        
    df = tickers_df[usecols]
    df.set_index('sid', inplace=True)
    
    db_writer.write_tickers(df)
