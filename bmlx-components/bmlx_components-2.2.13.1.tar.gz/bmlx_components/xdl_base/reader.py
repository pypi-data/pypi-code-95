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
        if app_id is None:
            app_id = "xdl"
        topic, _ = rpath.split("#")
        from xdl.python.pybind import get_PartNum
        part_num = get_PartNum(namenode, topic, app_id)
        print("part_num:", part_num, flush=True)
        assert part_num >= worker_num and part_num % worker_num == 0, "kafka partition num is {}, worker num should be divided by part num with no remainder".format(part_num)
        return part_num

    @classmethod
    def _resolve_sample_files(
        cls,
        schema: schema_pb2.Schema,
        sample_artifacts: List[Artifact],
        sampling_rate: float,
        reverse_file: bool,
        multi_shuffle_file: bool,
        reader_threads: int
    ):
        if not sample_artifacts:
            return []
        if sample_artifacts[0].meta.uri.startswith("kafka"):
            assert len(sample_artifacts) == 1, "sample_artifacts should be [kafka_path]"
            kafka_path = sample_artifacts[0].meta.uri
            _, namenode, rpath = xdl.DataReader.decode_path(sample_artifacts[0].meta.uri)
            return [kafka_path + "#" + str(cls._resolve_kafka_partition(namenode, rpath))]
        elif sample_artifacts[0].meta.uri.startswith("pulsar"):
            assert len(sample_artifacts) == 2, "sample_artifacts should be [pulsar_path, normal_path]"
            pulsar_path = sample_artifacts[0].meta.uri
            normal_path = sample_artifacts[1].meta.uri
            print("pulsar_path: ", pulsar_path, flush=True)
            print("normal_path: ", normal_path, flush=True)
            assert pulsar_path > normal_path, "check pulsar_path: " + pulsar_path + " and normal_path: " + normal_path
            if xdl.get_task_index() == 0:
                reader_threads = str(int(reader_threads) + 1)
            if xdl.get_task_index() != 0:
                pathlist = [normal_path] * int(reader_threads)
            else:
                pathlist = [pulsar_path] + ([normal_path] *(int(reader_threads) - 1))
            return pathlist
        # hdfs 
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
            if fs_type == pybind.fs.kafka or fs_type == pybind.fs.pulsar:
                return False
            return (
                False
                if xdl.get_run_mode() == "local"
                else bool(conf["global_schedule"])
            )

        def _resolve_threads(fs_type, namenode, rpath):
            if fs_type == pybind.fs.kafka:
                from xdl.python.utils.config import get_task_num
                worker_num = get_task_num()
                part_num = XdlReader._resolve_kafka_partition(namenode, rpath)
                return (
                    int(part_num / worker_num),
                    conf["threads"]["packer"].as_number(),
                )
            else:
                #pulsar hdfs
                return conf["threads"]["reader"].as_number(), conf["threads"]["packer"].as_number()

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

        fs_type, namenode, rpath = xdl.DataReader.decode_path(input_dict["samples"][0].meta.uri)

        reader_threads, packer_threads = _resolve_threads(fs_type, namenode, rpath)

         # get samples
        sampled_files = cls._resolve_sample_files(
            schema,
            input_dict["samples"]
            if not specific_samples
            else input_dict["specific_samples"], # 以参数而不是input channel的方式指定样本，driver中应构造specific_samples于input_dict中
            sampling_rate,
            bool(conf["reverse_file"]),
            bool(conf["multi_shuffle_file"]),
            reader_threads
        )
        if not sampled_files:
            raise ValueError("Empty samples!")
        global_scheduler = _resolve_global_schedule(fs_type)
        print("sampled_files: ", sampled_files, flush=True)
        reader = xdl.DataReader(
            ds_name=name,
            namenode=namenode,
            fs_type=fs_type,
            paths=sampled_files
            if xdl.get_task_index() == 0 or not global_scheduler
            else None,  # 只需要 worker master设置
            file_type=_resolve_data_format(),
            enable_state=bool(conf["enable_state"]),
            global_schedule=global_scheduler,
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
        elif conf["ztype"].as_str() == "txt": # for pred_emb request rtp support
            reader.ztype(xdl.ztypes.txt)
        else:
            raise Exception("ztype: " + conf["ztype"].as_str() + " not support.")
       
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
        assert "inputformat" in conf, "don't forget to set inputformat"
        if conf["inputformat"].as_str() == "RecordIO":
            reader.inputformat(xdl.inputformats.RecordIO)
        elif conf["inputformat"].as_str() == "Text":
            reader.inputformat(xdl.inputformats.Text)
        else:
            raise Exception("inputformat: " + conf["inputformat"].as_str() + " not support.")

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
