import os
from google.cloud import bigquery


project_ID = "dataplattform-dev-9da3"
schema_name = "fist_syntetiske_data"


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
    res = client.query(sql_call)
    return {row[0]: row[1] for row in res.result()}

def get_num_null(bq_table: str):
    client = bigquery.Client("dataplattform-dev-9da3")
    res = client.query(f"""
    SELECT col_name, COUNT(1) nulls_count
    FROM `{project_ID}.{schema_name}.{bq_table}` t, UNNEST(REGEXP_EXTRACT_ALL(TO_JSON_STRING(t), r'"(\w+)":null')) col_name
    GROUP BY col_name
    """)
    return {row[0]: row[1] for row in res.result()}

def metrics_numeric(bq_table: str, col_name: str):
    client = bigquery.Client("dataplattform-dev-9da3")
    res = client.query(f"""
    SELECT min({col_name}) min, max({col_name}) max
    FROM `{project_ID}.{schema_name}.{bq_table}`    
    """)
    for row in res.result():
        return {"min": row[0], "max": row[1]}

def metrics_string(bq_table: str, col_name: str):
    client = bigquery.Client("dataplattform-dev-9da3")
    res = client.query(f"""
    SELECT COUNT(DISTINCT {col_name})
    FROM `{project_ID}.{schema_name}.{bq_table}`    
    """)
    return {"unique": row[0] for row in res.result()}

def metrics_date(bq_table: str, col_name: str):
    client = bigquery.Client("dataplattform-dev-9da3")
    res = client.query(f"""
    SELECT COUNT(DISTINCT {col_name}), MIN({col_name}), MAX({col_name})
    FROM `{project_ID}.{schema_name}.{bq_table}`    
    """)
    for row in res.result():
        return {"unique:": row[0], "min": row[1], "max": row[2]}