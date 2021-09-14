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
from bmlx.metadata import standard_artifacts
from typing import Text, Dict, List, Any
from bmlx.execution.driver import BaseDriver
from bmlx.execution.launcher import Launcher
import os
import time
import subprocess
import sys

from bmlx_components.spark_submitter import submit_template

FILES="/files"
PYFILES="/pyfiles"
JARS="/jars"

class SparkSubmitterSpec(ComponentSpec):
    PARAMETERS = {
        "name": ExecutionParameter(
            type=(str, Text),
            optional=False
        ),
        "user": ExecutionParameter(
            type=(str, Text),
            optional=False
        ),
        "executors": ExecutionParameter(
            type=(str, int),
            optional=False
        ),
        "path": ExecutionParameter(
            type=(str, Text),
            optional=True
        ),
        "extra_param": ExecutionParameter(
            type=(str, Text),
            optional=True
        ),
        "main_param": ExecutionParameter(
            type=(str, Text),
            optional=True
        ),
        "timestamp": ExecutionParameter(
            type=(str, int),
            optional=True
        ),
    }

    INPUTS = {
        "deps": ChannelParameter(type=standard_artifacts.Schema, optional=True),
    }

    OUTPUTS = {
        "output": ChannelParameter(type=standard_artifacts.Schema, optional=True),
    }

class SparkSubmitterExecutor(Executor):
    SUBMIT_STDOUT = []
    LOG_FILE = './bmlx_spark.log'

    def submit_init(self):
        proc = self.call_cmd('touch {}'.format(self.LOG_FILE))
        self.collect_std(proc)

    def call_cmd(self, cmd_str):
        print('executing cmd : {}'.format(cmd_str))
        proc = subprocess.Popen([cmd_str], stdout=subprocess.PIPE, shell=True)
        return proc

    def collect_std(self, proc):
        with open(self.LOG_FILE, 'wb') as fd:
            for line in iter(proc.stdout.readline, b''):
                sys.stdout.write(bytes.decode(line).strip())
                fd.write(line)

    def print_std(self):
        with open(self.LOG_FILE) as fd:
            lines = fd.readlines()
            for line in lines:
                print(line)

    def wait_submit_cmd(self, proc):
        proc.wait()
        return proc.returncode

    def get_file_list(self, path_str):
        result = []
        if os.path.exists(path_str):
            paths = os.listdir(path_str)
            for path in paths:
                p = path_str + "/" + str(path)
                if not os.path.isdir(p):
                    result.append(p)
        return ",".join(result)

    def execute(
            self,
            input_dict: Dict[Text, List[Artifact]],
            output_dict: Dict[Text, List[Artifact]],
            exec_properties: Dict[Text, Any],
    ):
        self._log_startup(input_dict, output_dict, exec_properties)
        name = exec_properties["name"]
        user = exec_properties["user"]
        executors = exec_properties["executors"]
        path = exec_properties["path"]
        extra_param = exec_properties["extra_param"]
        main_param = exec_properties["main_param"]
        timestamp = exec_properties["timestamp"]
        real_timestamp = timestamp
        if real_timestamp <= 0:
            real_timestamp = exec_properties.get("pipeline_execution_time", int(time.time()))

        if path != "":
            output_uri = time.strftime(path, time.localtime(real_timestamp))
            output_dict["output"][0].meta.uri = output_uri

        base = os.getcwd()
        files = self.get_file_list(base + FILES)
        if files != "":
            files = "--files " + files
        pyfiles = self.get_file_list(base + PYFILES)
        if pyfiles != "":
            pyfiles = "--py-files " + pyfiles
        jars = self.get_file_list(base + JARS)
        if jars != "":
            jars = "--jars " + jars
        main = base + "/main.py"

        script = submit_template.SUMIT_SCRIPT.format(
            name=name,
            user=user,
            executors=executors,
            extra=extra_param,
            files=files,
            pyfiles=pyfiles,
            jars=jars,
            main=main,
            main_param=main_param,
            timestamp=real_timestamp
        )
        print("command: " + script)

        self.submit_init()
        proc = self.call_cmd(script)
        code = self.wait_submit_cmd(proc)
        print("spark result code: {}".format(code))
        self.collect_std(proc)
        self.print_std()
        if code != 0:
            raise RuntimeError("spark running failed.")

class SparkSubmitter(Component):
    SPEC_CLASS = SparkSubmitterSpec

    EXECUTOR_SPEC = ExecutorClassSpec(SparkSubmitterExecutor)

    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
            self,
            instance_name,
            name: Text = "",
            user: Text = "",
            executors: int = 1,
            path: Text = "",
            extra_param: Text = "",
            main_param: Text = "",
            deps: Channel = None,
            timestamp: int = -1
    ):
        output = Channel(
            artifact_type=standard_artifacts.Schema,
            artifacts=[standard_artifacts.Schema()],
        )
        spec = SparkSubmitterSpec(
            name=name,
            user=user,
            executors=executors,
            path=path,
            extra_param=extra_param,
            main_param=main_param,
            deps=deps,
            output=output,
            timestamp=timestamp
        )

        super(SparkSubmitter, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return Launcher