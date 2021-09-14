import os
import sys
import base64
import zlib
import subprocess
import tempfile
import logging
import json
import time
import requests
from typing import Any, Dict, List, Text, Optional
from bmlx.utils import io_utils
from bmlx.fs import hdfs
from bmlx_components.utils.common_tools import *
from google.protobuf.json_format import MessageToJson

MODEL_NAME = ""
MODEL_VERSION = ""
START_TIMEOUT = 300
SLEEP_SEC = 180
PORT = "9999" # 暂时写死

VALIDATE_FILES_HDFS_ROOT = "hdfs://bigo-rt/user/bmlx/validate_ahead_files"

RTP_BIN                = "mlplat_rtp_d"
RTP_CONF_GFLAGS        = "gflags.conf"
RTP_CONF_SERVER_SG     = "server-sg.conf"
RTP_CONF_SERVER_EU     = "server-eu.conf"
RTP_CONF_FEATURE_QUERY = "feature_query.yaml"
RTP_LIB_IOMP5          = "libiomp5.so"
RTP_LIB_MKLML          = "libmklml_intel.so"
RTP_LIB_TF             = "libtensorflow.so.1"
RTP_LIB_NV             = "libnvinfer.so.6"
RTP_LIB_NV_PLUG        = "libnvinfer_plugin.so.6"
CHECK_EXEC             = "rtp_check_tool"

def download_file(local_dir, file_name, need_chmod=False):
    remote_path = os.path.join(VALIDATE_FILES_HDFS_ROOT, file_name)
    local_path = os.path.join(local_dir, file_name)
    fs, p = io_utils.resolve_filesystem_and_path(remote_path)
    fs.download(remote_path, local_path)
    if need_chmod:
        os.system(
            'cd %s && chmod +x %s' % (local_dir, file_name)
        )

