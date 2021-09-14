import logging
import os
import struct
import math
import tempfile
import base64
import sys
import zlib
import re
from typing import Dict, Text, List, Any
from bmlx.flow import Executor, Artifact
from bmlx.utils import artifact_utils, io_utils
from xdl.python.proto import trace_pb2
import numpy as np

INTEGER = '([0-9]*)'

def trace2nptype(tp):
    if tp == trace_pb2.Int8:
        return np.int8
    elif tp == trace_pb2.Int16:
        return np.int16
    elif tp == trace_pb2.Int32:
        return np.int32
    elif tp == trace_pb2.Int64:
        return np.int64
    elif tp == trace_pb2.Float:
        return np.float32
    elif tp == trace_pb2.Double:
        return np.float64
    elif tp == trace_pb2.Bool:
        return np.bool
    elif tp == trace_pb2.Byte:
        return np.byte
    else:
        raise RuntimeError("unknown trace data type: {}".format(tp))


def getDct(infostr):
    dct = {}
    for iter_str in infostr.split("#"):
        if len(iter_str) == 0:
            continue
        fd_pos = iter_str.find(":")
        if fd_pos == -1:
            continue
        key = iter_str[:fd_pos]
        val = iter_str[fd_pos + 1 :]
        dct[key] = val
    return dct


