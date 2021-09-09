# -*- coding: utf-8 -*-
import os
import dictdiffer
# yaml

import yaml
from yaml import Loader

# django Imports
from django.db.models.signals import post_delete, post_save,pre_save
from django.dispatch import receiver
from django.conf import settings

# App Imports
from track_actions.constants import TABLES
from track_actions.models import History
from track_actions.requestMiddleware import RequestMiddleware

# python imports
import datetime
import json

# def show_change(olddict,newdict):
#     """比较两个字典 返回如  [{'field': 'data.sex', 'old': '\xe7\x94\xb7', 'new': '\xe5\xa5\xb3'}, {'field': 'template', 'old': '', 'new': '11'}] """
#     changelist = []
#
#     for diff in list(dictdiffer.diff(olddict, newdict)):
#         changedict = {}
#         diff  = list(diff)
#         if diff[0] == "change":
#             changedict["field"] = diff[1]
#             changedict["old"] = diff[2][0]
#             changedict["new"] = diff[2][1]
#             changelist.append(changedict)
#     return changelist
#
#
#
#
# @receiver(pre_save)
# @receiver(post_delete)
# def track_user_actions(sender, instance, **kwargs):
#     """Signal function to track every change to a model
#
#     Arguments:
#         sender {object} -- The model sending the signal
#         instance {object} -- data instance
#     """
#
#     # print("updayefields",kwargs)
#     # 拿到实例后跟实例之前的进行比较 保存到一个记录里面 不要保存到多条记录里面
#
#     # 先获取原有的序列化的内容   监听应该在presave
#
#
#
#     current_request = RequestMiddleware.get_request_data()[1]
#
#     # 获取序列化器
#     request_url =current_request.path
#
#     if (
#         sender._meta.db_table not in TABLES
#         and hasattr(current_request, "user")
#         and hasattr(instance, "id")
#     ):
#         if RequestMiddleware.get_request_data()[0]:
#             request_data = decode_json(RequestMiddleware.get_request_data()[0])
#         else:
#             request_data = ""
#         data = instance.__dict__.copy()
#         data.__delitem__("_state")
#         if "drf_history.yaml" in os.listdir(settings.BASE_DIR):
#             yaml_file = open(settings.BASE_DIR + "/drf_history.yaml", "r")
#             yaml_content = yaml.load(yaml_file, Loader=Loader)
#             if (
#                 type(yaml_content) is dict
#                 and type(request_data) is dict
#                 and "fields_to_exclude" in yaml_content.keys()
#                 and type(yaml_content["fields_to_exclude"]) is list
#             ):
#                 feilds_to_exclude = yaml_content["fields_to_exclude"]
#                 [request_data.pop(key, None) for key in feilds_to_exclude]
#
#         save_history(instance, current_request, request_data, data)
#
#
# def decode_json(data):
#     request_data = ""
#     try:
#         request_data = json.loads(data)
#     except:
#         pass
#     return request_data
#
#
# def save_history(instance, current_request, request_data, data):
#     try:
#         history = History(
#             table_name=str(instance._meta.db_table),
#             user=current_request.user,
#             instance_id=instance.id,
#             action=current_request.method,
#             request_data=request_data,
#             path=current_request.path,
#             response_data=data,
#         )
#         history.save()
#     except ValueError:
#         pass
#
#
# if __name__ == '__main__':
#     second_dict = {
#         "template": "",
#         "template2": "",
#         "data": {
#             "name": "鸣人",
#             "age": 22,
#             "sex": "男",
#             "title": "六代火影"
#         }  # 数据
#     }
#
#     first_dict = {
#         "template": "11",
#         "template1": "11",
#         "data": {
#             "name": "鸣人",
#             "age": 22,
#             "sex": "女",
#             "title": "六代火影"
#         }  # 数据
#     }
#     change = show_change(second_dict,first_dict)
#     print(change)