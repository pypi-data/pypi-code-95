import uuid
from datetime import datetime
from python_wrap_gcp.docs import config

WORKER_ID = uuid.uuid4().hex[:6]


def conn_db(config_class):
    from sqlalchemy import create_engine
    return create_engine(
        f"{config_class.CONNECTION_TYPE}://{config_class.USERNAME}:{config_class.PASSWORD}@{config_class.HOST}:{config_class.PORT}/{config_class.DATABASE}{config_class.CONFIG}?charset=UTF8MB4",
    pool_recycle=3600)


def log(stack_inspect, msg, status, to_database=False, **kwargs):
    dt = datetime.utcnow()
    _time = str(dt)[11:-5]
    scope = stack_inspect[0][1].split('/')[-1]
    method = stack_inspect[0][3]
    print(f"[{_time}]-[{scope}]-[{method}]-[{msg}]-[{status}]-[{WORKER_ID}]")
    if to_database:
        conn_db(config.AppDBConfig).execute(
            "INSERT INTO logs (date_time, scope, method, msg, status, worker_id) VALUES ('{}','{}','{}','{}','{}','{}');".format(
                str(dt)[:-5], scope, method, msg, status, WORKER_ID))