class ScoreComparerExecutor(Executor):
    def download_to_local(self, remote_path, local_dir):
        fs, path = io_utils.resolve_filesystem_and_path(remote_path)
        local_path = os.path.join(local_dir, os.path.basename(remote_path))
        fs.download(
            remote_path, local_path,
        )
        return local_path

    def parse_featurelog_line(self, line, online_score_location):
        try:
            compressed_bytes = base64.b64decode(line)
        except Exception as e:
            logging.error(
                "Failed to decode base64 featurelog, exception: %d", e
            )
            return None

        origin_bytes = zlib.decompress(compressed_bytes)

        sys.path.insert(
            0, os.path.join(os.path.dirname(__file__), "../mlplat-protos")
        )
        from mlplat.feature import original_feature_pb2

        origin_feature = original_feature_pb2.OriginalFeature()
        origin_feature.ParseFromString(origin_bytes)

        ret = {}
        dispatcher_id = origin_feature.scenario.feature[
            "dispatcher_id"
        ].bytes.decode()
        if online_score_location not in origin_feature.items.items_online.feature_list:
            raise RuntimeError("%s is not found" % online_score_location)
        for (vid, s_list) in zip(
            origin_feature.items.item_ids,
            origin_feature.items.items_online.feature_list[
                online_score_location
            ].feature,
        ):
            multi_score_list = s_list.float_list.value
            if len(multi_score_list) == 0:
                continue
            ret[f"{dispatcher_id}_{vid}"] = multi_score_list

        return ret

    def parse_online_scores(self, path, online_score_location):
        ret = {}
        with open(path, "r") as f:
            for line in f.readlines():
                ret.update(self.parse_featurelog_line(
                    line,
                    online_score_location
                ))
        return ret

    def getDct(self, infostr):
        dct = {}
        for iter_str in infostr.split("#"):
            if len(iter_str) == 0:
                continue
            fd_pos = iter_str.find(":")
            if fd_pos == -1:
                continue
            key = iter_str[:fd_pos]
            val = iter_str[fd_pos + 1 :]
            dct[key] = val
        return dct

    def parse_column(self, key, col):
        val_t = np.frombuffer(col.data, dtype=trace2nptype(col.dtype)).reshape(
            col.shape
        )
        logging.info("[len val_t]%s", len(val_t))
        res = []
        if key == "sampleid":
            for val_i in val_t:
                val = getDct("".join(chr(v) for v in val_i))
                res.append(val)
        else:
            for val_i in val_t:
                val = list(val_i)
                res.append(val)

        return res

    def parse_offline_scores(self, path):
        with open(path, "rb") as f:
            trace_content = f.read()
            content_len = len(trace_content)
            logging.debug("content_len: %s", content_len)
            sz = struct.unpack("<I", trace_content[:4])[0]
            buf = trace_content[4 : 4 + sz]
            hdrs = trace_pb2.Header()
            hdrs.ParseFromString(buf)
            logging.info("[hdrs]%s", hdrs)

            readed = 4 + sz
            ret = {}
            while readed < content_len:
                buf = trace_content[readed : readed + 4]
                if not buf:
                    break
                readed += 4
                sz = struct.unpack("<I", buf)[0]
                buf = trace_content[readed : readed + sz]
                record = trace_pb2.Record()
                record.ParseFromString(buf)
                readed += sz

                dispatch_id = None
                vid = None
                y_pred = None
                for key, col in dict(zip(hdrs.key, record.column)).items():
                    key = str(key)
                    val = self.parse_column(key, col)
                    logging.info("[key]%s", key)
                    if key == "sampleid":
                        dispatch_id_list = []
                        vid_list = []
                        for val_i in val:
                            if "disp_id" not in val_i:
                                continue
                            dispatch_id = str(val_i["disp_id"])
                            par = re.match(INTEGER, val_i["vid"])
                            if par is not None and par.group(0) != '':
                                vid = par.group(0)
                            dispatch_id_list.append(dispatch_id)
                            vid_list.append(vid)
                    elif key == "y_pred":
                        y_pred_list = val
                d_list_len = len(dispatch_id_list)
                v_list_len = len(vid_list)
                y_list_len = len(y_pred_list)
                logging.info("[len of dispatch_id_list]%s", d_list_len)
                logging.info("[len of vid_list]%s", v_list_len)
                logging.info("[len of y_pred_list]%s", y_list_len)
                assert d_list_len == v_list_len

                for i in range(d_list_len):
                    ret[f"{dispatch_id_list[i]}_{vid_list[i]}"] = [
                        float(v) for v in y_pred_list[i]
                    ]
            return ret

    def compare_scores(self, online_score, offline_score):
        diff_nums = [0, 0, 0, 0]
        anum = 0
        top_que = []
        for k, v in online_score.items():
            logging.debug("<<dispid_vid: %s---------------", k)
            if k in offline_score:
                logging.debug("[online]  dim: %s, score: %s",
                    len(v), v
                )
                logging.debug("[offline] dim: %s, score: %s",
                    len(offline_score[k]), offline_score[k]
                )
                if len(v) != len(offline_score[k]) or len(v) == 0:
                    logging.info(
                        "[warn]online_score dim and offline_score dim is not equal: %s != %s",
                        len(v), len(offline_score[k])
                    )
                    continue

                res_list = []
                diff = math.fabs(v[0] - offline_score[k][0])
                if diff < 0.00001:
                    diff_nums[3] += 1
                elif diff < 0.0001:
                    diff_nums[2] += 1
                elif diff < 0.001:
                    diff_nums[1] += 1
                elif diff < 0.01:
                    diff_nums[0] += 1
                for idx in range(len(v)):
                    delta = v[idx] - offline_score[k][idx]
                    res_list.append(
                        "{}:{}:{}".format(v[idx], offline_score[k][idx], delta)
                    )
                top_que.append((diff, k, v[0], offline_score[k][0]))
                anum += 1
            else:
                logging.debug("[dispid_vid not in offline]")
            logging.debug(">>")

        assert anum > 0, "anum = 0!!!"

        logging.info("top100 diff:%s", sorted(top_que, key=lambda x: x[0], reverse=True)[:100])
        anum = float(anum)
        other_num = anum - sum(diff_nums)
        msg = "score diff [>=0.01,<0.01,<0.001,<0.0001,<0.00001]: {:.2f}%,{:.2f}%,{:.2f}%,{:.2f}%,{:.2f}%".format(
            100 * other_num / anum,
            100 * diff_nums[0] / anum,
            100 * diff_nums[1] / anum,
            100 * diff_nums[2] / anum,
            100 * diff_nums[3] / anum,
        )
        logging.info(msg)

    def execute(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        self._log_startup(input_dict, output_dict, exec_properties)
        assert len(input_dict["origin_samples"]) == 1
        assert len(input_dict["predict_result"]) == 1
        online_score_location = exec_properties.get(
            "online_score_location",
            "rank_judgements_score"
        )
        logging.info("[online_score_location](%s)", online_score_location)
        detail = exec_properties.get(
            "detail", False
        )
        logging.info("[detail](%s)", detail)
        if detail:
            logging.getLogger().setLevel(logging.DEBUG)

        with tempfile.TemporaryDirectory() as tempdir:
            online_scores = self.parse_online_scores(
                self.download_to_local(
                    os.path.join(
                        input_dict["origin_samples"][0].meta.uri,
                        "origin_samples.txt",
                    ),
                    tempdir,
                ),
                online_score_location
            )
            logging.debug("##### online scores: %s", online_scores)

            offline_scores = self.parse_offline_scores(
                self.download_to_local(
                    os.path.join(
                        input_dict["predict_result"][0].meta.uri,
                        "test.predict.trace.0.1",
                    ),
                    tempdir,
                )
            )
            logging.debug("##### offline scores: %s", offline_scores)
            self.compare_scores(online_scores, offline_scores)
