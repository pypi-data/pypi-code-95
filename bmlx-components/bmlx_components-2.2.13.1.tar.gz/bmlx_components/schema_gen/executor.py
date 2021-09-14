import os
import hashlib
import logging
import itertools
import yaml
import collections
from typing import Dict, Text, List, Any
from enum import Enum
from bmlx_components.proto import schema_pb2
from bmlx.flow import Executor, Artifact
from bmlx.utils import artifact_utils, io_utils


class SchemaExecutor(Executor):
    """
    schema 的正确实现方式应该是从schema中心读取schema，并且填充相关的tag，
    因为schema中心还没有建设好， 所以先从 配置文件中去生成schema
    """

    def get_slot_dim_map(self, fg_conf_path):
        # 返回按照 {slot: dim} 的 ordered_map
        slot_2_dim = dict()
        op_names = set()
        try:
            fg_conf = yaml.load(
                io_utils.read_file_string(fg_conf_path), yaml.Loader
            )
        except Exception as e:
            raise RuntimeError("Failed to load fg conf with exception %s" % e)
        last_slot = None
        for op_type in ["shared", "iterable"]:
            for op in fg_conf[op_type]:
                # name 不能重复
                assert op["name"] not in op_names
                op_names.add(op["name"])
                if "export" in op:
                    slot = op["export"]["slot"]
                    # export的时候，是按照 op 出现的顺序去export 到 feature_vector
                    # 现在的 逻辑都是直接按照slot 大小排序，这里需要保证 fg conf中 op
                    # 出现的顺序 也是按照slot 大小排序的
                    if slot not in slot_2_dim:
                        slot_2_dim[slot] = op["export"].get("range", 1)
                    else:
                        # 相同的slot必须连续
                        assert last_slot == slot
                        slot_2_dim[slot] = slot_2_dim[slot] + op["export"].get(
                            "range", 1
                        )
                    last_slot = slot
        return slot_2_dim

    def execute(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        self._log_startup(input_dict, output_dict, exec_properties)
        schema = schema_pb2.Schema()
        assert "fg_conf" in input_dict and len(input_dict["fg_conf"]) > 0
        fg_conf_path = input_dict["fg_conf"][0].meta.uri

        slot_dim_map = self.get_slot_dim_map(fg_conf_path)
        model_input_conf = yaml.load(
            io_utils.read_file_string(exec_properties["model_input_conf"]),
            yaml.Loader,
        )

        parsed_slots = set()

        for group in model_input_conf["feature_group"]:
            assert group in ("dense", "sparse", "bias", "stats", "additional")

        for group in itertools.chain(
            model_input_conf["feature_group"].get("sparse", []),
            model_input_conf["feature_group"].get("stats", []),
        ):
            for slot in group["slots"]:
                if slot in parsed_slots:
                    continue
                parsed_slots.add(slot)

                sf = schema.sparse_features.add()
                sf.name = str(slot)
                sf.qualified_name = ""

        for group in itertools.chain(
            model_input_conf["feature_group"].get("dense", []),
            model_input_conf["feature_group"].get("bias", []),
        ):
            logging.info("[group slots]%s", group["slots"])
            logging.info("[slot_dim_map key]%s", slot_dim_map.keys())
            for slot in group["slots"]:
                if slot in parsed_slots:
                    continue
                parsed_slots.add(slot)
                sf = schema.dense_features.add()
                sf.name = str(slot)
                sf.length = slot_dim_map[int(slot)]

        for group in model_input_conf["feature_group"]["additional"]:
            if "dim" in group:
                sf = schema.dense_features.add()
                sf.name = group["name"]
                sf.length = group["dim"]
                sf.qualified_name = ""
            else:
                sf = schema.sparse_features.add()
                sf.name = group["name"]
                sf.qualified_name = ""

        label_count = model_input_conf["reader"]["label_count"]
        for i in range(label_count):
            label = schema.labels.add()
            # xdl.DataReader 只关注label_count 不关注内部的具体label含义，
            # 所以简单构造label
            label.name = "label_" + str(i + 1)

        hasher = hashlib.md5()
        hasher.update(schema.SerializeToString())
        checksum = hasher.hexdigest()

        # schema gen 执行多次，相同的schemagen 逻辑，执行的结果都相同，对应的artifact uri 也相同
        output_path = artifact_utils.get_single_uri(output_dict["output"])
        schema_path = os.path.join(output_path, checksum, "schema.pbtxt")

        fs, path = io_utils.resolve_filesystem_and_path(schema_path)
        if not fs.exists(path):
            logging.info(
                "create new schema to %s with checksum %s",
                schema_path,
                checksum,
            )
            io_utils.write_pbtxt_file(schema_path, schema)
        else:
            logging.info("schema with checksum %s already exist", checksum)
        # update outputs uri
        output_dict["output"][0].meta.uri = schema_path