def start_rtp_service(service_path, graph_data_path, offline_data_path, which_cyclone, local_emb_remote_path):

    # 修改gflags.conf中的配置
    def modify_gflags_conf(file_name, modify_content_map):
        content = ""
        with open(file_name, "r") as file_in:
            lines = file_in.readlines()
            for line in lines:
                key = line.split('=')[0].lstrip('-')
                if key in modify_content_map:
                    new_line = f"--{key}={modify_content_map[key]}\n"
                    modify_content_map.pop(key)
                    content += new_line
                else:
                    content += line
            for key in modify_content_map:
                new_line = f"--{key}={modify_content_map[key]}\n"
                content += new_line
        logging.info("[modified gflags.conf]%s", content)
        with open(file_name, "w") as file_out:
            file_out.write(content)

    # service_path为本地起的rtp的路径
    if not os.path.exists(service_path):
        os.makedirs(service_path)

    rtp_dirs = ["bin", "conf", "lib", "model", "log"]
    rtp_dirs_path = []
    for rtp_dir in rtp_dirs:
        rtp_dir_path = os.path.join(service_path, rtp_dir)
        if not os.path.exists(rtp_dir_path):
            os.mkdir(rtp_dir_path)
        rtp_dirs_path.append(rtp_dir_path)
    logging.info("[rtp_dirs_path]%s", rtp_dirs_path)

    # download 
    download_file(rtp_dirs_path[0], RTP_BIN, True)
    download_file(rtp_dirs_path[1], RTP_CONF_GFLAGS)
    if which_cyclone == "sg":
        download_file(rtp_dirs_path[1], RTP_CONF_SERVER_SG)
        os.system('cd %s && mv %s server.conf' % (rtp_dirs_path[1], RTP_CONF_SERVER_SG))
    elif which_cyclone == "eu":
        download_file(rtp_dirs_path[1], RTP_CONF_SERVER_EU)
        os.system('cd %s && mv %s server.conf' % (rtp_dirs_path[1], RTP_CONF_SERVER_EU))
    else:
        raise RuntimeError(f"[which_cyclone]{which_cyclone} is not allowed")
    download_file(rtp_dirs_path[1], RTP_CONF_FEATURE_QUERY)
    download_file(rtp_dirs_path[2], RTP_LIB_IOMP5)
    download_file(rtp_dirs_path[2], RTP_LIB_MKLML)
    download_file(rtp_dirs_path[2], RTP_LIB_TF)
    download_file(rtp_dirs_path[2], RTP_LIB_NV)
    download_file(rtp_dirs_path[2], RTP_LIB_NV_PLUG)

    gflags_conf = os.path.join(rtp_dirs_path[1], "gflags.conf")
    model_path = os.path.join(
        rtp_dirs_path[3], MODEL_NAME, MODEL_VERSION
    )

    # 结构形如 /{tempdir}/model/{MODEL_NAME}/{MODEL_VERSION}/{fg/, graph.bin, model.json...}
    local_graph_path = os.path.join(
        model_path,
        os.path.basename(graph_data_path)
    )
    local_validate_sample_path = os.path.join(
        model_path,
        "validate_sample"
    )
    if not os.path.exists(local_graph_path):
        os.makedirs(local_graph_path)
    if not os.path.exists(local_validate_sample_path):
        os.makedirs(local_validate_sample_path)
    io_utils.download_dir(graph_data_path, local_graph_path)
    io_utils.download_dir(offline_data_path, local_validate_sample_path)
    if local_emb_remote_path:
        local_emb_local_path = os.path.join(local_graph_path, "emb")
        io_utils.download_dir(local_emb_remote_path, local_emb_local_path)

    # TODO: 其他配置
    modify_config = {
        "conf_dir": f"{rtp_dirs_path[1]}/",
        "model_dir": rtp_dirs_path[3],
        "log_dir": f"{rtp_dirs_path[4]}/",
        "rtp_disable_gpu": "true",
        "daemon_client_on": "true",
    }
    modify_gflags_conf(gflags_conf, modify_config)

    # __list__.json手动指定
    json_content = {
        "all": {
            MODEL_NAME: {
                "path": model_path,
                "version": MODEL_VERSION
            }
        }
    }
    list_json_file = os.path.join(rtp_dirs_path[3], "__list__.json")
    with open(list_json_file, "w") as file_out:
        file_out.write(
            json.dumps(json_content, indent=4, separators=(', ', ': '))
        )

    host_ip = get_host_ip()
    logging.info("[host_ip]%s", host_ip)
    logging.info("[rtp directory]")
    walk_through_dir(service_path)

    # 设置环境
    cur_env_path = os.getcwd()
    logging.info("[origin env]%s", cur_env_path)
    os.chdir(rtp_dirs_path[0])
    logging.info("[current env]%s", os.getcwd())
    os.environ["LD_LIBRARY_PATH"] = ("%s:%s" %
        (rtp_dirs_path[2], os.environ["LD_LIBRARY_PATH"])
    )
    logging.info("[LD_LIBRARY_PATH]%s", os.environ["LD_LIBRARY_PATH"])
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    logging.info("[CUDA_VISIBLE_DEVICES]%s", os.environ["CUDA_VISIBLE_DEVICES"])

    # start rtp
    start_time = time.time()
    proc = subprocess.Popen(
        ("./mlplat_rtp_d", "--flagfile=%s" % gflags_conf),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    os.chdir(cur_env_path)
    logging.info("[revert env]%s", os.getcwd())

    dur = lambda x: time.time() - x
    # check if ready
    service_url = f"http://127.0.0.1:{PORT}"
    rtp_ready = False
    while dur(start_time) < START_TIMEOUT:
        try:
            resp = requests.get(service_url)
            if resp.status_code == 200:
                logging.info("[RTP]Ready.")
                rtp_ready = True
                break
            else:
                logging.info("[RTP]Service abnormal, %s", resp.status_code)
        except Exception as e:
            logging.warning("[RTP]Not ready..., %s", e)
            time.sleep(30)
    if not rtp_ready:
        raise RuntimeError(f"[RTP]TIMEOUT {START_TIMEOUT}")

    return proc, model_path

def wind_up_rtp(process):
    if process is not None and process.poll() is None:
        try:
            process.kill()
            logging.info("[RTP]Killed")
        except:
            raise RuntimeWarning("[RTP]Kill rtp failed!")
    logging.info("[RTP]End")

def rtp_predict_cycle(original_feature, times=1):
    data = {
        "log_id": 111111,
        "model_name": MODEL_NAME,
        "source": "bmlx_validate",
        "original_feature": {}
    }
    json_ori = MessageToJson(original_feature)
    decode_json = json.loads(json_ori)
    data['original_feature'] = decode_json
    data_json = json.dumps(data)

    for i in range(times):
        r = requests.get(
            f"http://127.0.0.1:{PORT}/v1/rtp/predict",
            data=data_json
        )

def do_check(
    process,
    offline_data_path,
    service_path,
    model_path,
    accuracy,
    rate,
    need_cyclone
):
    assert process.poll() is None

    download_file(service_path, CHECK_EXEC, need_chmod=True)

    # warmup cyclone
    sys.path.insert(
        0, os.path.join(os.path.dirname(__file__), "../mlplat-protos")
    )
    from mlplat.feature.original_feature_pb2 import OriginalFeature

    original_feature_path = os.path.join(
        model_path, "validate_sample", "original_samples"
    )
    if need_cyclone:
        logging.info("[warm up cyclone] send 1000 requests")
        with open(original_feature_path, "r") as of:
            lines = of.readlines()
            for line in lines:
                if len(line) >= 4:
                    ori_feat = OriginalFeature()
                    ori_feat_zlib = base64.b64decode(line)
                    ori_feat_str = zlib.decompress(ori_feat_zlib)
                    ori_feat.ParseFromString(ori_feat_str)

                    rtp_predict_cycle(ori_feat, 1000)
                    break
        logging.info("[warm up cyclone] finish")
    else:
        logging.info("[don't need cyclone]")

    os.chdir(service_path)
    logging.info("[current env]%s", os.getcwd())

    # run check
    proc_C = subprocess.Popen(
        (
            "./rtp_check_tool",
            f"--service_name=127.0.0.1:{PORT}",
            f"--data_path={model_path}",
            f"--accuracy={accuracy}",
            f"--rate={rate}"
        ),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    ret_C = proc_C.wait()

    if ret_C != 0:
        raise Exception("Run check abnormal, ret: %s" % ret_C)

    log_file_dir = '_'.join(["log", MODEL_NAME, MODEL_VERSION])
    log_file = os.path.join(
        log_file_dir,
        "PASS"
    )

    # 上传校验结果信息
    log_remote_dir = os.path.join(
        '/'.join(offline_data_path.rstrip('/').split('/')[:-1]),
        log_file_dir
    )
    io_utils.upload_dir(log_file_dir, log_remote_dir)
    logging.info("============================================================")
    logging.info("[Validation LOG] %s", log_remote_dir)

    if os.path.exists(log_file):
        return True
    else:
        return False


def validate_ahead(
    offline_data_path: Text,
    graph_data_path: Text,
    model_name: Text,
    model_version: Text,
    accuracy: Text,
    rate: Text,
    which_cyclone: str = "sg",
    local_emb_remote_path: str = "",
    rtp_config: Optional[Dict[Text, Any]] = None
):
    global MODEL_NAME, MODEL_VERSION
    MODEL_NAME = model_name
    MODEL_VERSION = str(model_version)

    with tempfile.TemporaryDirectory() as tmpdir:
        proc, model_path = start_rtp_service(
            tmpdir, graph_data_path, offline_data_path, which_cyclone, local_emb_remote_path
        )

        res = do_check(
            proc,
            offline_data_path,
            tmpdir,
            model_path,
            accuracy,
            rate,
            False if local_emb_remote_path else True
        )

        wind_up_rtp(proc)

    return res

                