import logging
from typing import Callable, TYPE_CHECKING

import pandas as pd

from .type import PrepType

if TYPE_CHECKING:
    from typing import List

    import forecastflow

__all__ = ['make_prediction_schema']

logger = logging.getLogger(__name__)


def make_prediction_schema(
    user: 'forecastflow.User', project_id: str, model_id: str
) -> Callable[[], 'pd.DataFrame']:
    """
    Make schema for Tableau Prep's get_output_schema function for prediction

    Args:
        user:
            ForecastFlow User object

        project_id:
            ForecastFlow Project ID

        model_id:
            ForecastFlow Model ID

    Returns:
        A function which returns a schema for Tableau Prep.
    """

    def _get_prediction_schema():
        model = user.get_project(project_id).get_model(model_id)
        schema_dict = model.prediction_schema.copy()

        for key in schema_dict:
            type_str = schema_dict[key]
            if type_str == 'float':
                prep_type = PrepType.DECIMAL
            elif type_str == 'int':
                prep_type = PrepType.INT
            elif type_str == 'str':
                prep_type = PrepType.STR
            elif type_str == 'bool':
                prep_type = PrepType.BOOL
            else:
                raise ValueError(f"Unsupported type '{type_str}'.")
            schema_dict[key] = [prep_type.value]

        prep_schema = pd.DataFrame(schema_dict)
        logger.info(f'prediction schema:\n{prep_schema}')
        return prep_schema

    return _get_prediction_schema


def __dir__() -> 'List[str]':
    return __all__
