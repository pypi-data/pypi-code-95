#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Author: 陈乾
#@Version: 1.0
#@Filename: __init__.py
#@Time: 2021/09/09 23:01
import json
import requests
import datetime
from hashlib import sha256


def login(cardNo:str, password:str) -> json:
    """健康管控平台登录
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :param: cardNo: 账号
    :param: password: 密码
    :return: token, data: token和登录信息
    """
    loginUrl = "http://hmgr.sec.lit.edu.cn/wms/healthyLogin"
    headers = {
        'Host': "hmgr.sec.lit.edu.cn",
        'Referer': "http://hmgr.sec.lit.edu.cn/web/",
        'Content-Type': "application/json;charset=UTF-8;Access-Control-Allow-Headers",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    }
    if not isinstance(cardNo, str):
        try:
            cardNo = str(cardNo)
        except Exception:
            raise Exception("The cardNo must be String or can be transformed to String.")
    if not isinstance(password, str):
        try:
            password = str(password)
        except Exception:
            raise Exception("The password must be String or can be transformed to String.")
    password = sha256(password.encode('utf-8')).hexdigest()
    data = {
        'cardNo': cardNo,
        'password': password
    }
    data = json.dumps(data)
    try:
        response = requests.post(url=loginUrl, headers=headers, data=data, timeout=2)
    except requests.exceptions.ConnectionError:
        raise Exception("Please check your network.")
    except Exception as e:
        print(e)
    else:
        try:
            response = response.json()
        except Exception:
            print(response.text)
            raise Exception("The response is not json format.")
        else:
            code = response['code']
            if code == 4001:
                raise Exception("The cardNo is not exist. Please check the cardNo you gave.")
            elif code == 4002:
                raise Exception("The password is wrong. Please check the password you gave.")
            elif code == 200:
                return response['data']
            else:
                print(response)
                raise Exception("Unkown error.")

def getClassDetail(token:str, identity:int, organizationId:int, teamId:int=3) -> json:
    """获取班级/单位个人详情
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    :param: token: 登录令牌
    :param: identity: 身份( 1000401|学生 1000402|教职工 1000403|职工 1000404|居民 1000405|其他人员 )
    :param: organizationId: 班号
    :param: teamId: ( 默认为3 )
    :return: information: 学生信息
    """
    date = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    totleUlr = f"http://hmgr.sec.lit.edu.cn/wms/healthyReportCount?teamId={teamId}&identity={identity}&organizationIds={organizationId}&createTime={date}"
    if not isinstance(token, str):
        try:
            token = str(token)
        except Exception:
            raise Exception("The token must be String or can be transformed to String.")
    headers = {
        'token': token,
        'Host': "hmgr.sec.lit.edu.cn",
        'Referer': "http://hmgr.sec.lit.edu.cn/web/",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    }
    try:
        response = requests.get(url=totleUlr, headers=headers, timeout=2)
    except requests.exceptions.ConnectionError:
        raise Exception("Please check your network.")
    except Exception as e:
        print(e)
    else:
        if response.json()['data']['recordTotal'] == 0:
            raise Exception("This class is not exist.")
        else:
            pages = response.json()['data']['recordTotal'] // 10
            if not response.json()['data']['recordTotal'] % 10 == 0:
                pages += 1
            for page in range(1, pages + 1):
                detailUrl = f"http://hmgr.sec.lit.edu.cn/wms/healthyRecord/page?pageNum={page}&pageSize=10&teamId=3&createTime={date}&identity={identity}&organizationIds={organizationId}&recordStatus=0&inTeamCity="
                try:
                    response = requests.get(url=detailUrl, headers=headers, timeout=2)
                except requests.exceptions.ConnectionError:
                    raise Exception("Please check your network.")
                except Exception as e:
                    print(e)
                else:
                    if response.json()['code'] == 4003:
                        raise Exception("The user of the token you gave has no power to do this.")
                    for each in response.json()['data']['list']:
                        information = {
                            "userId": each['userId'],
                            "name": each["name"],
                            "mobile": each["mobile"],
                            "teamNo": each["teamNo"],
                            "organizationName": each["organizationName"],
                            "college": each["college"],
                            "instructorName": each["instructorName"]
                        }
                        yield information