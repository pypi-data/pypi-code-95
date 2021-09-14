"""bmlx trainer executor."""
import os
import logging
import re
import xdl
import functools
import tempfile
from typing import Any, Dict, List, Text, Tuple
from pathlib import Path

from bmlx.flow import Artifact
from bmlx_components.proto import schema_pb2, model_pb2
from bmlx.utils import import_utils, artifact_utils, io_utils
from bmlx_components.xdl_base.executor import XdlExecutor
from bmlx_components.xdl_base.runner import XdlRunner
from bmlx_components.xdl_base.reader import XdlReader

MY_DIR = os.path.dirname(os.path.realpath(__file__))


class XdlTrainerExecutor(XdlExecutor):
    def common_execute(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        # 将 tf graph 和 model conf 拷贝到 checkpoint 目录（带有date-hour 信息的目录，而不是放在最外层）
        _, model_version = self._resolve_latest_sample_meta(
            input_dict["samples"]
        )
        fs, path = io_utils.resolve_filesystem_and_path(
            exec_properties["model_uri_base"]
        )
        meta_files = [
            fname
            for fname in fs.ls(path)
            if os.path.basename(fname).startswith("tf_")
        ]
        with tempfile.TemporaryDirectory() as tempdir:
            for fname in meta_files:
                base_name = os.path.basename(fname)
                local_path = os.path.join(tempdir, base_name)
                dst_path = os.path.join(
                    exec_properties["model_uri_base"],
                    model_version,
                    base_name,
                )
                if fs.exists(dst_path):
                    fs.delete(dst_path)
                fs.download(fname, local_path)
                fs.upload(local_path, dst_path)
            # 构造 _SUCCESS 用来标识训练成功
            local_path = os.path.join(tempdir, "_SUCCESS")
            Path(local_path).touch()
            dst_path = os.path.join(
                exec_properties["model_uri_base"], model_version, "_SUCCESS"
            )
            fs.upload(local_path, dst_path)
        # xdl 中 checkpoint_dir/checkpoints 文件会覆盖 model_bank，
        # 即实际使用的是 checkpoints 文件中指定的 上个模型
        # TODO: 后续请修改XDL 这个奇葩逻辑。应该 model_bank 有更高优先级
        fs, path = io_utils.resolve_filesystem_and_path(
            exec_properties["model_uri_base"]
        )
        checkpoints_file = os.path.join(
            exec_properties["model_uri_base"], "checkpoints"
        )
        if fs.exists(checkpoints_file):
            try:
                fs.delete(checkpoints_file)
            except OSError as e:
                logging.error(
                    "Failed to delete file %s, err: %s", checkpoints_file, e
                )

        # 获得输出meta的uri， meta uri中会存储具体的文件存储的位置
        meta_output_path = artifact_utils.get_single_uri(
            output_dict["output"]
        )
        logging.info(
            "train finished, model meta gen to %s" % meta_output_path
        )
        model = model_pb2.Model()
        model.model_path = exec_properties["model_uri_base"]
        model.model_version = model_version
        io_utils.write_pbtxt_file(
            os.path.join(meta_output_path, "model.pbtxt"), model
        )

    def execute_as_worker(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        schema = self._resolve_schema(input_dict["schema"])
        _, model_version = self._resolve_latest_sample_meta(
            input_dict["samples"]
        )

        assert (
            exec_properties.get("parameters") is not None
        ), "please call _load_xdl_parameters first"
        # resolve train func
        stage = exec_properties["stage"]
        module = exec_properties.get("module")
        parameters = exec_properties["parameters"]

        meta_output_path = artifact_utils.get_single_uri(output_dict["output"])

        if exec_properties["enable_trace"]:
            parameters.set_args(
                {"hooks.trace.output_dir": meta_output_path,}
            )
        else:
            parameters.set_args({"hooks.trace": {}})

        if parameters["hooks"]["save_metrics"].exists():
            parameters.set_args(
                {
                    "hooks.save_metrics.output_file_path": os.path.join(
                        meta_output_path,
                        parameters["hooks"]["save_metrics"][
                            "output_file_name"
                        ].as_str("metrics.txt"),
                    )
                }
            )

        if not module:
            raise ValueError("'module' field not set in 'exec_properties'.")

        runner = XdlRunner(
            model_module=module,
            parameters=parameters,
            stage=stage,
            is_training=True,
            model_version=model_version,
            schema=schema,
            is_local=exec_properties["is_local"],
            metrics_sinker=self._tf_metrics_sinker(exec_properties),
        )

        reader_conf = parameters["reader"]
        # 这里给xdl.reader.script 进行赋值，来传递一些在 用户的 convert 脚本中会用到的参数
        reader_conf.set_args(
            {"script": self._substitude_reader_script(reader_conf["script"].as_str()) + f" -jt {stage} -p bmlx"}
        )
        reader = XdlReader.get_reader(
            conf=reader_conf,
            name="xdl_reader",
            input_dict=input_dict,
            schema=schema,
            sampling_rate=exec_properties["sampling_rate"],
        )

        runner.run(reader=reader)

        if xdl.get_run_mode() == "local" or xdl.get_task_index() == 0:
            # 将 tf graph 和 model conf 拷贝到 checkpoint 目录（带有date-hour 信息的目录，而不是放在最外层）
            # _, model_version = self._resolve_latest_sample_meta(
            #     input_dict["samples"]
            # )
            fs, path = io_utils.resolve_filesystem_and_path(
                exec_properties["model_uri_base"]
            )
            meta_files = [
                fname
                for fname in fs.ls(path)
                if os.path.basename(fname).startswith("tf_")
            ]
            with tempfile.TemporaryDirectory() as tempdir:
                for fname in meta_files:
                    base_name = os.path.basename(fname)
                    local_path = os.path.join(tempdir, base_name)
                    dst_path = os.path.join(
                        exec_properties["model_uri_base"],
                        model_version,
                        base_name,
                    )
                    if fs.exists(dst_path):
                        fs.delete(dst_path)
                    fs.download(fname, local_path)
                    fs.upload(local_path, dst_path)
                # 构造 _SUCCESS 用来标识训练成功
                local_path = os.path.join(tempdir, "_SUCCESS")
                Path(local_path).touch()
                dst_path = os.path.join(
                    exec_properties["model_uri_base"], model_version, "_SUCCESS"
                )
                fs.upload(local_path, dst_path)
            # xdl 中 checkpoint_dir/checkpoints 文件会覆盖 model_bank，
            # 即实际使用的是 checkpoints 文件中指定的 上个模型
            # TODO: 后续请修改XDL 这个奇葩逻辑。应该 model_bank 有更高优先级
            fs, path = io_utils.resolve_filesystem_and_path(
                exec_properties["model_uri_base"]
            )
            checkpoints_file = os.path.join(
                exec_properties["model_uri_base"], "checkpoints"
            )
            if fs.exists(checkpoints_file):
                try:
                    fs.delete(checkpoints_file)
                except OSError as e:
                    logging.error(
                        "Failed to delete file %s, err: %s", checkpoints_file, e
                    )

            # 获得输出meta的uri， meta uri中会存储具体的文件存储的位置
            meta_output_path = artifact_utils.get_single_uri(
                output_dict["output"]
            )
            logging.info(
                "train finished, model meta gen to %s" % meta_output_path
            )
            model = model_pb2.Model()
            model.model_path = exec_properties["model_uri_base"]
            model.model_version = model_version
            io_utils.write_pbtxt_file(
                os.path.join(meta_output_path, "model.pbtxt"), model
            )
                # self.common_execute(input_dict, output_dict, exec_properties)

    def execute_as_chief_worker(
        self,
        input_dict: Dict[Text, List[Artifact]],
        output_dict: Dict[Text, List[Artifact]],
        exec_properties: Dict[Text, Any],
    ):
        # self.common_execute(input_dict, output_dict, exec_properties)
        pass