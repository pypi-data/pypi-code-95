import requests
import json

DEFAULT_GUARDIAN_ENDPOINT = "http://43.224.67.124:8787/api/v1"


def get_published_latest_data(namespace, data_name):
    resp = requests.get(
        f"{DEFAULT_GUARDIAN_ENDPOINT}/datas/",
        params={"name": data_name, "min_version": -1, "namespace": namespace},
    )
    resp.raise_for_status()
    resp_obj = json.loads(resp.content)
    if not resp_obj or not resp_obj["data"]:
        raise RuntimeError("No data returned!")
    return resp_obj["data"][0]


if __name__ == "__main__":
    ret = get_published_latest_data(
        namespace="likee_rerank", data_name="server.conf.online"
    )
    print(ret)
