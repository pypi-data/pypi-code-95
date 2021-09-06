# -*- encoding: utf-8 -*-
'''
@文件    :session.py
@说明    :
@时间    :2020/09/02 11:47:10
@作者    :caimmy@hotmail.com
@版本    :0.1
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from ..datadef import DbConfig

def createDbSession(db_config: DbConfig, debugMode:bool = False):
    """
    创建数据库会话
    """
    _engine = create_engine(f"mysql+pymysql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.dbname}?charset=utf8mb4", \
        encoding="utf-8", echo=debugMode,  pool_size=db_config.pool_size, pool_recycle=db_config.pool_recycle)

    return scoped_session(sessionmaker(bind=_engine, autocommit=False, autoflush=False, expire_on_commit=False))