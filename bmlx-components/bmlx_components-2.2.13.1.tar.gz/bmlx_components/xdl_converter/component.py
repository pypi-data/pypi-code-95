"""BMLX model converter component definition."""
from typing import Optional, Text, List
from bmlx.flow import (
    Artifact,
    Channel,
    Component,
    ComponentSpec,
    ExecutorClassSpec,
    DriverClassSpec,
    ExecutionParameter,
    ChannelParameter,
)
from bmlx_components.xdl_converter.driver import XdlConverterDriver
from bmlx.metadata import standard_artifacts
from bmlx_components import custom_artifacts
from bmlx_components.xdl_converter.executor import XdlConverterExecutor
from bmlx_components.xdl_converter.launcher import XdlConverterLauncher


class XdlConverterSpec(ComponentSpec):
    """ModelConverter component spec."""

    PARAMETERS = {
        "model_name": ExecutionParameter(
            type=str, optional=True, description="模型名称"
        ),
        "export_emb_default_threshold": ExecutionParameter(
            type=float,
            optional=False,
            description="导出embedding的默认threshold，embedding的score超过threshold才会导出到模型中",
        ),
        "half_p": ExecutionParameter(
            type=bool, optional=True, description="是否使用半精度压缩模型"
        ),
        "ceto_emb_base_dir": ExecutionParameter(
            type=(str, Text),
            optional=True,
            description="发布到ceto上的embedding数据的base路径, 默认为空，若手动指定则覆盖target中的地区对应路径",
        ),
        # 转换为在线预测图output 节点名字,如：y_pred = tf.sigmoid(y, name='xxx')。
        # 转化时会自动根据xxx为后缀寻找node 全称，这就要求xxx 在导出图里全局唯一。
        # 默认为 predict_node
        "output_node": ExecutionParameter(
            type=(str, Text), optional=True, description="tf预测图的输出节点"
        ),
        "model_class": ExecutionParameter(
            type=(str, Text), optional=True, description="模型的类型，比如RtpXdlModel"
        ),
        "optimize_tool_path": ExecutionParameter(
            type=(str, Text), optional=True, description="tf 图优化工具路径"
        ),
        "local_emb": ExecutionParameter(
            type=bool, optional=True, description="是否为本地embedding(本地模型)"
        ),
        "keys_count": ExecutionParameter(
            type=(str, Text), optional=True, description="zmap的key大小"
        ),
        "disable_skip_execution": ExecutionParameter(
            type=bool,
            optional=True,
            description="是否禁止掉 skip 该组件的操作，如果是，则该组件在pipeline中总是会执行",
        ),
    }

    INPUTS = {
        "model": ChannelParameter(
            type=standard_artifacts.Model, description="训练好的模型"
        ),
        "fg_conf": ChannelParameter(
            type=custom_artifacts.FgConf, description="fg 配置文件"
        ),
        "fg_lib": ChannelParameter(
            type=custom_artifacts.FgCppLib,
            optional=True,
            description="fg 的cpp so 文件",
        ),
    }

    OUTPUTS = {
        "output": ChannelParameter(
            type=custom_artifacts.ConvertedModel,
            description="转换后的模型,包含 tf graph, sparse embedding, fg conf, 小样本校验数据集[optional]",
        ),
    }


class XdlConverter(Component):
    SPEC_CLASS = XdlConverterSpec

    EXECUTOR_SPEC = ExecutorClassSpec(XdlConverterExecutor)

    DRIVER_SPEC = DriverClassSpec(XdlConverterDriver)

    def __init__(
        self,
        model: Channel,
        fg_conf: Channel,
        fg_lib: Optional[Channel] = None,
        model_name: Text = "",
        export_emb_default_threshold: float = 0.0,
        half_p: Optional[bool] = False,
        ceto_emb_base_dir: Optional[Text] = "hdfs://bigocluster/data/embs/",
        output_node: Optional[Text] = "predict_node",
        model_class: Optional[Text] = "RtpXdlV1",
        optimize_tool_path: Optional[
            Text
        ] = "hdfs://bigo-rt/user/bmlx/tools/tf_graph_optimize/offline_optimize",
        local_emb: bool = False,
        keys_count: Optional[Text] = None,
        disable_skip_execution: bool = False,
        instance_name: Optional[Text] = None,
    ):
        if not model_name:
            raise ValueError("model_name not provided")

        if not model:
            raise ValueError("model not provided")

        if not fg_conf:
            raise ValueError("fg_conf not provided")

        converted_model = Channel(
            artifact_type=custom_artifacts.ConvertedModel,
            # 注意！！！ 这里的 name 填充为model_name，用于显示在模型中心上
            artifacts=[custom_artifacts.ConvertedModel(name=model_name)],
        )

        if not instance_name:
            instance_name = "xdl_convert"

        spec = XdlConverterSpec(
            model=model,
            fg_conf=fg_conf,
            fg_lib=fg_lib,
            model_name=model_name,
            export_emb_default_threshold=export_emb_default_threshold,
            half_p=half_p,
            ceto_emb_base_dir=ceto_emb_base_dir,
            output_node=output_node,
            model_class=model_class,
            output=converted_model,
            optimize_tool_path=optimize_tool_path,
            local_emb=local_emb,
            keys_count=keys_count,
            disable_skip_execution=disable_skip_execution,
        )

        super(XdlConverter, self).__init__(
            spec=spec, instance_name=instance_name
        )

    def get_launcher_class(self, ctx):
        return XdlConverterLauncher

    def skip_execution(self, pipeline_execution, exec_properties) -> bool:
        if (
            not exec_properties["disable_skip_execution"]
            and not pipeline_execution.deployment_running
        ):
            return True
        else:
            return False
