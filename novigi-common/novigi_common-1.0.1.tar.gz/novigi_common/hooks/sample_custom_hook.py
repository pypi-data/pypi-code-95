from airflow.hooks.base_hook import BaseHook



class CustomHook(BaseHook):

    def __init__(self, *args, **kwargs):
        print('Hello in Init')
        conn = self.get_connection('mssql_default')
        print(f"AIRFLOW_CONN_{conn.conn_id.upper()}='{conn.get_uri()}'")