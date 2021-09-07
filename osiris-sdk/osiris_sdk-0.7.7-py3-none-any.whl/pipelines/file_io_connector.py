"""
A source to download files from Azure Datalake
"""
import os
import json
from datetime import timedelta, datetime
from typing import List, Optional, Generator, Dict
import pandas as pd

from apache_beam.io import OffsetRangeTracker, iobase
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.filedatalake import FileSystemClient, PathProperties

from .azure_data_storage import Dataset
from ..core.azure_client_authorization import ClientAuthorization


class FileBatchController:
    """
    Used to find the next batch of files to process.

    This batch controller can be used in two different ways:
    1. You can initialize it with an ingest time. In this case it will process files from the current hour and the
    previous hour no matter if they have been processed before or not. It will also ignore the max_files argument.
    2. If you don't initialize it with an ingest time, it will use a state which it will store in a file (STATE_FILE)
    on the dataset. This state will contain the last modified timestamp of the last file it processed. Next time
    it runs it will only process files newer than this timestamp and according to the max_files argument.
        - If you use this approach you need to call close() after the pipeline to save the state otherwise it will
        keep processing the same files again and again.
        - First time it runs it will use the current UTC time.
   """

    STATE_FILE = 'transformation_state.json'

    # pylint: disable=too-many-arguments
    def __init__(self,
                 client_auth: ClientAuthorization,
                 account_url: str,
                 filesystem_name: str,
                 guid: str,
                 ingest_time: datetime = None,
                 max_files: int = 10):

        if None in [client_auth, account_url, filesystem_name, guid]:
            raise TypeError

        self.client_auth = client_auth
        self.account_url = account_url
        self.filesystem_name = filesystem_name
        self.guid = guid
        self.has_ingest_time = ingest_time is not None
        self.file_paths = self.__get_file_paths(ingest_time, max_files, self.client_auth.get_local_copy())

    def __get_file_paths(self, ingest_time: Optional[datetime], max_files: int,
                         local_client_auth: ClientAuthorization) -> List[PathProperties]:
        with FileSystemClient(self.account_url, self.filesystem_name,
                              credential=local_client_auth.get_credential_sync()) as filesystem_client:

            if ingest_time is None:
                return self.__get_paths_since_last_run(filesystem_client, max_files)

            return self.__get_paths_on_basis_of_ingest_time(filesystem_client, ingest_time)

    def __get_paths_on_basis_of_ingest_time(self, filesystem_client, ingest_time: datetime) -> List[PathProperties]:
        folder_path1 = f'{self.guid}/year={ingest_time.year}/month={ingest_time.month:02d}/' + \
                       f'day={ingest_time.day:02d}/hour={ingest_time.hour:02d}'

        prev_hour = ingest_time - timedelta(hours=1)
        folder_path2 = f'{self.guid}/year={prev_hour.year}/month={prev_hour.month:02d}/day={prev_hour.day:02d}' + \
                       f'/hour={prev_hour.hour:02d}'

        paths = []
        paths += self.__get_file_paths_from_folder(folder_path1, filesystem_client)
        paths += self.__get_file_paths_from_folder(folder_path2, filesystem_client)

        return paths

    def __get_paths_since_last_run(self, filesystem_client: FileSystemClient, max_files: int) -> List[PathProperties]:
        state = self.__retrieve_transformation_state(filesystem_client)

        last_successful_run = datetime.strptime(state['last_successful_run'], '%Y-%m-%dT%H:%M:%S')
        now = datetime.utcnow()
        time_range = pd.date_range(last_successful_run, now, freq='H')
        paths = []

        for timeslot in time_range:
            folder_path = f'{self.guid}/year={timeslot.year}/month={timeslot.month:02d}/day={timeslot.day:02d}' + \
                          f'/hour={timeslot.hour:02d}'

            paths.extend(self.__get_file_paths_from_folder(folder_path, filesystem_client))

            if len(paths) > max_files:
                break

        paths_return = paths[:max_files]

        for path in paths_return:
            # Set 'processing' tag when the file is getting processed
            filesystem_client.get_file_client(path.name).set_metadata({'status': 'processing'})

        return paths_return

    def __retrieve_transformation_state(self, filesystem_client: FileSystemClient) -> Dict:
        with filesystem_client.get_file_client(f'{self.guid}/{self.STATE_FILE}') as file_client:
            try:
                state = file_client.download_file().readall()
                return json.loads(state)
            except ResourceNotFoundError:
                return {'last_successful_run': '1970-01-01T00:00:00'}

    def __save_transformation_state(self, filesystem_client: FileSystemClient, state: Dict):
        with filesystem_client.get_file_client(f'{self.guid}/{self.STATE_FILE}') as file_client:
            json_data = json.dumps(state)
            file_client.upload_data(json_data, overwrite=True)

    @staticmethod
    def __get_file_paths_from_folder(folder_path: str, file_system_client: FileSystemClient) -> List[PathProperties]:
        try:
            paths = list(file_system_client.get_paths(path=folder_path))
            unprocessed_files = []

            for path in paths:
                processed_file_metadata = file_system_client.get_file_client(path.name).get_file_properties().metadata
                # Only append files which does not have the status=processed or processing tag
                # NOTE: some "processing" files might not have run if transformation fails. Remove the tag, then rerun

                if 'status' not in processed_file_metadata:
                    unprocessed_files.append(path)
                elif processed_file_metadata['status'] not in ['processed', 'processing']:
                    unprocessed_files.append(path)

            return unprocessed_files
        except ResourceNotFoundError:
            return []

    def get_batch(self) -> List[str]:
        """
        Get the next batch to process.
        """
        # The list of self.file_paths is of type FileProperties and we want to return a list of paths as strings
        file_path_list = ['/'.join(file_path.name.split('/')[1:]) for file_path in self.file_paths]

        return file_path_list

    def save_state(self):
        """
        Updates the transformation state file after a successful run. Its important this method gets called
        after the pipeline has run or else the datasource will keep processing already processed files.
        """

        # If ingest time its set, we will not update or use the state. Close() should not be called in this
        # situation.
        if self.has_ingest_time:
            return

        local_client_auth = self.client_auth.get_local_copy()

        with FileSystemClient(self.account_url, self.filesystem_name,
                              credential=local_client_auth.get_credential_sync()) as filesystem_client:
            state = self.__retrieve_transformation_state(filesystem_client)

            # state file doesn't exist. We create a fresh one.
            if not state:
                state = {}

            if len(self.file_paths):
                for path in self.file_paths:
                    # Set 'processed' tag in the metadata of the file
                    filesystem_client.get_file_client(path.name).set_metadata({'status': 'processed'})

                # Get the date from the folder structure of the last file it has processed
                date_elements = self.file_paths[-1].name.split('/')[1:-1]
                date_str = ''.join([x.split('=')[1] for x in date_elements])

                latest_folder_date = datetime.strptime(date_str, '%Y%m%d%H').isoformat()
                state['last_successful_run'] = latest_folder_date
                self.__save_transformation_state(filesystem_client, state)


