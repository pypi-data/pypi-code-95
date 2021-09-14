from bmlx_components.sample_selector.driver import SampleSelectorDriver
from bmlx.flow import Node, Artifact, Channel
from bmlx.flow.driver_spec import DriverClassSpec
from typing import Union, List, Text, Type, Optional, Dict, Any
from bmlx.metadata import standard_artifacts


class SampleSelector(Node):
    DRIVER_SPEC = DriverClassSpec(SampleSelectorDriver)

    def __init__(
        self,
        instance_name,
        sample_uri_base: Text,
        model_uri_base: Text,
        start_sample_hour: Text = None,
        end_sample_hour: Optional[Text] = None,
        max_wait_minutes: int = 60,
        max_selected_sample_hours: int = 10,
        min_selected_sample_hours: int = 1,
        try_limit: int = 1,  # 允许component重试，try_limit 规定了 component 在一次pipeline run中最多执行次数。
    ):
        """
        SampleSelector 会选择出来基础模型和样本。
        流程介绍：
        一、基础模型的选择
            会在 model_uri_base 路径下，从当前小时开始搜索，直到 start_sample_hour - 1 所在的小时为止。
            找到的第一个可用模型作为基础模型；如果没找到，则没有基础模型直接开始训练。
            注：这个逻辑比较粗糙，但可以满足大多数的应用场景。

        二、样本的选择
          设置 start_sample_hour（必须设置） 为样本开始时间， end_sample_hour 为样本结束时间；
          根据选择出来的基准模型时间 last_model_hour ，结合 start_sample_hour 和 end_sample_hour 来选择样本。
            (1) 如果设置了 end_sample_hour, 则从 [max(last_model_hour, start_sample_hour), end_sample_hour] 中，
                从左向右 选择最少 min_selected_sample_hours 最多 max_selected_sample_hours 个小时的可用样本
            (2) 如果未设置 end_sample_hour，则选择 [max(last_model_hour, start_sample_hour), +∞) 中，
                从左向右 选择最少 min_selected_sample_hours 最多 max_selected_sample_hours 个小时的可用样本
        """
        assert sample_uri_base and model_uri_base and start_sample_hour

        self._sample_uri_base = sample_uri_base
        self._model_uri_base = model_uri_base
        self._start_sample_hour = start_sample_hour
        self._end_sample_hour = end_sample_hour
        self._max_wait_minutes = max_wait_minutes
        self._max_selected_sample_hours = max_selected_sample_hours
        self._min_selected_sample_hours = min_selected_sample_hours
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
        super(SampleSelector, self).__init__(
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
            "start_sample_hour": self._start_sample_hour,
            "max_wait_minutes": self._max_wait_minutes,
            "max_selected_sample_hours": self._max_selected_sample_hours,
            "min_selected_sample_hours": self._min_selected_sample_hours,
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
            "start_sample_hour": self._start_sample_hour,
            "end_sample_hour": self._end_sample_hour,
            "max_wait_minutes": self._max_wait_minutes,
            "max_selected_sample_hours": self._max_selected_sample_hours,
            "min_selected_sample_hours": self._min_selected_sample_hours,
        }
