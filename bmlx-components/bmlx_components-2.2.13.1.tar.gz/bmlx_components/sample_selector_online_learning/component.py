from bmlx_components.sample_selector_online_learning.driver import SampleSelectorForOnlineLearningDriver
from bmlx.flow import Node, Artifact, Channel
from bmlx.flow.driver_spec import DriverClassSpec
from typing import Union, List, Text, Type, Optional, Dict, Any
from bmlx.metadata import standard_artifacts

class SampleSelectorForOnlineLearning(Node):
    DRIVER_SPEC = DriverClassSpec(SampleSelectorForOnlineLearningDriver)

    def __init__(
        self,
        instance_name,
        sample_uri_base: Text,
        model_uri_base: Text,
        try_limit: int = 1,  # 允许component重试，try_limit 规定了 component 在一次pipeline run中最多执行次数。
    ):
        """
        SampleSelectorForOnlineLearning 是专门用于在线kafka和pulsar任务
        流程介绍：
        一、基础模型的选择
            会从model_uri_base下面的checkpoint文件中找到最新的ckpt载入

        二、样本的选择
            如果没有配置结束时间点，则默认补齐
        """
        assert sample_uri_base and model_uri_base
        self._sample_uri_base = sample_uri_base
        self._model_uri_base = model_uri_base
        self._output_dict = {
            "samples": Channel(
                artifact_type=standard_artifacts.Samples,
                artifacts=[standard_artifacts.Samples()],
            ),
            "model": Channel(
                artifact_type=standard_artifacts.Model,
                artifacts=[standard_artifacts.Model()],
                optional=True,
            ),
        }
        super(SampleSelectorForOnlineLearning, self).__init__(
            instance_name=instance_name, try_limit=try_limit
        )

    def __repr__(self):
        return (
            "SampleSelector: name:%s sample_uri_base:%s, model_uri_base:%s"
            % (self._instance_name, self._sample_uri_base, self._model_uri_base)
        )

    def to_json_dict(self) -> Dict[Text, Any]:
        return {
            "instance_name": self._instance_name,
            "output_dict": self._output_dict,
            "sample_uri_base": self._sample_uri_base,
            "model_uri_base": self._model_uri_base,
            "driver_spec": self.driver_spec,
            "executor_spec": self.executor_spec,
        }

    @property
    def inputs(self) -> Dict[str, Channel]:
        return {}

    @property
    def outputs(self) -> Dict[str, Channel]:
        return self._output_dict

    @property
    def exec_properties(self) -> Dict[Text, Any]:
        return {
            "sample_uri_base": self._sample_uri_base,
            "model_uri_base": self._model_uri_base,
        }
