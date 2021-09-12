#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import os


class CommonConstant:
    # 默认语言
    DEFAULT_LANGUAGE = 'zh-CN'
    """
     媒体文件类型
     * 1-课程介绍视频
     * 2-课程视频文件
     * 3-课程音频文件
     * 4-章节视频文件
     * 5-章节音频文件
    """
    MEDIA_TYPE = {
        'COURSE_INTRODUCTION_VIDEO': 1,
        'COURSE_VIDEO_FILE': 2,
        'COURSE_AUDIO_FILE': 3,
        'LESSON_VIDEO_FILE': 4,
        'LESSON_AUDIO_FILE': 5
    }
    """
     课程、章节学习状态
     * 1-学习中
     * 2-已学完
    """
    LEARNING_STATUS = {
        'LEARNING': 1,
        'FINISHED': 2,
    }
    """
     课程提交动作
     * 0-提交审核
     * 1-提交测试
     * 2-撤销审核
    """
    COURSE_COMMIT_ACTION = {
        'COMMIT_REVIEW': 0,
        'COMMIT_TEST': 1,
        'CANCEL_COMMIT': 2
    }
    """
     期望变更到的状态值
     * 1-课程下架，课程不可推荐、搜索和售卖，但已购用户可以使用。
     * 2-课程上架，课程可推荐、搜索、售卖和使用。
     * 3-课程下架，课程不可推荐、搜索和售卖，已购用户也不可使用。
    """
    COURSE_STATUS_CHANGE = {
        'COURSE_OFFSHELF_AND_PURCHASED_USER_AVAILABLE': 1,
        'COURSE_ONSHELF': 2,
        'COURSE_OFFSHELF_AND_PURCHASED_USER_UNAVAILABLE': 3
    }
    """
     课程售卖模式
     * 0-仅支持课程售卖
     * 1-免费
     * 2-仅支持会员包售卖
     * 3-同时支持单课程售卖和会员包售卖
     * 4-只支持教育中心会员售卖
     * 5-同时支持教育中心会员售卖和单卖
     * 6-同时支持教育中心会员售卖和CP会员售卖
     * 7-同时支持教育中心会员售卖和CP会员售卖和单卖   
    """
    COURSE_SELLING_MODE = {
        'SEPARATELY': 0,
        'FREE': 1,
        'SOLD_BY_PACKAGE_ONLY': 2,
        'SOLD_SEPARATELY_AND_BY_PACKAGE': 3,
        'SOLD_BY_EDUCATION_ONLY': 4,
        'SOLD_SEPARATELY_AND_BY_EDUCATION': 5,
        'SOLD_EDUCATION_AND_BY_CP': 6,
        'SOLD_SEPARATELY_AND_BY_CP_AND_BY_EDUCATION': 7
    }
    """
     有效期单位
     * 1-无限制：此时忽略validityNum的值，课程购买后永久有效
     * 2-天
     * 3-周
     * 4-月
     * 5-年
    """
    VALIDITY_UNIT = {
        'PERMANENT': 1,
        'DAY': 2,
        'WEEK': 3,
        'MONTH': 4,
        'YEAR': 5
    }
    """
     课程类型
     * 1000-其它类型
     * 1001-直播课
     * 1002-录播课
     * 1003-教辅教材
     * 1004-绘本
    """
    COURSE_TYPE = {
        'OTHERS': 1000,
        'LIVE': 1001,
        'RECORDED': 1002,
        'TEACHING_MATERIALS': 1003,
        'DRAWING_BOOK': 1004,
    }
    """
     订购状态
     * 2-已订购
     * 4-已退订
    """
    SUBSCRIPTION_STATUS = {'SUBSCRIBED': 2, 'UNSUBSCRIBED': 4}
    """
     价格类型
     * 1-原始价格。可用在降价促销等场景展示商品原始价格；教育中心App显示原价时，将使用删除线进行标识
     * 2-售卖价格。用户购买商品时实际需要支付的价格
    """
    PRICE_TYPE = {'ORIGINAL': 1, 'CURRENT': 2}
    """
     课程或章节的媒体类型
     * 1-音频
     * 2-视频
     * 3-绘本
    """
    COURSE_LESSON_MEDIA_TYPE = {'AUDIO': 1, 'VIDEO': 2, 'DRAWING_BOOK': 3}

    CREDENTIAL_LIST = {
        'client_id': '235889897037149184',
        'client_secret': '55A5C9CA1E983328DA7E020B'
        '1A1CC4B02AEB80BFF60F648F74997670D45C7EFF',
        'grant_type': 'client_credentials'
    }

    CONFIG_DIR = 'config'
    AUTH_DIR = 'ssl'
    LOG_DIR = os.path.join('storage', 'log')

    # 文件访问类型
    FILE_MODE_READ = 'rb'
    FILE_MODE_CREATE_WRITE = 'wb+'
    FILE_MODE_CREDENTIAL_WRITE = 'w'

    # 内存访问类型
    SHMOP_MODE_CREATE = 'c'

    # 文件访问权限
    FILE_DEFAULT_MOD = 0o640

    # 目录访问权限
    DIR_DEFAULT_MOD = 0o740

    # 证书
    CERT = 'cacert.pem'
    REFRESH_TIME_BEFORE_EXPIRE = 3600

    # 返回状态
    RESULT_SUCCESS = 0

    # 获取默认证书文件
    DEFAULT_CERT_URL = 'http://curl.haxx.se/ca/cacert.pem'

    # 项目名
    PROJECT_NAME = 'edukit_sdk'

    # 根目录
    cur_path = os.path.abspath(os.path.dirname(__file__))
    ROOT_PATH = os.path.abspath(
        os.path.dirname(__file__))[:cur_path.find(PROJECT_NAME) +
                                   len(PROJECT_NAME)]
