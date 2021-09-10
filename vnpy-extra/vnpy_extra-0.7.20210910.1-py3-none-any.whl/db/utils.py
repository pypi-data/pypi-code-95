"""
@author  : MG
@Time    : 2020/12/23 13:42
@File    : utils.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""


def is_table_exists(table_name, schema=None):
    from .orm import database
    try:
        return database.table_exists(table_name, schema)
    finally:
        database.close()


def execute_sql(sql_str, params=None):
    """执行数据库语句"""
    from .orm import database
    try:
        return database.execute_sql(sql_str, params)
    finally:
        database.close()


if __name__ == "__main__":
    pass
