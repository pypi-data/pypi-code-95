import os
from google.cloud import bigquery


def authenticate(filename):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = filename


def get_table_sample(project_ID: str, schema_name: str, table_name: str, nrows: int):
    client = bigquery.Client(project_ID)
    sql_call = f"SELECT * FROM {schema_name}.{table_name} WHERE RAND() < {nrows}/(SELECT COUNT(*) FROM {schema_name}.{table_name})"
    query_job = client.query(sql_call)
    return query_job.to_dataframe()


def get_table_dtypes(project_ID: str, schema_name: str, table_name: str):
    client = bigquery.Client(project_ID)
    sql_call = f"SELECT column_name, data_type FROM {schema_name}.INFORMATION_SCHEMA.COLUMNS WHERE table_name='{table_name}'"
    res = client.query(sql_call)
    return {row[0]: row[1] for row in res.result()}


def get_num_null(project_ID: str, schema_name: str, table_name: str):
    client = bigquery.Client(project_ID)
    res = client.query(f"""
        SELECT col_name, COUNT(1) nulls_count
        FROM `{schema_name}.{table_name}` t, UNNEST(REGEXP_EXTRACT_ALL(TO_JSON_STRING(t), r'"(\w+)":null')) col_name
        GROUP BY col_name
        """)
    return {row[0]: row[1] for row in res.result()}


def metrics_numeric(project_ID: str, schema_name: str, table_name: str, col_name: str, dtype: str):
    client = bigquery.Client(project_ID)
    res = client.query(f"""
        SELECT COUNT(DISTINCT {col_name}) unique, 
        MIN({col_name}) min, 
        MAX({col_name}) max, 
        COUNTIF({col_name} IS NULL) null_count
        FROM `{schema_name}.{table_name}`
        """)
    for row in res.result():
        return {"dtype": dtype, "unique": row[0],"min": row[1], "max": row[2], "num_null": row[3]}


def metrics_string(project_ID: str, schema_name: str, table_name: str, col_name: str, dtype: str):
    client = bigquery.Client(project_ID)
    res = client.query(f"""
        SELECT COUNT(DISTINCT {col_name}), 
        COUNTIF({col_name} IS NULL) null_count
        FROM `{schema_name}.{table_name}`    
        """)
    for row in res.result():
        return {"dtype": dtype, "unique": row[0], "num_null": row[1]}


def metrics_date(project_ID: str, schema_name: str, table_name: str, col_name: str, dtype: str):
    client = bigquery.Client(project_ID)
    res = client.query(f"""
        SELECT COUNT(DISTINCT {col_name}), 
        MIN({col_name}), 
        MAX({col_name}), 
        COUNTIF({col_name} IS NULL) null_count
        FROM `{schema_name}.{table_name}`    
        """)
    for row in res.result():
        return {"dtype": dtype, "unique:": row[0], "min": row[1], "max": row[2], "num_null": row[3]}


def column_metrics(project_ID: str, schema_name: str, table_name: str, column_name: str, dtype: str):
    if dtype == "STRING":
        return metrics_string(project_ID, schema_name, table_name, column_name, dtype)
    elif dtype == "DATE":
        return metrics_date(project_ID, schema_name, table_name, column_name, dtype)
    elif dtype == "FLOAT64" or dtype == "INT64":
        return metrics_numeric(project_ID, schema_name, table_name, column_name, dtype)
    else:
        return {"dtype": dtype}


def table_metrics(project_ID: str, schema_name: str, table_name: str):
    out = {}
    dtypes = get_table_dtypes(project_ID, schema_name, table_name)
    for col, data_type in dtypes.items():
        out[col] = column_metrics(project_ID, schema_name, table_name, col, data_type)
    return out