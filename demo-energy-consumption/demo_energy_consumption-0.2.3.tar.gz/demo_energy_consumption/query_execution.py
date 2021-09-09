# -*- coding: utf-8 -*-
"""
Created on Sun Sep  5 17:37:16 2021

@author: denis
"""
import teradataml as tdml

from functools import wraps


def execute_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        query = func(*args, **kwargs)

        con = tdml.get_connection()

        if con:
            con.execute(query)
        else:
            raise Exception(
                """Sorry, There is no connection to a Vantage system.
                Please connect first""")

        return tdml.DataFrame.from_query(query=query)

    return wrapper
