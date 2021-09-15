import warnings
from typing import TYPE_CHECKING, Callable

from forecastflow.satellite.tableau import prep

if TYPE_CHECKING:
    import forecastflow
    import pandas as pd

warnings.filterwarnings("module", category=DeprecationWarning, module=__name__)


def make_prediction_schema(
    user: 'forecastflow.User', project_id: str, model_id: str
) -> Callable[[], 'pd.DataFrame']:
    warnings.warn(
        f'{__name__} is deprecated, use {prep.__name__} instead.',
        DeprecationWarning,
        stacklevel=2,
    )
    return prep.make_prediction_schema(
        user=user, project_id=project_id, model_id=model_id
    )


__all__ = ['make_prediction_schema']
