"""
 TODO: Multiple config.ini files present, causing confusion, resolve it to work even with whl packaging
"""
import configparser
import redis
import os

class TMConfig(object):
    cfg_object = configparser.ConfigParser()
    cfg_object.read(os.path.join(os.path.curdir, "config.ini"))

    redis_cfg = cfg_object['Redis']
    worker_cfg = cfg_object['Worker']
    image_cfg = cfg_object['Image']

    redis_url = redis_cfg.get('url')
    redis_channel = worker_cfg.get('redis_channel')
    docker_url = worker_cfg.get('docker_url', False)
    executor_backend = worker_cfg.get('executor')
    image_tag = image_cfg.get('full_tag')
    