import pandas as pd
from sqlalchemy import create_engine




class AWS_Engine:
  def __init__(self, credentials:dict):
    end_point = credentials["endpoint"]
    port = credentials["port"]
    db_identifier = credentials["db_identifier"]
    password = credentials["password"]
    self.engine = create_engine(f'postgresql://postgres:{password}@{end_point}/{db_identifier}').connect()

  def sql_to_df(self, query_filepath):
    query = open(f'{query_filepath}', 'r')
    df = pd.read_sql_query(query.read(), self.engine)
    query.close()
    return df

  def df_to_rds(self, df, table_name):
    df.to_sql(con=self.engine, name=f"{table_name}", if_exists='replace', chunksize=100, index=False)

  def insert_to_rds(self, df, cols, table_name):
    for row in df.itertuples():
      self.engine.execute(f'''
                    INSERT INTO {table_name} {cols}
                    VALUES {row}
                    '''
                     )