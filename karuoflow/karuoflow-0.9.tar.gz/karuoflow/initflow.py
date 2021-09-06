# -*- encoding: utf-8 -*-
'''
@文件    :initflow.py
@说明    :
@时间    :2020/09/02 22:35:44
@作者    :caimmy@hotmail.com
@版本    :0.1
'''
import os
import yaml
import codecs
from sqlalchemy.orm import Session
from sqlalchemy import and_

from karuoflow.db.tables import TblFlowJob, TblFlowRule
from karuoflow.db.session import createDbSession
from karuoflow.datadef import DbConfig
# from .db.tables import TblFlowJob, TblFlowRule


def InitializeFlowsFromConfigure(config_path: str, dbsession: Session):
    """
    从配置文件目录加载所有流程
    config_path: str 配置文件路径
    dbsession: Session 数据库会话
    """
    files = os.listdir(config_path)
    handle_result = {
        "total": 0,             # 共有审批流程数
        "skip": 0,              # 跳过流程数
        "success": 0,           # 建立成功的流程数
        "failure": 0            # 建立失败的流程数
    }
    for _f in files:
        _f_config = os.path.join(config_path, _f)
        if os.path.isfile(_f_config):
            handle_result["total"] += 1
            # 解析yaml配置文件
            with codecs.open(_f_config, "r", "utf-8") as _cf:
                _rule = yaml.load(_cf.read(), yaml.FullLoader)
                if _check_config_rule_valid(_rule):
                    _g_ret = _generationDBRecords(dbsession, _rule)
                    if -1 == _g_ret:
                        handle_result["failure"] += 1
                    elif 0 == _g_ret:
                        handle_result["skip"] += 1
                    elif 1 == _g_ret:
                        handle_result["success"] += 1
    return handle_result

def InitializeFlowsFromConfigureWithDbConfig(configpath:str, host, port, db, user, password):
    return InitializeFlowsFromConfigure(configpath, createDbSession(DbConfig(host, db, user, password, port), True))

def _check_config_rule_valid(apply_rule: dict):
    """
    @return bool
    """
    if "catalog" in apply_rule and "version" in apply_rule:
        if "flow" in apply_rule:
            _flows = apply_rule.get("flow")
            if isinstance(_flows, list) and 1 < len(_flows):
                return True
    return False

def _generationDBRecords(dbsession: Session, apply_rule: dict):
    """
    @return int , -1：流程创建失败；0：流程已存在，跳过；1：流程创建成功
    """
    _ret_code = -1
    # 1 check the rule if exists or not.
    _catalog = apply_rule.get("catalog")
    _subflow = apply_rule.get("subflow")
    _version = apply_rule.get("version")
    _name = apply_rule.get("name")
    _apply_flows = apply_rule.get("flow")
    _publisher = apply_rule.get("publisher") if "publisher" in apply_rule else ""

    if not dbsession.query(dbsession.query(TblFlowRule).filter(and_(
                TblFlowRule.catalog == _catalog,
                TblFlowRule.subflow == _subflow,
                TblFlowRule.version == _version,
                TblFlowRule.status == '1'
            )).exists()).scalar():
        start_node = None
        close_node = None
        _middle_nodes = []

        if 2 == len(_apply_flows):
            start_node = _apply_flows[0]
            close_node = _apply_flows[1]
        elif 2 < len(_apply_flows):
            start_node = _apply_flows[0]
            close_node = _apply_flows[-1]
            _middle_nodes = _apply_flows[1:-1]
        _prev_id = 0
        if start_node and close_node:
            try:
                _start_flow = TblFlowRule()
                _start_flow.prev_id = 0
                _start_flow.publisher = _publisher
                _start_flow.catalog = _catalog
                _start_flow.subflow = _subflow
                _start_flow.name = _name
                _start_flow.node_label = "start"
                _start_flow.version = _version
                _start_flow.method = start_node.get("method")
                _start_flow.reviewer = start_node.get("reviewer") if "reviewer" in start_node else []
                _start_flow.ext_prop = start_node.get("ext_prop")
                _start_flow.memo = start_node.get("memo")
                dbsession.add(_start_flow)
                dbsession.flush()
                _prev_id = _start_flow.id

                for _m_item in _middle_nodes:
                    _item_node = TblFlowRule()
                    _item_node.prev_id = _prev_id
                    _item_node.publisher = _publisher
                    _item_node.catalog = _catalog
                    _item_node.subflow = _subflow
                    _item_node.name = _name
                    _item_node.node_label = _m_item.get("node") if "node" in _m_item else "middle"
                    _item_node.version = _version
                    _item_node.method = _m_item.get("method")
                    _item_node.reviewer = _m_item.get("reviewer") if "reviewer" in _m_item else []
                    _item_node.ext_prop = _m_item.get("ext_prop")
                    _item_node.memo = _m_item.get("memo")
                    dbsession.add(_item_node)
                    dbsession.flush()
                    _prev_id = _item_node.id
                
                _end_flow = TblFlowRule()
                _end_flow.prev_id = _prev_id
                _end_flow.publisher = _publisher
                _end_flow.catalog = _catalog
                _end_flow.subflow = _subflow
                _end_flow.name = _name
                _end_flow.node_label = "close"
                _end_flow.reviewer = close_node.get("reviewer") if "reviewer" in close_node else []
                _end_flow.ext_prop = close_node.get("ext_prop")
                _end_flow.version = _version
                _end_flow.method = close_node.get("method")
                _end_flow.memo = close_node.get("memo")
                dbsession.add(_end_flow)
                
                dbsession.commit()
                _ret_code = 1

            except Exception as e:
                dbsession.rollback()
                print(e)
                _ret_code = -1
            finally:
                dbsession.close()
        else:
            _ret_code = -1            
    else:
        _ret_code = 0
    return _ret_code
        
    

if "__main__" == __name__:
    # dbsess = createDbSession(DbConfig('218.89.168.173', 'duoneng', 'root', 'Net.info.2006'), True)
    
    data = InitializeFlowsFromConfigureWithDbConfig("/data/work/karuoflow/examples/", '218.89.168.173', 3306, 'duoneng', 'root', 'Net.info.2006')
    print(data)