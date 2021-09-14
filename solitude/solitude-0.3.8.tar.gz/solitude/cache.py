import json
import logging
import tempfile
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Type


class CacheData(ABC):
    DEFAULT_EXPIRATION_TIME = 1209600  # 2 weeks expressed in secs

    def __init__(self, timestamp: Optional[int] = None):
        self.timestamp = int(
            timestamp if timestamp is not None else time.time()
        )

    @abstractmethod
    def to_dict(self) -> Dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls: Type, dic: Dict) -> "CacheData":
        pass


class Cache(object):
    def __init__(self, data_class: Type[CacheData], file_name: Path):
        self._logger = logging.getLogger("Cache")
        self.__cache: Dict[str, CacheData] = {}
        self._file_name = file_name
        self.__data_class = data_class
        self._load()

    def _load(self):
        self.__cache.clear()
        if not self._file_name.resolve().is_file():
            self._logger.debug(f"{self._file_name} does not exists.")
            return
        try:
            with open(self._file_name, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as ex:
            self._logger.error(
                f"Error reading the Cache file (JSONDecodeError) : {self._file_name}"
            )
            self._logger.debug(f"{ex}")
            return
        for key, value in data.items():
            self.__cache[key] = self.__data_class.from_dict(dic=value)
        self._logger.debug(
            f"Read {len(self)} cached {self.__data_class} items"
        )

    def update(self, key: str, value: CacheData):
        self.__cache[key] = value
        self._save()

    def delete(self, key: str):
        if key in self.__cache:
            del self.__cache[key]
            self._save()

    def __getitem__(self, key: str) -> CacheData:
        return self.__cache[key]

    def __len__(self) -> int:
        return len(self.__cache)

    def __contains__(self, key: str) -> bool:
        return key in self.__cache

    def _save(self):
        self._file_name.parent.mkdir(parents=True, exist_ok=True)
        data = {k: v.to_dict() for k, v in self.__cache.items()}
        self._logger.debug(
            f"Writing {self.__data_class} items to cache: {self._file_name}"
        )
        json_write_atomic(fname=self._file_name, data=data)

    def cleanup(
        self, expiration_time: int = CacheData.DEFAULT_EXPIRATION_TIME
    ):
        current_time = time.time()
        initial_size = len(self.__cache)
        for key in list(self.__cache.keys()):
            if current_time - self.__cache[key].timestamp >= expiration_time:
                del self.__cache[key]
        cleaned_items = initial_size - len(self.__cache)
        if cleaned_items > 0:
            self._logger.debug(
                f"Removed {cleaned_items} expired {self.__data_class} items from cache."
            )
            self._save()


def json_write_atomic(fname: Path, data: Any):
    # specify dir to ensure same filesystem...
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, dir=str(fname.parent)
    ) as f:
        tmp_filename = Path(f.name)
        json.dump(data, f, indent=4)
    # atomic write with replacement (most of the time)
    tmp_filename.replace(fname)
