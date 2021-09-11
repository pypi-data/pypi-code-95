from abc import *


class IConverter:
    @abstractmethod
    def converter(self, data):
        pass

    @property
    @abstractmethod
    def DANMU_TYPE_SRC(self):
        pass

    @property
    @abstractmethod
    def DANMU_TYPE_DST(self):
        pass

    @property
    @abstractmethod
    def DANMU_EXTNAME_SRC(self):
        pass

    @property
    @abstractmethod
    def DANMU_EXTNAME_DST(self):
        pass