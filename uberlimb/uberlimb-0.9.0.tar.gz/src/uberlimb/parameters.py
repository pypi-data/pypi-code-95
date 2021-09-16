from enum import Enum
from typing import Optional

from pydantic import (BaseModel, PositiveInt, PositiveFloat, conint, Field,
                      NonNegativeFloat)


class BaseEnum(str, Enum):
    @classmethod
    def as_list(cls):
        return [x.value for x in list(cls)]

    @classmethod
    def get_index(cls, value):
        return cls.as_list().index(value)


# I cherry-picked only those activations that look different
# from each other.
class ModelActivation(BaseEnum):
    GELU = 'gelu'
    HARD_SIGMOID = 'hard_sigmoid'
    LINEAR = 'linear'
    SIGMOID = 'sigmoid'
    SINUS = 'sinus'
    EXP1 = 'experimental1'
    TANH = 'tanh'


class ModelArchitecture(BaseEnum):
    PERCEPTRON = 'perceptron'
    DENSENET = 'densenet'
    RESNET = 'resnet'
    RESNET_CONCAT = 'resnet_concat'
    CHAIN = 'chain'
    PLEXUS = 'plexus'


class PeriodicFunctionType(BaseEnum):
    DISABLED = 'None'
    SIN = 'Sin'
    TANG = 'Tan(square)'
    SECRET_FUNCTION1 = 'Squares#2'
    KVADRATIKI_S_RESHETKAMI = 'Squares and stripes'
    TILES_W_BUBBLES = 'Tiles with bubbles'
    EXP = 'Experimental'
    EXP2 = 'Experimental2'
    EXP3 = 'Experimental3'


class ModelMode(BaseEnum):
    FAN_IN = 'fan_in'
    FAN_OUT = 'fan_out'
    FAN_AVG = 'fan_avg'


class ModelDistribution(BaseEnum):
    TRUNCATED_NORMAL = 'truncated_normal'
    NORMAL = 'normal'
    UNTRUNCATED_NORMAL = 'untruncated_normal'
    UNIFORM = 'uniform'


class FourierMode(BaseEnum):
    DISABLED = 'disabled'
    ALL = 'all'
    # XY = 'XY'


class ModelParams(BaseModel):
    seed: int = 43
    width: PositiveInt = 3
    depth: PositiveInt = 3
    variance: PositiveFloat = 512
    mode: ModelMode = ModelMode.FAN_IN
    distribution: ModelDistribution = ModelDistribution.TRUNCATED_NORMAL
    architecture: ModelArchitecture = ModelArchitecture.DENSENET
    activation: ModelActivation = ModelActivation.SIGMOID
    out_activation: ModelActivation = ModelActivation.SIGMOID
    f_mode: FourierMode = FourierMode.DISABLED


class InputSpaceParams(BaseModel):
    alpha: float = 0.5
    beta: float = 0.5
    scale: PositiveFloat = 1
    offset_x: float = 0
    offset_y: float = 0
    custom_function: Optional[str] = None
    x_resolution: conint(gt=1, multiple_of=2) = 1280
    y_resolution: conint(gt=1, multiple_of=2) = 800
    rotation: float = 0
    resolution_factor: PositiveFloat = 1
    periodic_function: PeriodicFunctionType = PeriodicFunctionType.DISABLED
    per_factor: float = 1


class FrameColorMap(BaseEnum):
    BINNING = 'Binning'
    BC_JETBRAINS = 'JetBrains product colorway'
    BC_SPACE = 'Space product colorway'
    BC_IDEA = 'IntelliJ IDEA product colorway'
    BC_PHPSTORM = 'PhpStorm product colorway'
    BC_PYCHARM = 'PyCharm product colorway'
    BC_RUBYMINE = 'RubyMine product colorway'
    BC_WEBSTORM = 'PhpStorm product colorway'
    BC_CLION = 'CLion product colorway'
    BC_DATAGRIP = 'DataGrip product colorway'
    BC_APPCODE = 'AppCode product colorway'
    BC_GOLAND = 'GoLand product colorway'
    BC_RESHARPER = 'ReSharper product colorway'
    BC_RESHARPER_C = 'ReSharper C++ product colorway'
    BC_DOTCOVER = 'dotCover product colorway'
    BC_DOTMEMORY = 'dotMemory product colorway'
    BC_DOTPEEK = 'dotPeek product colorway'
    BC_DOTTRACE = 'dotTrace product colorway'
    BC_RIDER = 'Rider product colorway'
    BC_TEAMCITY = 'TeamCIty product colorway'
    BC_YOUTRACK = 'YouTrack product colorway'
    BC_UPSOURCE = 'Upsource product colorway'
    BC_HUB = 'Hub product colorway'
    BC_KOTLIN = 'Kotlin product colorway'
    BC_MONO = 'Mono product colorway'
    BC_MPS = 'MPS product colorway'
    BC_IDEA_EDU = 'Intellij IDEA Edu product colorway'
    BC_PYCHARM_EDU = 'PyCharm EDU product colorway'
    BC_DATASPELL = 'DataSpell product colorway'
    BC_QODANA = 'Qodana product colorway'
    BC_DATALORE = 'Datalore product colorway'
    BC_CODEWITHME = 'CodeWithMe product colorway'
    APPLELIKERNBW = 'Apple classic rainbow palette '
    VALERACUSTOM = 'Wha?'
    # RANDOM = 'Random one from 993 colorways'


class PostFXParams(BaseModel):
    dither_strength: NonNegativeFloat = 0.
    color_map: FrameColorMap = FrameColorMap.BC_SPACE
    flat_colors: bool = True


class AnimationFunction(BaseEnum):
    DEFAULT = 'Default animation'
    BERNOULLI = 'Bernoulli animation'


class AnimationParams(BaseModel):
    func: AnimationFunction = AnimationFunction.BERNOULLI
    fps: float = 60
    length: float = 30
    bitrate: float = 20


class RendererParams(BaseModel):
    model: ModelParams = Field(default_factory=ModelParams)
    input: InputSpaceParams = Field(default_factory=InputSpaceParams)
    post_fx: PostFXParams = Field(default_factory=PostFXParams)
    animation: AnimationParams = Field(default_factory=AnimationParams)
