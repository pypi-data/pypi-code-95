import os
import sys
import logging
import numpy as np
import struct
import base64
import re
from typing import Any, Dict, List, Text
from bmlx.flow import Executor, Artifact
from bmlx_components.proto import schema_pb2, model_pb2
from bmlx.utils import import_utils, artifact_utils, io_utils
from xdl.python.proto import trace_pb2

SHARE_SLOTS = "shared_slots"
ITEM_SLOTS = "item_slots"
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


class ConverterExecutor(Executor):
    def parse_column(self, key, col):
        val_t = np.frombuffer(col.data, dtype=trace2nptype(col.dtype)).reshape(
            col.shape
        )
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

    def list_not_all_zero(self, list_judge: List[float]):
        for i in list_judge:
            if i > 1e-6 or i < -1e-6:
                return True
        return False

    def judge_same(self, list_a, list_b):
        if list_a is None and list_b is None:
            return True
        if list_a is None or list_b is None:
            return False
        if len(list_a) != len(list_b):
            return False
        for i in range(len(list_a)):
            if list_a[i] != list_b[i]:
                return False
        return True

    def statistic_list_ele(self, list_todo: List[List[float]]):
        cnt = []
        res = []
        for list_i in list_todo:
            exist = False
            for i in range(len(res)):
                if self.judge_same(list_i, res[i]):
                    cnt[i] += 1
                    exist = True
                    break
            if not exist:
                res.append(list_i)
                cnt.append(1)
        temp = {}
        for i in range(len(res)):
            temp[cnt[i]] = res[i]
        ret = sorted(temp.items(), key=lambda x:x[0], reverse=True)
        return ret

    def parse_trace(self, trace_content, shared_slots, item_slots, ori_model_samples):
        content_len = len(trace_content)
        sz = struct.unpack("<I", trace_content[:4])[0]
        buf = trace_content[4 : 4 + sz]
        hdrs = trace_pb2.Header()
        hdrs.ParseFromString(buf)
        logging.info("[hdrs key]%s", "|".join(hdrs.key))
        logging.info("[headers]%s", hdrs)

        logging.info("shared slots: %s", shared_slots)
        logging.info("item slots: %s", item_slots)

        readed = 4 + sz
        records = {}
        count = 0
        total_disp_id_list = []
        total_vid_list = []
        total_y_pred_list = []
        total_shared_records_list = {}
        total_item_records_list = {} # {slot_num: [value, ...], ...}
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

            for key, col in dict(zip(hdrs.key, record.column)).items():
                key = str(key)
                val = self.parse_column(key, col)
                logging.info("[%s val]%s", key, val)

                if key == "sampleid":
                    for val_i in val:
                        if "disp_id" not in val_i:
                            continue
                        dispatch_id = str(val_i["disp_id"])
                        par = re.match(INTEGER, val_i["vid"])
                        if par is not None and par.group(0) != '':
                            vid = par.group(0)
                        total_disp_id_list.append(dispatch_id)
                        total_vid_list.append(vid)
                elif key == "y_pred":
                    total_y_pred_list.extend(val)
                    logging.info("[y_pred]%s", val)
                elif key.isnumeric():
                    slot_str = key
                    slot = int(slot_str)
                    if slot in shared_slots:
                        if slot_str not in total_shared_records_list:
                            total_shared_records_list[slot_str] = []
                        for val_i in val:
                            total_shared_records_list[slot_str].append(
                                val_i
                            )
                    elif slot in item_slots:
                        if slot_str not in total_item_records_list:
                            total_item_records_list[slot_str] = []
                        for val_i in val:
                            total_item_records_list[slot_str].append(
                                val_i
                            )
            count += 1
        logging.info("[trace_content count] %s", count)

        shared_slots_disp_value = {} # {slot_num: {disp_id: [value, ...], ...}, ...}
        item_slots_keys = [] # [{keys_set}, ...]
        item_slots_values = [] # [[value, ...], ...]
        item_records_to_keys_map = {} # {slot_num: [keys_idx, ...], ...}
        model_sample_dict = dict(ori_model_samples)

        disp_id_list_len = len(total_disp_id_list)
        logging.info("[disp_id_list_len] %s", disp_id_list_len)
        assert disp_id_list_len == len(total_vid_list)
        # 长度统一
        for slot_i in total_shared_records_list:
            total_shared_records_list[slot_i] = total_shared_records_list[slot_i][:disp_id_list_len]
            shared_slots_disp_value[slot_i] = {}
        for slot_i in total_item_records_list:
            total_item_records_list[slot_i] = total_item_records_list[slot_i][:disp_id_list_len]
            item_records_to_keys_map[slot_i] = []
        total_y_pred_list = total_y_pred_list[:disp_id_list_len]

        handle_key = lambda x: str(x.hash_key)
        # 统一处理slot和y_pred, 前处理
        for i in range(disp_id_list_len):
            disp_id = total_disp_id_list[i]
            vid = total_vid_list[i]
            model_sample = model_sample_dict[disp_id]

            if disp_id not in records:
                records[disp_id] = {
                    SHARE_SLOTS: {}
                }

            for slot_i in total_shared_records_list:
                if disp_id not in shared_slots_disp_value[slot_i]:
                    shared_slots_disp_value[slot_i][disp_id] = []
                shared_slots_disp_value[slot_i][disp_id].append(total_shared_records_list[slot_i][i])
            for k in model_sample.item_feature:
                if str(k.item_id) == vid:
                    for slot_i in total_item_records_list:
                        found = False
                        for sparse_k in k.sparse:
                            if str(sparse_k.slot) == slot_i:
                                found = True
                                keys = set(map(handle_key, sparse_k.feature))
                                value = total_item_records_list[slot_i][i]
                                if keys in item_slots_keys:
                                    idx = item_slots_keys.index(keys)
                                    item_slots_values[idx].append(value)
                                else:
                                    item_slots_keys.append(keys)
                                    item_slots_values.append([value])
                                    idx = len(item_slots_values) - 1
                                item_records_to_keys_map[slot_i].append(idx)
                                break
                        if not found:
                            item_records_to_keys_map[slot_i].append(-1)
                    break
        for slot_i in item_records_to_keys_map:
            len_i = len(item_records_to_keys_map[slot_i])
            if len_i != disp_id_list_len:
                logging.error("[item_records_to_keys_map][%s]len: %s", slot_i, len_i)

        # 修改shared_slots
        logging.info("[shared_slots_disp_value]")
        trick_shared_slots_disp_value = {}
        for slot_num in shared_slots_disp_value:
            trick_shared_slots_disp_value[slot_num] = {}
            logging.info("slot_num %s:", slot_num)
            for disp_id_i in shared_slots_disp_value[slot_num]:
                reorder = self.statistic_list_ele(shared_slots_disp_value[slot_num][disp_id_i])
                logging.info("disp_id:%s, ", disp_id_i)
                for pair in reorder:
                    logging.info("cnt[%s]-%s", pair[0], pair[1])
                trick_shared_slots_disp_value[slot_num][disp_id_i] = reorder[0][1]

        for i in range(len(total_disp_id_list)):
            temp_dict = {}
            for key_i in total_shared_records_list:
                value = {
                    "emb_slot": key_i,
                    "pooling_weights": trick_shared_slots_disp_value[key_i][total_disp_id_list[i]]
                }
                temp_dict[key_i] = value
            records[total_disp_id_list[i]][SHARE_SLOTS] = temp_dict
            logging.debug("[SHARE_SLOTS]%s", total_disp_id_list[i])
            for k in temp_dict:
                logging.debug("%s_%s", k, temp_dict[k])

        # 修改item_slots
        logging.info("[item_slots_key_value]")
        trick_item_slots_values = []
        for i in range(len(item_slots_values)):
            reorder = self.statistic_list_ele(item_slots_values[i])
            logging.info("item_slots_idx: %s", i)
            for pair in reorder:
                logging.info("cnt[%s]-%s", pair[0], pair[1])
            trick_item_slots_values.append(reorder[0][1])        

        # 统一处理slot和y_pred
        value_dim = len(trick_item_slots_values[0])
        empty_value = [0.0 for x in range(value_dim)]
        for i in range(disp_id_list_len):
            disp_id = total_disp_id_list[i]
            vid = total_vid_list[i]
            model_sample = model_sample_dict[disp_id]

            item_records = {ITEM_SLOTS: {}}
            item_records["y_pred"] = total_y_pred_list[i]

            for slot_i in total_item_records_list:
                idx = item_records_to_keys_map[slot_i][i]
                value = {
                    "emb_slot": slot_i,
                    "pooling_weights": trick_item_slots_values[idx] if idx != -1 else empty_value
                }
                item_records[ITEM_SLOTS][slot_i] = [value]
            records[disp_id][vid] = item_records

        logging.debug("[parse_trace record]")
        cnt = 0
        for disp_id in records:
            logging.debug(f"[{cnt}]{disp_id}")
            for key_i in records[disp_id]:
                if key_i == SHARE_SLOTS:
                    for slot_i in records[disp_id][key_i]:
                        logging.debug(f"[shared][{slot_i}]{records[disp_id][key_i][slot_i]}")
                else:
                    logging.debug(f"[{key_i}]{records[disp_id][key_i]}")
            cnt += 1
        return records

    def parse_model_sample(self, sample_str):
        sys.path.insert(
            0, os.path.join(os.path.dirname(__file__), "../mlplat-protos")
        )
        from mlplat.feature.sample_pb2 import Sample
        import zlib

        buf = zlib.decompress(sample_str, zlib.MAX_WBITS | 16)
        buf_size = len(buf)

        readed = 0
        model_samples = []
        shared_slots = []
        item_slots = []
        while readed < buf_size:
            len_str = buf[readed : readed + 8]
            if not len_str:
                break
            record = Sample()
            lens = struct.unpack("<Q", len_str)[0]
            readed += 12
            record.ParseFromString(buf[readed : readed + lens])
            readed = readed + lens + 4
            logging.info("[record.user_debug_str len]%s", len(record.user_debug_str))
            logging.info("[record.item_debug_str len]%s", len(record.item_debug_str))
            # 如果user_debug_str为空，再去share_map中
            if len(record.user_debug_str) >= 4:
                user_info = record.user_debug_str
                user_info_dct = getDct(user_info)
                dispatch_id = str(user_info_dct["disp_id"])
            else:
                user_info_dct = record.shared_map.feature
                dispatch_id = user_info_dct["disp_id"].bytes.decode()

            for sparse_fea in record.model_sample.shared_feature.sparse:
                shared_slots.append(sparse_fea.slot)
            for i in range(len(record.model_sample.item_feature)):
                for sparse_fea in record.model_sample.item_feature[i].sparse:
                    item_slots.append(sparse_fea.slot)

            model_samples.append((dispatch_id, record.model_sample))
        return model_samples, list(set(shared_slots)), list(set(item_slots))

    def gen_model_sample_and_scores(self, ori_model_samples, trace_records):
        sys.path.insert(
            0, os.path.join(os.path.dirname(__file__), "../mlplat-protos")
        )
        from mlplat.feature.score_pb2 import SampleScore
        model_samples_list = []
        scores_list = []

        for (dispatch_id, sample) in ori_model_samples:
            if dispatch_id not in trace_records:
                print("dispatch_id %s not found in trace info." % dispatch_id)
                continue
            trace_record = trace_records[dispatch_id]

            # shared feature
            single_shared = trace_record[SHARE_SLOTS]
            trace_shared_slots = single_shared.keys()
            shared_slots = []
            for sparse in sample.shared_feature.sparse:
                slot = str(sparse.slot)

                if slot not in single_shared:
                    continue
                shared_slots.append(slot)

                single_slot = single_shared[slot]
                logging.info("[single_slot]%s", single_slot)
                emb = sparse.embedding.add()
                emb.emb_slot = int(single_slot["emb_slot"])
                for weight in single_slot["pooling_weights"]:
                    emb.pooling_weight.append(weight)

            if len(shared_slots) < len(trace_shared_slots):
                print(
                    "dispatch_id ",
                    dispatch_id,
                    " shared slots: ",
                    list(set(trace_shared_slots).difference(set(shared_slots))),
                    "not found in model sample.",
                )

            # iterator feature and score
            sample_score = SampleScore()
            for item in sample.item_feature:
                vid = str(item.item_id)
                if vid not in trace_record:
                    print(
                        "vid %s not found in trace info, dispatch id %s."
                        % (vid, dispatch_id)
                    )
                    continue

                item_score = trace_record[vid]["y_pred"]
                score = sample_score.score.add()
                score.item_id = item.item_id
                for s in item_score:
                    score.value.append(s)

                single_record = trace_record[vid][ITEM_SLOTS]
                trace_iterator_slots = single_record.keys()
                iterator_slots = []
                for sparse in item.sparse:
                    slot = str(sparse.slot)
                    if slot not in single_record:
                        continue
                    iterator_slots.append(slot)
                    single_slot = single_record[slot]
                    for info in single_slot:
                        emb = sparse.embedding.add()
                        emb.emb_slot = int(info["emb_slot"])
                        for weight in info["pooling_weights"]:
                            emb.pooling_weight.append(weight)
                if len(iterator_slots) < len(trace_iterator_slots):
                    print(
                        "dispatch_id ",
                        dispatch_id,
                        " vid: ",
                        vid,
                        " slots: ",
                        list(
                            set(trace_iterator_slots).difference(
                                set(iterator_slots)
                            )
                        ),
                        "not found in model sample.",
                    )

            model_samples_list.append(
                base64.b64encode(sample.SerializeToString()).decode()
            )
            scores_list.append(
                base64.b64encode(sample_score.SerializeToString()).decode()
            )

        return "\n".join(model_samples_list), "\n".join(scores_list)

    def convert(self, sample, predict_trace):
        ori_model_samples, shared_slots, item_slots = self.parse_model_sample(sample)
        trace_records = self.parse_trace(predict_trace, shared_slots, item_slots, ori_model_samples)
        return self.gen_model_sample_and_scores(ori_model_samples, trace_records)
        

    def execute(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        assert len(input_dict["validate_origin_sample"]) == 1
        assert len(input_dict["validate_sample"]) == 1
        assert len(input_dict["predict_trace"]) == 1

        validate_origin_sample_path = input_dict[
            "validate_origin_sample"
        ][0].meta.uri.rstrip('/')
        validate_origin_sample_file_path = os.path.join(
            validate_origin_sample_path, "origin_samples.txt"
        )

        validate_sample_file_path = input_dict[
            "validate_sample"
        ][0].meta.uri.rstrip('/')
        validate_sample_path = "/".join(
            validate_sample_file_path.split('/')[:-1]
        )

        predict_trace_path = input_dict[
            "predict_trace"
        ][0].meta.uri.rstrip('/')
        predict_trace_file_path = os.path.join(
            predict_trace_path, "test.predict.trace.0.1"
        )

        # validate_sample的path应为"xxxxxxx/exp_xx/run_xx/processed_samples.gz",
        # 在此路径下新建目录validate_sample为转换后输出存放地址
        output_root_path = os.path.join(
            validate_sample_path.rstrip('/'), "validate_sample"
        )
        original_samples_path, model_sample_path, sample_score_path = list(
            os.path.join(
                output_root_path,
                [
                    "original_samples",
                    "model_samples",
                    "sample_scores"
                ][i]
            )
            for i in range(3)
        )

        if not io_utils.exists(output_root_path):
            io_utils.mkdirs(output_root_path)

        model_sample, sample_score = self.convert(
            io_utils.read_file_string(validate_sample_file_path),
            io_utils.read_file_string(predict_trace_file_path)
        )

        # output存hdfs上，在此改写
        output_dict["converted_samples"][0].meta.uri = output_root_path

        io_utils.write_string_file(
            original_samples_path,
            io_utils.read_file_string(validate_origin_sample_file_path)
        )

        io_utils.write_string_file(
            model_sample_path,
            model_sample.encode()
        )

        io_utils.write_string_file(
            sample_score_path,
            sample_score.encode()
        )
        