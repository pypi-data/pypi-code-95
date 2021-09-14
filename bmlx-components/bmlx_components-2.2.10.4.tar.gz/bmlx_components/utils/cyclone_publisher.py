import requests
import json
import logging
import sys
import time

# 线上
HK_CYCLONE_GET_MASTER_URL_ONLINE = (
    "http://169.136.88.180:6210/CycloneMetaService/GetMasterInfo"
)
# 测试
HK_CYCLONE_GET_MASTER_URL_TEST = (
    "http://164.90.76.189:6210/CycloneMetaService/GetMasterInfo"
)
SG_CYCLONE_GET_MASTER_URL = (
    "http://169.136.190.98:6210/CycloneMetaService/GetMasterInfo"
)
EU_CYCLONE_GET_MASTER_URL = (
    "http://169.197.106.120:6210/CycloneMetaService/GetMasterInfo"
)
CYCLONE_PUBLISH_MODEL_URI = "http://{}:6210/CycloneMetaService/PublishModel"
CYCLONE_GET_MODEL_INFO_URI = (
    "http://{}:6210/CycloneMetaService/GetModelDeployInfo"
)


class CycloneOptions(object):
    __slots__ = [
        "model_name",
        "model_version",
        "model_class",
        "mask",
        "dup_cnt",
    ]

    def __init__(
        self,
        model_name,
        model_version,
        model_class="EmbeddingZmapModel",
        mask=65535,
        dup_cnt=3,
    ):
        self.model_name = model_name
        self.model_version = model_version
        self.model_class = model_class
        self.mask = mask
        self.dup_cnt = dup_cnt


def get_cyclone_master(is_eu=False, try_limit=3):
    if is_eu:
        url = EU_CYCLONE_GET_MASTER_URL
    else:
        url = SG_CYCLONE_GET_MASTER_URL

    def convert_netaddr(x):
        return ".".join([str(x // (256 ** i) % 256) for i in range(0, 4)])

    ret = None
    for i in range(try_limit):
        r = requests.get(url, headers={"content-type": "application/json"})
        if r.status_code != 200 or r.json().get("status") != "OK":
            logging.info(
                "get_cyclone_master, retry %d, status: %s, response: %s"
                % (i + 1),
                r.status_code,
                r.text,
            )
            time.sleep(0.1)
            continue
        ret = convert_netaddr(r.json().get("master_ip"))
        break
    return ret


def publish_model_to_cyclone(
    options, shards, is_eu=False, is_sg=True, try_limit=3
):
    def _do_publish(dest, f_eu):
        master_ip = get_cyclone_master(f_eu, try_limit)
        if not master_ip:
            logging.error(
                "[%s]Failed to get ip of cyclone meta master", dest
            )
            return False
        logging.info("[publish %s ip]%s", dest, master_ip)

        for try_cnt in range(try_limit):
            resp = requests.get(
                CYCLONE_PUBLISH_MODEL_URI.format(master_ip),
                headers={"content-type": "application/json"},
                data=json.dumps(body),
            )
            logging.info(
                "[%s]publish to cyclone, resp: %s", dest, resp.content
            )
            if resp.status_code == 200 and resp.json().get("status") == "OK":
                return True
            time.sleep(1)
        logging.error(
            "[%s]Failed to publish model to cyclone, cyclone master ip: %s, resp: %s, cyclone options: %s, shards: %s",
            dest,
            master_ip,
            resp.content,
            options,
            shards,
        )
        return False

    if (not is_eu) and (not is_sg):
        logging.error("no model to publish!")
        return False

    basic_info = {
        "dup_count": options.dup_cnt,
        "publish_time": options.model_version,
        "name": options.model_name,
        "class_name": options.model_class,
        "mask": options.mask,
        "version": str(options.model_version),
    }

    body = {"basic_info": basic_info, "shards": shards}
    logging.info("prepare publish model to cyclone, request: %s", body)

    ret_sg = True
    ret_eu = True
    if is_sg:
        ret_sg = _do_publish("sg", False)
    if is_eu:
        ret_eu = _do_publish("eu", True)
    return ret_sg and ret_eu

def poll_cyclone_model_info(
    model_name,
    model_version,
    timeout_s=3600,
    is_eu=False,
    is_sg=True,
    try_limit=3
):
    def _do_poll(dest, master_ip):
        resp = requests.get(
            CYCLONE_GET_MODEL_INFO_URI.format(master_ip),
            headers={"content-type": "application/json"},
            data=json_body,
        )
        logging.info(
            "[%s]polling cyclone model, resp_status: %s",
            dest,
            resp.json()["status"]
        )
        r = resp.json()
        if resp.status_code == 200 and r["status"] == "OK":
            r_version = r["model_info"]["basic_info"]["version"]
            if r_version == str(model_version):
                logging.info(
                    "[%s]Poll cyclone model info successfully, resp: %s",
                    dest, resp.content
                )
                return True
            else:
                logging.info(
                    "[%s]Poll cyclone model info wrong, resp_veriosn: %s",
                    dest, r_version
                )
        return False

    if (not is_eu) and (not is_sg):
        logging.error("no model to poll!")
        return False

    cur_ts = int(time.time())
    json_body = json.dumps(
        {"model_name": model_name, "model_version": str(model_version)}
    )
    logging.info(
        "[Poll request]model_name: %s, model_version: %s",
        model_name, model_version
    )

    if is_sg:
        master_ip_sg = get_cyclone_master(False, try_limit)
        if not master_ip_sg:
            logging.error("[sg]Failed to get ip of cyclone meta master")
            return False
        logging.info("[poll sg ip]%s", master_ip_sg)
    if is_eu:
        master_ip_eu = get_cyclone_master(True, try_limit)
        if not master_ip_eu:
            logging.error("[eu]Failed to get ip of cyclone meta master")
            return False
        logging.info("[poll eu ip]%s", master_ip_eu)

    eu_ok = False if is_eu else True
    sg_ok = False if is_sg else True
    while int(time.time()) < cur_ts + timeout_s:
        if is_sg and not sg_ok:
            sg_ok = _do_poll("sg", master_ip_sg)
        if is_eu and not eu_ok:
            eu_ok = _do_poll("eu", master_ip_eu)

        if sg_ok and eu_ok:
            break
        time.sleep(60)
        logging.info("waiting cyclone to finish loading model...")

    if (not sg_ok) or (not eu_ok):
        logging.error(
            "Failed to poll cyclone model info with timeout after %d seconds",
            timeout_s,
        )
    return sg_ok and eu_ok
