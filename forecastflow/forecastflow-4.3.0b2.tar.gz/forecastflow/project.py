import tempfile
from typing import IO, List, Dict, Optional, Union

import pandas

from .api import _v3
from .data_source import DataSource
from .enums import DataSourceLabel, FileType
from .model import Model
from .user import User


class Project:
    """
    ForecastFlow project class
    """

    def __init__(self, user: 'User', project_id: str, team_id: Optional[str] = None):
        """
        Instantiate Project object with given project ID

        Args:
            user:
                Owner of project.

            project_id:
                Project ID you want to open.
        """
        self.user = user
        self.project_id = project_id
        self.team_id = team_id
        self._data_sources: Dict[str, 'DataSource'] = {}
        self._models: Dict[str, 'Model'] = {}

    @property
    def _document(self) -> dict:
        doc = _v3.get_project_info(
            id_token=self.user.id_token, team_id=self.team_id, pid=self.pid
        )
        return doc

    def update(self):
        document = self._document
        self.name = document['name']

    def create_data_source(
        self,
        data: Union['pandas.DataFrame', Union[List[str], List[IO]]],
        name: str,
        label: 'DataSourceLabel',
        description: Optional[str] = None,
        filetype: Optional['FileType'] = None,
        skip_profile: bool = False,
    ) -> 'DataSource':
        """
        Upload file to ForecastFlow and create data source.

        Args:
            data:
                pandas.DataFrame or list of files to upload.

            name:
                Name of data source.

            label:
                Label of data.

            description:
                Description of data source.

            filetype:
                Data file format

        Returns:
            New data source created.
        """
        if isinstance(data, pandas.DataFrame):
            if filetype is None:
                filetype = FileType.CSV
            if not name.endswith('.csv'):
                name += '.csv'  # TODO: Currently file extension is needed. Store data type in database.
            return self._create_data_source_from_data_frame(
                df=data,
                filetype=filetype,
                name=name,
                label=label,
                description=description,
                skip_profile=skip_profile,
            )
        else:
            if filetype is None:
                raise ValueError('filetype should be specified')
            else:
                return self._create_data_source_from_files(
                    files=data,
                    filetype=filetype,
                    name=name,
                    label=label,
                    description=description,
                    skip_profile=skip_profile,
                )

    def _create_data_source_from_data_frame(
        self,
        df: 'pandas.DataFrame',
        filetype: 'FileType',
        name: str,
        label: 'DataSourceLabel',
        description: Optional[str] = None,
        skip_profile: bool = False,
    ) -> 'DataSource':
        if filetype != FileType.CSV:
            raise ValueError(
                f'{filetype} is not supported for uploading `pandas.DataFrame`.'
            )
        with tempfile.TemporaryDirectory() as tempdir:
            path = f'{tempdir}/temp.csv'
            df.to_csv(path)
            return self._create_data_source_from_files(
                files=[path],
                filetype=filetype,
                name=name,
                label=label,
                description=description,
                skip_profile=skip_profile,
            )

    def _create_data_source_from_files(
        self,
        files: Union[List[str], List[IO]],
        filetype: 'FileType',
        name: str,
        label: 'DataSourceLabel',
        description: Optional[str] = None,
        skip_profile: bool = False,
    ) -> 'DataSource':
        did = _v3.create_data_source_from_files(
            id_token=self.user.id_token,
            team_id=self.team_id,
            pid=self.project_id,
            files=files,
            filetype=filetype,
            name=name,
            label=label,
            description=description,
        )
        self._data_sources[did] = DataSource(self, did)
        if not skip_profile:
            self._data_sources[did].profile()
        return self._data_sources[did]

    def get_data_source(self, data_source_id) -> 'DataSource':
        """
        Get data source with given data source id.

        Args:
            data_source_id:
                ID of data source you want to open.

        Returns:
            ForecastFlow data source object with given data source ID.
        """
        if data_source_id not in self._data_sources:
            d = DataSource(self, data_source_id)
            self._data_sources[data_source_id] = d
        return self._data_sources[data_source_id]

    def get_model(self, model_id) -> 'Model':
        """
        Get model with given model ID.

        Args:
            model_id:
                ID of model you want to open.

        Returns:
            ForecastFlow model object with given model ID.
        """
        if model_id not in self._models:
            self._models[model_id] = Model(self, model_id)
        return self._models[model_id]

    @property
    def pid(self) -> str:
        return self.project_id
