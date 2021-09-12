from abc import *

class IDownloader:
    @abstractmethod
    def download(self, line):
        pass

    @property
    @abstractmethod
    def DANMU_TYPE(self):
        pass

    @property
    @abstractmethod
    def DANMU_EXTNAME(self):
        pass

    @property
    @abstractmethod
    def DANMU_LIST_EXTNAME(self):
        pass