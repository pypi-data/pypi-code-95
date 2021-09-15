import os
from google.cloud import bigquery


def authenticate():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bigquerycred.json"


def get_table_sample(schema, table, nrows):
    client = bigquery.Client()
    sql_call = f"SELECT * FROM {schema}.{table} WHERE RAND() < {nrows}/(SELECT COUNT(*) FROM {schema}.{table})"
    query_job = client.query(sql_call)
    return query_job.to_dataframe()


def get_table_dtypes(schema, table):
    client = bigquery.Client()
    sql_call = f"SELECT column_name, data_type FROM {schema}.INFORMATION_SCHEMA.COLUMNS WHERE table_name='{table}'"
    query_job_dtypes = client.query(sql_call)
    return query_job_dtypes.to_dataframe()