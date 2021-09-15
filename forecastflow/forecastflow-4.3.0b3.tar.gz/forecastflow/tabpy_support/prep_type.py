import platform
import warnings

from forecastflow.satellite.tableau import prep

warnings.filterwarnings("module", category=DeprecationWarning, module=__name__)


if ('3', '7') > platform.python_version_tuple():
    PrepType = prep.PrepType


def __getattr__(name):
    if name in __all__:
        warnings.warn(
            f'{__name__} is deprecated, use {prep.__name__} instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(prep, name)
    else:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


__all__ = ['PrepType']
