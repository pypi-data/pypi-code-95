#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
refer to https://git.sysop.bigo.sg/recsys/scripts/blob/master/platform/update_resource_k8s.py
"""
import os
import json
import re
from random import choice
import logging
import threading
import requests
from bmlx.utils import io_utils

FOLDER_PREFIX = "/data/models"
HDFS_PREFIX_DP = "hdfs://dplhcluster" + FOLDER_PREFIX
HDFS_PREFIX_JJA = "hdfs://jjalhcluster" + FOLDER_PREFIX
HDFS_PREFIX_QW = "hdfs://qwlhcluster" + FOLDER_PREFIX


TOKEN = "access_token=eyJJbmZvIjoiZXlKVmMyVnlJam9pY205aWIzUXhJaXdpUlhod2FYSmhkR2x2YmtSaGRHVWlPams1T1RZMk1qazRNamw5IiwiSG1hYyI6Ik54ajBUcEhubGo1OFIxWkxWNFRaOVh1cUJyaHRDTVd1STlRWkpoWUd3bjg9In0="

PTN_HDFS_ADDR = re.compile("^hdfs://[0-9a-zA-Z-_\.,/]+$")
PTN_STRICT_NAME = re.compile("^[0-9a-zA-Z_-]+$")


def post_meta_to_k8s(name, namespace, version, path):
    headers = {"Content-type": "application/json", "Cookie": TOKEN}
    payload = {
        "name": name,
        "path": path,
        "ns": namespace,
        "version": version,
        "type": "model",
        "size": 11010,
    }
    resp = requests.post(
        "http://ceto.recsys.bigo.inner:8888/openapi/v1/update_model",
        headers=headers,
        data=json.dumps(payload),
    )
    logging.info(
        "post meta to k8s, request header: %s, request payload: %s, resp: %s",
        headers,
        payload,
        resp.text,
    )
    if resp.status_code != requests.codes.ok:
        raise RuntimeError("Failed to post meta to k8s")
    resp_dict = json.loads(resp.content)
    if resp_dict["errno"] != "1000000":
        logging.error(
            "Failed to sync data to k8s platform, errno: %s", resp_dict["errno"]
        )
        return False
    return True


upload_failed = False


def upload_data_to_hdfs(local_dir, hdfs_base_dir):
    global upload_failed
    upload_failed = False

    def upload_to_hdfs(local_dir, remote_dir):
        global upload_failed
        logging.info("uploading dir %s to remote %s", local_dir, remote_dir)
        try:
            io_utils.upload_dir(local_dir, remote_dir)
        except Exception as e:
            logging.error(
                "Failed to upload dir %s to remote %s, exception: %s",
                local_dir,
                remote_dir,
                e,
            )
            upload_failed = True

    hdfs_base_dir = hdfs_base_dir.strip("/")
    upload_dp = threading.Thread(
        target=upload_to_hdfs,
        args=(local_dir, os.path.join(HDFS_PREFIX_DP, hdfs_base_dir)),
    )
    upload_jja = threading.Thread(
        target=upload_to_hdfs,
        args=(local_dir, os.path.join(HDFS_PREFIX_JJA, hdfs_base_dir)),
    )
    upload_qw = threading.Thread(
        target=upload_to_hdfs,
        args=(local_dir, os.path.join(HDFS_PREFIX_QW, hdfs_base_dir)),
    )
    upload_dp.start()
    upload_jja.start()
    upload_qw.start()

    upload_dp.join()
    upload_jja.join()
    upload_qw.join()

    if upload_failed:
        logging.info(
            "Failed to upload data %s to hdfs %s", local_dir, hdfs_base_dir
        )
        return False
    else:
        logging.info(
            "Finished upload data %s to hdfs %s", local_dir, hdfs_base_dir
        )
        return True


def upload_and_sync(ns, local_dir, name, version):
    hdfs_base_dir = "/%s/%s/%d" % (ns, name, version)
    """
    upload data to localhdfs
    """
    if not local_dir:
        logging.error("Invalid local src %s", local_dir)
        return False

    if not os.path.isdir(local_dir):
        logging.error("local_dir should be directory")
        return False
    if not os.listdir(local_dir):
        logging.error("local_dir have no files")
        return False

    # upload to hdfs
    if not upload_data_to_hdfs(local_dir, hdfs_base_dir):
        return False

    # sync meta to k8s
    path = "%s/%s/%s/%d" % (FOLDER_PREFIX, ns, name, version)
    return post_meta_to_k8s(name, ns, version, path)
