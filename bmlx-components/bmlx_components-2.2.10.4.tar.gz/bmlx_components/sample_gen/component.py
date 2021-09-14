# -*- coding: UTF-8 -*-
from bmlx.flow import (
    Component,
    ComponentSpec,
    ExecutorClassSpec,
    DriverClassSpec,
    ExecutionParameter,
    ChannelParameter,
    Channel,
    Executor,
    Artifact
)
from bmlx_components import custom_artifacts
from bmlx.metadata import standard_artifacts
from typing import Text, Dict, List, Any
from bmlx.execution.driver import BaseDriver
from bmlx.execution.launcher import Launcher
import subprocess
import re

from bmlx_components.sample_gen import submit_template

class SampleGenSpec(ComponentSpec):

    PARAMETERS = {
        "job_name": ExecutionParameter(
            type=(str, Text),
            description="任务名",
            optional=False
        ),
        "job_scene": ExecutionParameter(
            type=(str, Text),
            description="任务场景",
            optional=False
        ),
        "user_name": ExecutionParameter(
            type=(str, Text),
            description="用户名",
            optional=False
        ),
        "submit_main": ExecutionParameter(
            type=(str, Text),
            description="main py文件，可以是hdfs路径",
            optional=False
        ),
        "output_path_prefix": ExecutionParameter(
            type=(str, Text),
            description="输出路径前缀，后缀根据输入数据而变化，类似20201212或者20201212/12两种格式",
            optional=False
        ),
        "executors": ExecutionParameter(
            type=(str, int),
            description="spark executor数量，默认1",
            optional=True
        ),
        "submit_files": ExecutionParameter(
            type=(str, List[Text]),
            description="依赖的files，可以是hdfs路径",
            optional=True
        ),
        "submit_pyfiles": ExecutionParameter(
            type=(str, List[Text]),
            description="依赖的pyfiles，可以是hdfs路径",
            optional=True
        ),
        "submit_jars": ExecutionParameter(
            type=(str, List[Text]),
            description="依赖的jars，可以是jars路径",
            optional=True
        ),
        "submit_extra": ExecutionParameter(
            type=(str, Text),
            description="额外参数",
            optional=True
        ),
        "specific_path": ExecutionParameter(
            type=(str, Text),
            description="指定输入路径，如果该参数非空，则original_data参数不生效",
            optional=True
        ),
    }

    INPUTS = {
        "original_data": ChannelParameter(type=custom_artifacts.OriginSamples, optional=True),
    }

    OUTPUTS = {
        "output_path": ChannelParameter(type=standard_artifacts.Samples, optional=True),
    }

