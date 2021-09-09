from abc import ABC, abstractmethod
from functools import cached_property
from typing import Union, Callable


class User(ABC):
    __slots__ = ('_uid',)

    def __init__(self, uid: Union[int, str], user_data_getter: Callable = None):
        self._uid = uid
        self._visual_name = None
        # self._user_data = None
        self._user_data_getter = user_data_getter

    def set_user_data_getter(self, getter_function: Callable):
        self._user_data_getter = getter_function

    @property
    def uid(self) -> Union[int, str]:
        return self._uid

    @cached_property
    def _data(self):
        return self._user_data_getter()

    @property
    @abstractmethod
    def data(self):
        """Must return self._data"""
        return self._data

    @cached_property
    def visual_name(self) -> str: return self.get_visual_name()

    @cached_property
    def short_name(self) -> str: return self.get_short_name()

    @abstractmethod
    def get_visual_name(self) -> str: pass

    @abstractmethod
    def get_short_name(self) -> str: pass

    @property
    @abstractmethod
    def id_url(self) -> str:
        pass
