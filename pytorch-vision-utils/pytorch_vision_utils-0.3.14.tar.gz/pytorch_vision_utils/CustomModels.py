"""Contains all of the available models for customization. 
"""

from torch import nn

from .custom_models.inceptionv4 import InceptionV4
from .custom_models.mobilenetv2 import MobileNetV2
from .custom_models.resnext import ResNeXt101_32x4d
from .custom_models.vggm import VGGM
from .custom_models.xception import Xception

_model_names = ["inceptionv4",
                "mobilenetv2", 
                "resnext101_32x4d",
                "vggm",
                "xception"]

_models = [InceptionV4,
           MobileNetV2,
           ResNeXt101_32x4d,
           VGGM,
           Xception]

avail_models = dict(zip(_model_names, _models))