class SampleGenExecutor(Executor):

    def call_cmd(self, cmd_str):
        print('executing cmd : {}'.format(cmd_str))
        proc = subprocess.Popen([cmd_str], shell=True)
        return proc

    def wait_submit_cmd(self, proc):
        proc.wait()
        return proc.returncode

    def generate_output_path(self, input_path, output_path_prefix):
        if input_path[-1] == "/":
            process_path = input_path[:-1]
        else:
            process_path = input_path

        pattern_hour = "hdfs://.*/([0-9]{8})/([0-9]{2})$"
        res_hour = re.match(pattern_hour, process_path)
        if res_hour:
            return output_path_prefix + "/" + res_hour.group(1) + "/" + res_hour.group(2)
        else:
            pattern_day = "hdfs://.*/([0-9]{8})$"
            res_day = re.match(pattern_day, process_path)
            if res_day:
                return output_path_prefix + "/" + res_day.group(1)
        raise RuntimeError("Generate_output path failed.")

    def append_output_path(self, output_dict, output_path):
        artifact = Artifact(type_name=standard_artifacts.Samples.TYPE_NAME)
        artifact.meta.uri = output_path
        output_dict["output_path"].append(artifact)

    def run_script(
            self,
            input_path,
            output_path,
            exec_properties: Dict[Text, Any],
    ):
        print("----------  Spark start. input: {}, output: {}".format(input, output_path))
        job_name = exec_properties["job_name"]
        job_scene = exec_properties["job_scene"]
        user_name = exec_properties["user_name"]
        submit_main = exec_properties["submit_main"]
        executors = exec_properties["executors"]
        submit_files = exec_properties["submit_files"]
        submit_pyfiles = exec_properties["submit_pyfiles"]
        submit_jars = exec_properties["submit_jars"]
        submit_extra = exec_properties["submit_extra"]



        files = ""
        if submit_files:
            files = "--files " + ",".join(submit_files)

        pyfiles = ""
        if submit_pyfiles:
            pyfiles = "--py-files " + ",".join(submit_pyfiles)

        jars = ""
        if submit_jars:
            jars = "--jars " + ",".join(submit_jars)

        script = submit_template.SUMIT_SCRIPT.format(
            name=job_name,
            scene=job_scene,
            user=user_name,
            executors=executors,
            extra=submit_extra,
            files=files,
            pyfiles=pyfiles,
            jars=jars,
            main=submit_main,
            input_path=input_path,
            output_path=output_path
        )
        print("command: " + script)

        proc = self.call_cmd(script)
        code = self.wait_submit_cmd(proc)
        print("spark result code: {}".format(code))
        if code != 0:
            raise RuntimeError("spark running failed.")
        print("----------  Spark finish. input: {}, output: {}".format(input, output_path))

    def execute(
            self,
            input_dict: Dict[Text, List[Artifact]],
            output_dict: Dict[Text, List[Artifact]],
            exec_properties: Dict[Text, Any],
    ):
        self._log_startup(input_dict, output_dict, exec_properties)

        specific_path = exec_properties["specific_path"]
        output_path_prefix = exec_properties["output_path_prefix"]
        if specific_path:
            output_path = self.generate_output_path(specific_path, output_path_prefix)
            self.run_script(
                specific_path,
                output_path,
                exec_properties
            )
            self.append_output_path(output_dict, output_path)
        elif input_dict["original_data"] and len(input_dict["original_data"]) > 0:
            for input_meta in input_dict["original_data"]:
                output_path = self.generate_output_path(input_meta.meta.uri, output_path_prefix)
                self.run_script(
                    input_meta.meta.uri,
                    output_path,
                    exec_properties
                )
                self.append_output_path(output_dict, output_path)
        else:
            raise RuntimeError("Input paths not found.")


class SampleGen(Component):
    SPEC_CLASS = SampleGenSpec

    EXECUTOR_SPEC = ExecutorClassSpec(SampleGenExecutor)

    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    """
    job_name: 任务名
    job_scene： 任务场景
    user_name： 用户名
    submit_main： main py文件，可以是hdfs路径
    output_path_prefix： 输出路径前缀，后缀根据输入数据而变化，类似20201212或者20201212/12两种格式
    executors:  spark executor数量，默认1
    submit_files： 依赖的files，可以是hdfs路径
    submit_pyfiles：  依赖的pyfiles，可以是hdfs路径
    submit_jars：  依赖的jars，可以是jars路径
    submit_extra:  额外参数
    original_data：  上游输入的原始数据，Channel类型
    specific_path：   指定输入路径，如果该参数非空，则original_data参数不生效
    """
    def __init__(
            self,
            instance_name,
            job_name: Text,
            job_scene: Text,
            user_name: Text,
            submit_main: Text,
            output_path_prefix: Text,
            executors: int = 1,
            submit_files: List[Text] = "",
            submit_pyfiles: List[Text] = "",
            submit_jars: List[Text] = "",
            submit_extra: Text = "",
            original_data: Channel = None,
            specific_path: Text = "",
    ):
        output = Channel(
            artifact_type=standard_artifacts.Samples,
            artifacts=[standard_artifacts.Samples()],
        )
        spec = SampleGenSpec(
            job_name=job_name,
            job_scene=job_scene,
            user_name=user_name,
            submit_main=submit_main,
            output_path_prefix=output_path_prefix,
            executors=executors,
            submit_files=submit_files,
            submit_pyfiles=submit_pyfiles,
            submit_jars=submit_jars,
            submit_extra=submit_extra,
            specific_path=specific_path,
            original_data=original_data,
            output_path=output
        )

        super(SampleGen, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return Launcher
