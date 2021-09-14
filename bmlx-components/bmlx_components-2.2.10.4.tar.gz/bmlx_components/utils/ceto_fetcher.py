import requests
import json
import logging

TOKEN = "access_token=eyJJbmZvIjoiZXlKVmMyVnlJam9pY205aWIzUXhJaXdpUlhod2FYSmhkR2x2YmtSaGRHVWlPams1T1RZMk1qazRNamw5IiwiSG1hYyI6Ik54ajBUcEhubGo1OFIxWkxWNFRaOVh1cUJyaHRDTVd1STlRWkpoWUd3bjg9In0="
SG_CETO_FETCH_MODEL_URL = (
    "http://sg.ceto.recsys.bigo.inner:8888/api/v1/mlplat/datas"
)

def fetch_model_from_ceto(name, namespace):
    headers = {"Cookie": TOKEN}
    params = {
        "name": name,
        "namespace": namespace,
        "page_size": 100, # 返回最多100条
    }
    resp = requests.get(
        SG_CETO_FETCH_MODEL_URL,
        headers=headers,
        params=params,
    )
    logging.debug(
        "fetch model info from k8s, request header: %s, request params: %s, resp: %s",
        headers,
        params,
        resp.text,
    )
    if resp.status_code != requests.codes.ok:
        raise RuntimeError("Failed to fetch model info from k8s")
    resp_dict = json.loads(resp.content)
    if resp_dict["errno"] != "1000000":
        raise RuntimeError(
            "Failed to fetch model info from k8s platform, errno: %s", resp_dict["errno"]
        )
    return resp_dict['data']
