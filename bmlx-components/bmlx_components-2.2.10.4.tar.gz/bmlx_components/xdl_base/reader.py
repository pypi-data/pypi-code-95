import xdl
import random
import logging
import datetime

from typing import Dict, Text, List
from bmlx_components.proto import schema_pb2
from bmlx.flow import Artifact
from bmlx.utils import io_utils
from xdl.python import pybind


class XdlReader(object):
    @classmethod
    def _resolve_kafka_partition(cls, namenode, rpath):
        from xdl.python.utils.config import get_task_num, get_app_id

        worker_num = get_task_num()
        app_id = get_app_id()
        import xdl.python.io.read_kafka as kafka_op

        topic, _ = rpath.split("#")
        part_num = kafka_op.get_part_num(namenode, topic, app_id)
        assert (
            part_num >= worker_num and part_num % worker_num == 0
        ), "kafka partition num is {}, worker num should be divided by part num with no remainder".format(
            part_num
        )
        return part_num

    @classmethod
    def _resolve_sample_files(
        cls,
        schema: schema_pb2.Schema,
        sample_artifacts: List[Artifact],
        sampling_rate: float,
        reverse_file: bool,
        multi_shuffle_file: bool,
    ):
        if not sample_artifacts:
            return []
        if sample_artifacts[0].meta.uri.startswith("kafka"):
            _, namenode, rpath = xdl.DataReader.decode_path(
                sample_artifacts[0].meta.uri
            )
            return [
                sample_artifacts[0].meta.uri
                + "#"
                + str(cls._resolve_kafka_partition(namenode, rpath))
            ]

        def is_valid_sample_file(file_path):
            if (
                file_path.split("/")[-1] == "_SUCCESS"
                or file_path.find("origin_samples") >= 0
                or file_path.find(".inprogress.") >= 0
            ):
                return False
            return True

        def collect_file_in_hour(file_list):
            time_format_hour = "%Y%m%d/%H"
            items_tmp = file_list[0].split("/")
            try:
                datetime.strptime(
                    "{}/{}".format(items_tmp[-3], items_tmp[-2]),
                    time_format_hour,
                )
                hours_delta = 1
            except Exception:
                hours_delta = 24
            timestr_2_file_list = dict()
            for line in file_list:
                items_tmp = line.split("/")
                if hours_delta == 1:
                    timestr = "{}/{}".format(items_tmp[-3], items_tmp[-2])
                else:
                    timestr = items_tmp[-2]

                timestr_2_file_list.setdefault(timestr, [])
                timestr_2_file_list[timestr].append(line)
            return timestr_2_file_list

        def shuffle_file_in_slots(file_list):
            timestr_2_file_lst = collect_file_in_hour(file_list)
            res_lst = []
            for timestr in timestr_2_file_lst.keys():
                random.shuffle(timestr_2_file_lst[timestr])
                res_lst.extend(timestr_2_file_lst[timestr])
            return res_lst

        def sample_file_in_slots(file_list, files_sample_rate):
            timestr_2_file_lst = collect_file_in_hour(file_list)
            res_lst = []
            for timestr in timestr_2_file_lst.keys():
                if not timestr_2_file_lst[timestr]:
                    continue
                res = random.sample(
                    timestr_2_file_lst[timestr],
                    max(
                        1,
                        int(
                            len(timestr_2_file_lst[timestr]) * files_sample_rate
                        ),
                    ),
                )
                res_lst.extend(res)
            return res_lst

        cur_fs = None
        pathlist = []
        for sample in sample_artifacts:
            fs, uri = io_utils.resolve_filesystem_and_path(sample.meta.uri)
            if cur_fs is not None and type(fs) != type(cur_fs):
                raise RuntimeError(
                    "you could only passing hdfs or local file, not both!"
                )
            cur_fs = fs
            if cur_fs.isdir(uri):
                pathlist.append(uri)
            else:
                pathlist.append(sample.meta.uri)

        file_list = []
        for path in pathlist:
            if cur_fs.isdir(path):
                for f in cur_fs.ls(path):
                    if is_valid_sample_file(f):
                        file_list.append(f)
            elif is_valid_sample_file(path):
                file_list.append(path)

        if reverse_file:
            file_list.reverse()

        # 单个小时/单天的样本进行shuffle，不同小时/天的样本仍保持相对顺序
        if multi_shuffle_file:
            file_list = shuffle_file_in_slots(file_list)

        # 抽样, 仍然保持顺序，且每个slot 中的抽样比例相同
        if sampling_rate != 1.0:
            file_list = sample_file_in_slots(file_list, sampling_rate)

        logging.info(
            "resolve sample files, left files count: %d", len(file_list)
        )
        return file_list

    @classmethod
    def get_reader(
        cls,
        name: Text,
        conf,
        schema: schema_pb2.Schema,
        input_dict: Dict[Text, List[Artifact]],
        sampling_rate: float,
        specific_samples: bool = False,
    ):
        def _resolve_global_schedule(fs_type):
            if fs_type == pybind.fs.kafka:
                return False
            return (
                False
                if xdl.get_run_mode() == "local"
                else bool(conf["global_schedule"])
            )

        def _resolve_threads(fs_type, rpath):
            if fs_type == pybind.fs.kafka:
                from xdl.python.utils.config import get_task_num, get_app_id

                worker_num = get_task_num()
                topic, _ = rpath.split("#")
                app_id = get_app_id()
                import xdl.python.io.read_kafka as kafka_op

                part_num = kafka_op.get_part_num(namenode, topic, app_id)
                assert (
                    part_num >= worker_num and part_num % worker_num == 0
                ), "kafka partition num is {}, worker num should be divided by part num with no remainder".format(
                    part_num
                )
                return (
                    int(part_num / worker_num),
                    conf["threads"]["packer"].as_number(),
                )
            else:
                return (
                    conf["threads"]["reader"].as_number(),
                    conf["threads"]["packer"].as_number(),
                )

        def _resolve_data_format():
            if conf["parser"].as_str() == "txt":
                return pybind.parsers.txt
            elif conf["parser"].as_str() == "pb":
                return pybind.parsers.pb
            else:
                raise Exception(
                    "currently not support parser [%s]"
                    % conf["parser"].as_str()
                )

        # get samples
        sampled_files = cls._resolve_sample_files(
            schema,
            input_dict["samples"]
            if not specific_samples
            else input_dict["specific_samples"], # 以参数而不是input channel的方式指定样本，driver中应构造specific_samples于input_dict中
            sampling_rate,
            bool(conf["reverse_file"]),
            bool(conf["multi_shuffle_file"]),
        )

        if not sampled_files:
            raise ValueError("Empty samples!")

        fs_type, namenode, rpath = xdl.DataReader.decode_path(sampled_files[0])

        reader_threads, packer_threads = _resolve_threads(fs_type, rpath)

        reader = xdl.DataReader(
            ds_name=name,
            namenode=namenode,
            fs_type=fs_type,
            paths=sampled_files
            if xdl.get_task_index() == 0
            else None,  # 只需要 worker master设置
            file_type=_resolve_data_format(),
            enable_state=bool(conf["enable_state"]),
            global_schedule=_resolve_global_schedule(fs_type),
        )

        # configure xld reader
        reader.epochs(conf["epoch"].as_number()).threads(
            packer_threads, reader_threads,
        ).batch_size(conf["batch_size"].as_number()).label_count(
            len(schema.labels)
        )
        if conf["ztype"].as_str() == "gz":
            reader.ztype(xdl.ztypes.gz)
        elif conf["ztype"].as_str() == "zlib":
            reader.ztype(xdl.ztypes.zlib)
        elif conf["ztype"].as_str() == "pb":
            reader.ztype(xdl.ztypes.pb)

        assert "inputformat" in conf, "don't forget to set inputformat"
        if conf["inputformat"].as_str() == "RecordIO":
            reader.inputformat(xdl.inputformats.RecordIO)
        elif conf["inputformat"].as_str() == "Text":
            reader.inputformat(xdl.inputformats.Text)
        else:
            raise Exception("inputformat: " + conf["inputformat"].as_str() + " not support.")


        reader.keep_skey(bool(conf["keep_skey"]))
        if bool(conf["shuffle_file"]):
            reader.shuffle_file()
        if bool(conf["shuffle_sample"]):
            reader.shuffle_sample()

        if conf["shuffle_queue_min_batch"].exists():
            reader.shuffle_sample_min_batch_num(
                conf["shuffle_queue_min_batch"].as_number()
            )

        # if conf["shuffle_queue_max_batch"].exists():
        #     reader.shuffle_sample_max_batch_num(
        #         conf["shuffle_queue_max_batch"].as_number()
        #     )
        reader.unique_ids(bool(conf["unique_ids"]))

        # set script and feature
        reader.set_script(conf["script"].as_str())

        for sparse_feature in schema.sparse_features:
            reader.feature(
                name=sparse_feature.name,
                type=xdl.features.sparse,
                serialized=True,
            )

        for dense_feature in schema.dense_features:
            reader.feature(
                name=dense_feature.name,
                type=xdl.features.dense,
                nvec=dense_feature.length,
            )

        if not bool(conf["enable_state"]):
            reader.startup()

        return reader
