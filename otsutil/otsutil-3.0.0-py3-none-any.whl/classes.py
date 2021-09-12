import base64
import pickle

from pathlib import Path
from typing import Any, Union

from otsutil.funcs import setup_path


class ObjectSaver:
    """オブジェクトを保存するファイルを扱うクラスです。
    """
    def __init__(self, file: Union[str, Path]):
        """オブジェクトを保存するファイルを準備します。

        Args:
            file (Union[str, Path]): オブジェクトを保存するファイルです。
        """
        self.__file = setup_path(file)
        self.__data = None
        self.__loaded = False
        if self.__file.exists():
            self.load_file()

    @staticmethod
    def dumps(obj: Any) -> str:
        """オブジェクトのpickle文字列を取得します。

        Args:
            obj (Any): pickle文字列を取得したいオブジェクトです。

        Returns:
            str: pickle文字列です。
        """
        otb = pickle.dumps(obj, protocol=4)
        return base64.b64encode(otb).decode('utf-8')

    @staticmethod
    def loads(pickle_str: str) -> Any:
        """pickle文字列をオブジェクト化します。

        Args:
            pickle_str (str): pickle文字列です。

        Returns:
            Any: 復元されたオブジェクトです。
        """
        stb = base64.b64decode(pickle_str.encode())
        return pickle.loads(stb)

    def load_file(self) -> Any:
        """ファイルに保存されているデータを読み込み、取得します。

        Returns:
            Any: ファイルに保存されていたオブジェクトです。
        """
        if not self.__loaded:
            with open(self.__file, 'r', encoding='utf-8') as f:
                self.__data = self.loads(f.read())
            self.__loaded = True
        return self.__data

    def save_file(self, obj: Any) -> bool:
        """ファイルにobjを保存します。

        また、loadメソッドで取得できるオブジェクトを更新します。

        Args:
            obj (Any): 保存したいオブジェクトです。

        Returns:
            bool: 保存の成否です。
        """
        try:
            bts = self.dumps(obj)
            with open(self.__file, 'w', encoding='utf-8') as f:
                f.write(bts)
            self.__data = obj
            return True
        except Exception as e:
            return False


class OtsuNoneType:
    """Noneが返るのが正常な場合など、異常なNoneを表す場合に使用するクラスです。
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return 'OtsuNone'

    def __bool__(self) -> bool:
        return False


OtsuNone = OtsuNoneType()