class DatalakeFileSource(iobase.BoundedSource):  # noqa
    """
    A Class to download files from Azure Datalake

    Class takes a list of paths to process in the batch.
    """

    # pylint: disable=too-many-arguments
    def __init__(self,
                 dataset: Dataset,
                 file_paths: List[str]):

        if None in [dataset, file_paths]:
            raise TypeError

        self.dataset = dataset
        self.file_paths = file_paths

    def estimate_size(self) -> int:
        """
        Returns the number of files to process
        """
        return len(self.file_paths)

    def get_range_tracker(self, start_position: Optional[int], stop_position: Optional[int]) -> OffsetRangeTracker:
        """
        Creates and returns an OffsetRangeTracker
        """
        if start_position is None:
            start_position = 0
        if stop_position is None:
            stop_position = len(self.file_paths)

        return OffsetRangeTracker(start_position, stop_position)

    def read(self, range_tracker: OffsetRangeTracker) -> Optional[Generator]:
        """
        Returns the content of the next file
        """
        for i in range(range_tracker.start_position(), range_tracker.stop_position()):
            if not range_tracker.try_claim(i):
                return

            path = self.file_paths[i]
            content = self.dataset.read_file(path)

            yield content

    def split(self,
              desired_bundle_size: int,
              start_position: Optional[int] = None,
              stop_position: Optional[int] = None) -> iobase.SourceBundle:
        """
        Splits a Tracker
        """
        if start_position is None:
            start_position = 0
        if stop_position is None:
            stop_position = len(self.file_paths)

        bundle_start = start_position
        while bundle_start < stop_position:
            bundle_stop = min(stop_position, bundle_start + desired_bundle_size)
            yield iobase.SourceBundle(
                weight=(bundle_stop - bundle_start),
                source=self,
                start_position=bundle_start,
                stop_position=bundle_stop)
            bundle_start = bundle_stop


class DatalakeFileSourceWithFileName(DatalakeFileSource):  # noqa
    """
    A Class to download files from Azure Datalake with file name.
    """

    def read(self, range_tracker: OffsetRangeTracker) -> Optional[Generator]:
        """
        Returns the content of the next file.
        """
        for i in range(range_tracker.start_position(), range_tracker.stop_position()):
            if not range_tracker.try_claim(i):
                return

            path = self.file_paths[i]
            content = self.dataset.read_file(path)

            file_name = os.path.basename(path)

            yield file_name, content
