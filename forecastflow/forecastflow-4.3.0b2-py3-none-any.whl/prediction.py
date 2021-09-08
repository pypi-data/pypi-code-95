import logging
import time
from io import BytesIO
from typing import TYPE_CHECKING

import pandas as pd

from .api import _v3
from .enums import FileType, Status
from .exceptions import ForecastFlowError, InvalidID, OperationFailed
from . import _storage

if TYPE_CHECKING:
    from . import Model, Project, User

logger = logging.getLogger(__name__)


class Prediction:
    """
    ForecastFlow prediction object
    """

    def __init__(self, model: 'Model', prediction_id: str):
        """
        Instantiate object with given prediction ID.

        Args:
            model:
                Model which makes this predict.

            prediction_id:
                ID of prediction you want to open.
        """
        self.model = model
        self.prediction_id = prediction_id
        self.name = None
        self.status = None
        self._document = None
        self.update()

    def get_result(self) -> pd.DataFrame:
        """
        Download the result from ForecastFlow.

        Returns:
            result with primary key and predicted values.
        """
        self.wait_until_done()
        urls = [f['downloadUrl'] for f in self._document['files']]
        filetype = self.filetype
        df_list = []
        for url in urls:
            with BytesIO() as f:
                _storage.download(
                    url,
                    f,
                )
                f.seek(0)
                if filetype == FileType.CSV:
                    df_list.append(pd.read_csv(f))
                elif filetype == FileType.TSV:
                    df_list.append(pd.read_csv(f, delimiter='\t'))
                elif filetype == FileType.PARQUET:
                    df_list.append(pd.read_parquet(f))
                else:
                    raise ForecastFlowError(f'{filetype} not supported.')
        return pd.concat(df_list, ignore_index=True)

    @property
    def project(self) -> 'Project':
        return self.model.project

    @property
    def rid(self) -> str:
        return self.prediction_id

    @property
    def filetype(self) -> 'FileType':
        return FileType(self._document.get('type', FileType.CSV))

    def update(self):
        """
        update name, status
        """
        self._document = _v3.get_prediction_info(
            id_token=self.user.id_token,
            team_id=self.project.team_id,
            pid=self.project.pid,
            rid=self.rid,
        )

        if self._document['mid'] != self.model.model_id:
            raise InvalidID('Given Prediction ID is not for this model')

        self.name = self._document['name']
        self.status = Status(self._document['status'])

        logger.info(f"Prediction '{self.name}': {self.status.value}")

    @property
    def user(self) -> 'User':
        return self.model.project.user

    def wait_until_done(self):
        """
        Wait until ForecastFlow finish prediction.
        """
        while self.status != Status.COMPLETED and self.status != Status.ERROR:
            self.update()
            time.sleep(5)

        if self.status == Status.ERROR:
            document = self._document
            error_info = document.get('errorInfo')
            if error_info is None:
                raise OperationFailed("Predictor quit with Error")
            else:
                raise OperationFailed(
                    f"{error_info['message']}\n"
                    f"error_log_id: {error_info['errorLogId']}"
                )
