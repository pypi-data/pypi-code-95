from cnvrg.modules.cnvrg_files import CnvrgFiles
import cnvrg.helpers.param_build_helper as param_build_helper
import cnvrg.helpers.config_helper as config_helper
from cnvrg.modules.errors import CnvrgError
from cnvrg.modules.storage import storage_factory
from cnvrg.helpers.error_catcher import suppress_exception
import cnvrg.helpers.data_working_dir_helper as data_working_dir_helper
import cnvrg.helpers.apis_helper as apis_helper
import os.path
from typing import AnyStr
import cnvrg.helpers.config_helper as config_helper

class Dataset(CnvrgFiles):
    def __init__(self, dataset=None, dataset_url=None, working_dir=None):
        super(Dataset, self).__init__()
        working_dir = data_working_dir_helper.init_data_working_dir(working_dir)
        if dataset_url:
            owner_slug, project_slug = Dataset.get_owner_and_project_from_url(dataset_url)
        else:
            owner_slug, project_slug = param_build_helper.parse_params(dataset, param_build_helper.DATASET, working_dir=working_dir)
        self.__owner = owner_slug
        self.__dataset = project_slug
        if working_dir is None:
            working_dir = os.curdir
        in_dir = config_helper.is_in_dir(config_helper.CONFIG_TYPE_DATASET, project_slug, working_dir)
        working_dir = os.path.join(working_dir, self.__dataset)
        self._set_working_dir(working_dir, save=False)
        self.storage = None #storage_factory(self, self.get_working_dir())
        if in_dir:
            self._set_working_dir(config_helper.find_config_dir(path=working_dir))
            self.in_dir = True
        elif not self.__dataset or not self.__owner:
            raise CnvrgError("Cant init dataset without params and outside project directory")

    def get_base_url(self):
        return "users/{owner}/datasets/{dataset}".format(owner=self.__owner, dataset=self.__dataset)

    def get_query(self, query_slug: AnyStr, data_dir: AnyStr=None,filter: AnyStr=None):
        return self._fetch_query(query_slug,data_dir,filter)

    def search(self, search: AnyStr,data_dir: AnyStr=None,filter: AnyStr=None):
        return self._search(search,data_dir,filter)

    def get_full_url(self):
        general_config = config_helper.load_generl_config()

        if general_config:
            api_url = general_config[":api"]
        else:
            api_url = os.environ.get("CNVRG_API")

        dataset_full_url = api_url.replace("/api", "/{owner}/datasets/{dataset}".format(owner=self.__owner,
                                                                                        dataset=self.__dataset))
        return dataset_full_url

    @suppress_exception
    def _search(self, search: AnyStr, data_dir: AnyStr=None,filter: AnyStr=None):
        response = apis_helper.post(apis_helper.url_join(self.get_base_url(), "search"), data={"search": search,"working_dir": data_dir,"filter": filter})
        return response.get("files")

    @suppress_exception
    def _fetch_query(self, query_slug: AnyStr, data_dir: AnyStr=None,filter: AnyStr=None):
        response = apis_helper.get(apis_helper.url_join(self.get_base_url(), "queries", query_slug), data={"working_dir": data_dir,"filter": filter})
        return response.get("files")

    # def get_by_query(self, query):
    #     all_files = self.fetch_all_files()
    #     query_files = apis_helper.get(apis_helper.url_join(self.get_base_url(), "search", query))
    #     fullpaths = dict([[x.get("fullpath"), x] for x in query_files.get("results").get("query_files")])
    #     return [{**fullpaths.get(elem.get("fullpath")), **elem} for elem in filter(lambda x: x.get("fullpath") in fullpaths, all_files)]
    #
    #
    # def query(self, query):
    #     all_files = self.fetch_all_files()
    #     query_files = apis_helper.post(apis_helper.url_join(self.get_base_url(), "search"), data={"query": query})
    #     fullpaths = dict([[x.get("fullpath"), x] for x in query_files.get("results").get("files")])
    #     return [{**fullpaths.get(elem.get("fullpath")), **elem} for elem in
    #                     filter(lambda x: x.get("fullpath") in fullpaths, all_files)]

    def fetch_all_files(self):
        return self.get_commit_files()

    @suppress_exception
    def download_file(self, file):
        file_path = os.path.join(self.get_working_dir(), file.get("fullpath"))
        if not os.path.exists(file_path):
            ### if we want s3 / gcp / azure / minio we can add "url" attribute to each file and we will
            # just simply download it.
            if file.get("url"): apis_helper.download_file(file.get("url"), fpath=file_path)
            else:
                if self.storage is None:
                    return
                self.storage.download_single_file(file)
        return file_path

    @suppress_exception
    def get_metadata(self, files: list, commit: str=None):
        resp = apis_helper.post(url=apis_helper.url_join(self.get_base_url(), 'tags'), data={"files": files, "commit": commit})
        return resp.get("data")

    # def pytorch_dataset(self, loader=None):
    #     from torch.utils.data.dataset import Dataset as TorchDataset
    #     class CnvrPytorchDataset(TorchDataset):
    #         'Characterizes a dataset for PyTorch'
    #         def __init__(self, dataset: CnvrgFiles=None):
    #             'Initialization'
    #             self.dataset = dataset
    #             self.files = dict(map(lambda x: [x.get("fullpath"), x], dataset.get_commit_files()))
    #             self.keys = list(self.files.keys())
    #             self.storage = storage_factory(dataset)
    #
    #         def __len__(self):
    #             'Denotes the total number of samples'
    #             return len(self.files.keys())
    #
    #         def __getitem__(self, index):
    #             'Generates one sample of data'
    #             # Select sample
    #             file_def = self.files[self.keys[index]]
    #             file_path = os.path.join(self.dataset.get_working_dir(), file_def.get("fullpath"))
    #             if not os.path.exists(file_path):
    #                 self.storage.download_single_file(file_def)
    #             return file_path if not loader else loader(file_path)
    #
    #     return CnvrPytorchDataset(dataset=self)
