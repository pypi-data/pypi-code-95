"""
copied from https://git.sysop.bigo.sg/xulei/brec_build_service/blob/master/pub_tools_v1/cannon/cannon_publisher_v1.py
with little modification
"""
import os
import sys
import requests
import json
import threading
import time
import random
import logging
from typing import Text, Optional
from datetime import datetime

DEFAULT_JOB_URL = "http://43.224.67.124:8787/api/v1/jobs/"
DEFAULT_TASK_URL = "http://43.224.67.124:8787/api/v1/tasks/"
DEFAULT_CYCLONE_META_URL = (
    "http://164.90.76.180:6210/CycloneMetaService/GetModelDeployInfo"
)

TEST_JOB_URL = "http://164.90.76.189:8787/api/v1/jobs/"
TEST_TASK_URL = "http://164.90.76.189:8787/api/v1/tasks/"
TEST_CYCLONE_META_URL = (
    "http://103.43.87.118:6210/CycloneMetaService/GetModelDeployInfo"
)


class PublishOptions(object):
    def __init__(
        self,
        build_type: Text,
        input_path: Text,
        data_name: Text,
        version: int,
        collection: Text,
        creator: Text,
        namespace: Text,
        dim: int = 0,
        class_name: Optional[Text] = "EmbeddingModel2",
        hdfs_sync: Optional[int] = None,
        task_type: Optional[Text] = None,
        phase: Optional[Text] = None,
        other_args: Optional[Text] = None,
        srv_addr: Optional[Text] = None,
        job_url: Text = DEFAULT_JOB_URL,
        task_url: Text = DEFAULT_TASK_URL,
        meta_url: Text = DEFAULT_CYCLONE_META_URL,
        test_env: bool = False,
    ):
        self.srv_addr = srv_addr
        self.build_type = build_type
        self.input_path = input_path
        self.data_name = data_name
        self.dim = dim
        self.class_name = class_name
        self.version = version
        self.collection = collection
        self.other_args = other_args
        self.creator = creator
        self.namespace = namespace
        self.phase = phase
        self.hdfs_sync = hdfs_sync
        self.task_type = task_type
        self.job_url = job_url
        self.task_url = task_url
        self.meta_url = meta_url
        if test_env:
            self.job_url = TEST_JOB_URL
            self.task_url = TEST_TASK_URL
            self.meta_url = TEST_CYCLONE_META_URL


def merge_dict(origin_dict, additional_dict):
    for k, v in additional_dict.items():
        if k not in origin_dict:
            origin_dict[k] = v
        elif not isinstance(v, type(origin_dict[k])):
            origin_dict[k] = v
        elif isinstance(v, dict):
            merge_dict(origin_dict[k], v)
        else:
            origin_dict[k] = v


def create_job(extra_job_dict, job_url):
    ts = time.time()
    job_dict = {
        "job_id": 1,
        "type": "full",
        "name": "",
        "phase": "final",
        "namespace": "bmlx_pusher",
        "creator": "",
        "create_time": 0,
        "update_time": 0,
        "task_ids": [],
        "params": {},
    }

    job_dict["create_time"] = int(ts)
    job_dict["update_time"] = int(ts)
    merge_dict(job_dict, extra_job_dict)

    if not job_dict["creator"]:
        logging.error("Creator is none")
        return -1
    data = json.dumps(job_dict)
    headers = {"content-type": "application/json"}

    logging.info("create job, request: %s", data)
    try:
        r = requests.post(job_url, data=data, headers=headers)
        resJs = json.loads(r.text)
        if "success" not in resJs["errmsg"]:
            logging.error("Failed to create job, result: %s", r.text)
            return -1
        job_id_str = resJs["data"]["id"]
        job_id = int(job_id_str)
        return job_id
    except Exception as e:
        logging.error("Failed to create job with exception: %s", e)
        return -1


def create_task(job_id, extra_task_dict, task_url):
    task_dict = {
        "job_id": job_id,
        "type": "full",
        "id": 0,
        "name": "",
        "namespace": "likee_recall",
        "type": "full",
        "phase": "cyclone",
        "hdfs_sync": 1,
        "create_time": 0,
        "start_time": 0,
        "end_time": 0,
        "debug": "true",
        "status": "unknown",
        "params": {
            "data_type": "",
            "data_name": "",
            "input_path": "",
            "output_path": "",
            "class_name": "",
            "args": "",
            "overseas": "",
        },
    }
    merge_dict(task_dict, extra_task_dict)

    ts = time.time()
    task_dict["create_time"] = int(ts)
    headers = {"content-type": "application/json"}
    data = json.dumps(task_dict)
    logging.info("create task, request: %s", data)
    try:
        r = requests.post(task_url, data=data, headers=headers)
        logging.info("create task resp: %s", r.content)
        return 0
    except Exception as e:
        logging.error("failed to create task, exception: %s", e)
        return -1


def generate_job_and_task_dict(args: PublishOptions):
    job_dict = dict()
    task_dict = dict()
    task_dict["params"] = dict()
    if args.creator:
        job_dict["creator"] = args.creator
    if args.namespace:
        job_dict["namespace"] = args.namespace
        task_dict["namespace"] = args.namespace
    if args.build_type:
        task_dict["params"]["data_type"] = args.build_type
    if args.data_name:
        task_dict["params"]["data_name"] = args.data_name
    if args.input_path:
        task_dict["params"]["input_path"] = args.input_path
    if args.class_name:
        task_dict["params"]["class_name"] = args.class_name
    if args.version:
        task_dict["params"]["version"] = args.version
    if args.collection:
        task_dict["params"]["collection"] = args.collection
    if args.other_args:
        task_dict["params"]["args"] = args.other_args
    if args.phase:
        task_dict["phase"] = args.phase
    if args.hdfs_sync:
        task_dict["hdfs_sync"] = args.hdfs_sync
    if args.task_type:
        task_dict["type"] = args.task_type
    return job_dict, task_dict


def publish_resource(publish_options):
    job_dict, task_dict = generate_job_and_task_dict(publish_options)
    job_id = 1

    if not publish_options.srv_addr:
        job_id = create_job(job_dict, publish_options.job_url)
        logging.info("created job_id %d", job_id)

    if job_id == -1:
        return -1

    ret = create_task(job_id, task_dict, publish_options.task_url)
    logging.info("created task ret: %d", ret)
    return ret


def check_resource(publish_options):
    payload = json.dumps(
        {
            "model_name": f"{publish_options.data_name}_{publish_options.dim}",
            "model_version": f"{publish_options.version}",
        }
    )

    FAIL_LIMIT = 20
    MAX_WAIT_MINUTES = 60

    final_timestamp = int(datetime.now().timestamp()) + MAX_WAIT_MINUTES * 60

    fail_cnt = 0
    while (
        fail_cnt <= FAIL_LIMIT
        and int(datetime.now().timestamp()) <= final_timestamp
    ):
        resp = requests.post(publish_options.meta_url, data=payload)
        if resp.status_code == 200:
            json_obj = json.loads(resp.content)
            if json_obj["status"] == "OK":
                logging.info("cyclone model loaded successfully!")
                return True
            else:
                logging.info("waiting cyclone model to be loaded...")
                time.sleep(20)
        else:
            logging.error(
                "Failed to request cyclone meta, resp: %s", resp.content
            )
            fail_cnt += 1
            time.sleep(20)
    return False
