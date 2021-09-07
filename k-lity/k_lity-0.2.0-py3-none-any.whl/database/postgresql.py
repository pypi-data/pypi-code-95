# encoding: utf-8
"""
K-lity module to manage postgresql databases.
"""

import psycopg2


def postgresql_connect(configuration):
    """
    Opening connection to postgresql database.
    """
    # Default values
    if "host" not in configuration or configuration["host"] == "":
        configuration["host"] = "127.0.0.1"
    if "port" not in configuration or configuration["port"] == "":
        configuration["port"] = 5432
    # Connection to database
    return {
        "type": "postgresql",
        "connection": psycopg2.connect(
            host=configuration["host"],
            port=configuration["port"],
            database=configuration["database"],
            user=configuration["user"],
            password=configuration["password"],
        ),
    }


def postgresql_execute(connection, request, parameters):
    result = None
    cursor = connection["connection"].cursor()
    cursor.execute(request, parameters)
    result = {
        "columns": [],
        "query": cursor.query,
        "rowcount": cursor.rowcount,
        "lastrowid": cursor.lastrowid,
        "results": [],
    }
    try:
        result["columns"] = [column[0] for column in cursor.description]
        result["results"] = cursor.fetchall()
    except:
        # No result to fetch...
        pass
    connection["connection"].commit()
    cursor.close()
    return result


def postgresql_close(connection):
    connection["connection"].close()
