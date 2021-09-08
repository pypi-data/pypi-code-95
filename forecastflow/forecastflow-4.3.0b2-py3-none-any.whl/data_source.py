import logging
import time
from typing import TYPE_CHECKING, Optional

from .enums import Status
from .exceptions import OperationFailed
from .model import Model
from .api import _v3

if TYPE_CHECKING:
    from . import Project, User
    from .training import TrainingSettings

logger = logging.getLogger(__name__)


class DataSource:
    """
    ForecastFlow data source class
    """

    def __init__(self, project: 'Project', data_source_id: str):
        """
        Instantiate object with given data source ID

        Args:
            project:
                Project which data source belong to.

            data_source_id:
                ID of data source you want to open.
        """
        self.project = project
        self.data_source_id = data_source_id
        self.name = None
        self.status = None
        self.update()

    @property
    def _document(self) -> dict:
        doc = _v3.get_data_source_info(
            id_token=self.user.id_token,
            team_id=self.project.team_id,
            pid=self.pid,
            did=self.did,
        )
        return doc

    @property
    def did(self) -> str:
        return self.data_source_id

    def update(self):
        """
        Update name, status
        """
        document = self._document

        self.name = document['name']
        self.status = Status(document['status'] or Status.WAITING.value)
        if self.status == Status.IN_PROGRESS:
            logger.info(f"Profiling '{self.name}': {self.status.value}")

    @property
    def user(self) -> 'User':
        return self.project.user

    @property
    def uid(self) -> str:
        return self.project.user.user_id

    def wait_until_done(self):
        """
        Wait until ForecastFlow finish profiling.
        """
        while self.status != Status.COMPLETED and self.status != Status.ERROR:
            self.update()
            time.sleep(5)

        if self.status == Status.ERROR:
            document = self._document
            error_info = document.get('errorInfo')
            if error_info is None:
                raise OperationFailed("Profiler quit with Error")
            else:
                raise OperationFailed(
                    f"{error_info['message']}\n"
                    f"error_log_id: {error_info['errorLogId']}"
                )

    def create_model(
        self,
        train_settings: 'TrainingSettings',
        name: str,
        test_frac: Optional[float] = None,
        test_data_source: Optional['DataSource'] = None,
        description: str = '',
    ):
        """
        Train model with this datasource.

        Args:
            train_settings:
                Object of ClassifierTrainingSettings or RegressorTrainingSettings

            name:
                Name of model.

            test_frac:
                Fraction of rows in train that will belong to the test.
                Round off to two decimal places.

            test_data_source:
                Data to test with.

            description:
                Description of model.

        Returns:
            ForecastFlow model object.
        """
        self.wait_until_done()
        if test_data_source:
            test_data_source.wait_until_done()
        test_pid = test_data_source.pid if test_data_source else None
        test_did = test_data_source.did if test_data_source else None
        mid = _v3.create_model(
            id_token=self.user.id_token,
            team_id=self.project.team_id,
            name=name,
            train_settings=train_settings,
            train_pid=self.pid,
            train_did=self.data_source_id,
            test_pid=test_pid,
            test_did=test_did,
            test_frac=test_frac,
            description=description,
        )
        return Model(project=self.project, model_id=mid)

    def profile(self):
        if self.status == Status.WAITING:
            _v3.profile(
                id_token=self.user.id_token,
                team_id=self.project.team_id,
                pid=self.pid,
                did=self.did,
            )

    @property
    def pid(self) -> str:
        return self.project.project_id
