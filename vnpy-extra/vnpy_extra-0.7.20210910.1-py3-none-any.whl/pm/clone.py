#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/8/25 14:15
@File    : clone.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
from vnpy_extra.db.orm import AccountStrategyMapping


def clone_account_stg_mapping(from_user_name, from_broker_id, to_user_name, to_broker_id):
    AccountStrategyMapping.clone_mapping(from_user_name, from_broker_id, to_user_name, to_broker_id)
