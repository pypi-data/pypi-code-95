from .base_files_connector import BaseFileConnector
from cnvrg.modules.dataset import Dataset
from cnvrg.helpers.apis_helper import url_join
DATASET_TYPE_QUERY = "type_query"
DATASET_TYPE_DATASET = "type_dataset"
class DatasetConnector(BaseFileConnector):

    @staticmethod
    def key_type():
        return "dataset"

    def __init__(self, dataset=None, working_dir=None, query=None):
        super(DatasetConnector, self).__init__(dataset)
        self.__type = DATASET_TYPE_DATASET
        self.__query = query
        self.__files = None
        self.__dataset = Dataset(url_join(self._org, self._data_connector), working_dir=working_dir)

    @property
    def _dataset_type(self):
        return DATASET_TYPE_QUERY if self.__query else DATASET_TYPE_DATASET


    @property
    def working_dir(self):
        return self.__dataset.get_working_dir()

    def __len__(self):
        if not self.__files: self.__fetch()
        return len(self.__files)

    def __fetch(self):
        if self._dataset_type == DATASET_TYPE_DATASET:
            self.__files = self._files_callback(self.__dataset.fetch_all_files())
        elif self._dataset_type == DATASET_TYPE_QUERY:
            self.__files = self._files_callback(self.__dataset.get_query(self.__query))

    def __getitem__(self, item):
        return self.__dataset.download_file(self.__files[item])