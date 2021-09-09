# coding:utf-8

import hashlib

__author__ = 'lee'

import uuid


def cal_sha1_string(s):
    return str(hashlib.sha1(s.encode("utf-8")).hexdigest())


def cal_md5_string(s):
    return str(hashlib.md5(s.encode("utf-8")).hexdigest())


def make_token():
    return str(uuid.uuid4()).replace("-", "")
