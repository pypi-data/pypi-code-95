# -*- encoding: utf-8 -*-
'''
@文件    :datadef.py
@说明    :
@时间    :2020/09/02 21:54:28
@作者    :caimmy@hotmail.com
@版本    :0.1
'''

from dataclasses import dataclass, field

# 审批方法： 会签
SIGN_METHOD_JOINT   = "joint"
# 审批方法： 或签
SIGN_METHOD_OR      = "or"

@dataclass
class DbConfig:
    """
    数据库的配置参数
    """
    host: str
    dbname: str
    user: str
    password: str
    port: int = 3306

    pool_size: int = 100
    pool_recycle: int = 600

@dataclass
class FlowCustomRuleNode:
    """
    自由定义的审核流程规则
    """
    catalog: str
    reviewer: list
    subflow: str = ""
    name: str = ""
    node_label: str = ""
    version: int = 1
    ext_prop: dict = field(default_factory=dict)
    status: int = 1
    memo: str = ""
    icon: str = ""
    method: str = ""

    def toDict(self):
        return {
            "catalog": self.catalog,
            "reviewer": self.reviewer,
            "subflow": self.subflow,
            "name": self.name,
            "node_label": self.node_label,
            "version": self.version,
            "ext_prop": self.ext_prop,
            "status": self.status,
            "memo": self.memo,
            "icon": self.icon,
            "method": self.method
        }

@dataclass
class OperResult:
    """
    操作的返回结果，携带操作结果信息
    """
    code: int = -1
    msg: str = "gen error"
    data: dict = field(default_factory=dict)

    @property
    def toDict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }

    @property
    def isSuccess(self):
        """
        判断操作是否成功
        :return bool
        """
        return 0 == self.code

    def setSuccess(self, data={}):
        self.code = 0
        self.msg = ""
        self.data = data

    def setNotExists(self):
        self.code = 404
        self.msg = "not exists"

    def setErrorInfor(self, code, msg):
        """
        设置错误信息
        :param code 错误码
        :param msg 错误消息
        """
        self.code = code
        self.msg = msg


class QueryParams:
    def __init__(self):
        self.matches = {}
        self.contains = {}
        self.in_ = {}
    
    def setMatches(self, match_param: dict):
        self.matches.update(match_param)

    def setContains(self, contain_param: dict):
        self.contains.update(contain_param)

    def setIns(self, ins_param:dict):
        self.in_.update(ins_param)
