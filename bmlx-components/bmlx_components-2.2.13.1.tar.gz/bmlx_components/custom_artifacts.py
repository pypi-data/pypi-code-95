"""
bmlx flow artifacts
bmlx.metadata.standard_artifacts 中定义的 Artifact 是最基本的。
bmlx 用户可以在该文件中增加自定义的Artifact 类型
"""

from bmlx.flow import Artifact


class FgConf(Artifact):
    TYPE_NAME = "FgConf"


class FgCppLib(Artifact):
    TYPE_NAME = "FgCppLib"


class FgPyLib(Artifact):
    TYPE_NAME = "FgPyLib"


class PushedModel(Artifact):
    TYPE_NAME = "PushedModel"


class ConvertedModel(Artifact):
    TYPE_NAME = "ConvertedModel"


class OriginSamples(Artifact):
    TYPE_NAME = "OriginSamples"


class PredictResult(Artifact):
    TYPE_NAME = "PredictResult"


class CompareResult(Artifact):
    TYPE_NAME = "CompareResult"


class ModelEval(Artifact):
    TYPE_NAME = "ModelEval"


class TextInfo(Artifact):
    TYPE_NAME = "TextInfo"


class ModelSample(Artifact):
    TYPE_NAME = "ModelSample"


class SampleScore(Artifact):
    TYPE_NAME = "SampleScore"


class CheckSample(Artifact):
    TYPE_NAME = "CheckSample"


class RtpResult(Artifact):
    TYPE_NAME = "RtpResult"