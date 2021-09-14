from typing import Text, Optional, List
from bmlx.flow import (
    Component,
    ComponentSpec,
    ExecutorClassSpec,
    DriverClassSpec,
    ExecutionParameter,
    ChannelParameter,
    Channel,
)
from bmlx.execution.driver import BaseDriver
from bmlx.metadata import standard_artifacts
from bmlx_components import custom_artifacts
from bmlx.execution.launcher import Launcher
from bmlx_components.validate_score_comparer.executor import (
    ScoreComparerExecutor,
)

"""
比较原始日志中的得分 和 根据原始特征进行 feature-process + xdl-predict 之后的得分
"""


class ScoreComparerSpec(ComponentSpec):
    """ score comparer spec """

    PARAMETERS = {
        "online_score_location": ExecutionParameter(
            type=str, optional=True, description="指定online score在样本中的位置"
        ),
        "detail": ExecutionParameter(
            type=bool, optional=True, description="日志打印更具体分数及对比"
        ),
    }

    INPUTS = {
        "origin_samples": ChannelParameter(
            type=standard_artifacts.Samples, description="得分比对使用的原始样本(线上数据)"
        ),
        "predict_result": ChannelParameter(
            type=custom_artifacts.PredictResult,
            description="得分比对使用的预测后的文件(离线数据)",
        ),
    }

    OUTPUTS = {
        "compare_result": ChannelParameter(
            type=custom_artifacts.CompareResult, description="对比结果"
        ),
    }


class ScoreComparer(Component):
    SPEC_CLASS = ScoreComparerSpec
    EXECUTOR_SPEC = ExecutorClassSpec(ScoreComparerExecutor)
    DRIVER_SPEC = DriverClassSpec(BaseDriver)

    def __init__(
        self,
        origin_samples: Channel,
        predict_result: Channel,
        instance_name: Optional[Text] = None,
        online_score_location: Optional[Text] = None,
        detail: Optional[bool] = None,
    ):
        assert origin_samples and predict_result
        compare_result = Channel(
            artifact_type=custom_artifacts.CompareResult,
            artifacts=[custom_artifacts.CompareResult()],
        )
        spec = ScoreComparerSpec(
            origin_samples=origin_samples,
            predict_result=predict_result,
            compare_result=compare_result,
            online_score_location=online_score_location,
            detail=detail,
        )
        if not instance_name:
            instance_name = "score_comparer"

        super(ScoreComparer, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return Launcher
