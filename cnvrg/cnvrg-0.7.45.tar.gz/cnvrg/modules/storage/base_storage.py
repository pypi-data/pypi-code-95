import os

from typing import Dict, List
from cnvrg.modules import UnknownStsError
from cnvrg.modules.base_module import CnvrgBase
from cnvrg.modules.cnvrg_files import CnvrgFiles
from cnvrg.helpers.crypto_helpers import decrypt
from cnvrg.helpers.apis_helper import download_file
from typing import Dict, List
import os


class BaseStorage(CnvrgBase):
    def __init__(self, element: CnvrgFiles, working_dir: str, sts_path: str):
        self.element = element
        self.working_dir = working_dir

        self.sts_local_file = None
        self.key = None
        self.iv = None
        self.init_sts(sts_path)

        self.conflicts = []

    def init_sts(self, sts_path):
        sts_local_file = os.path.join(os.path.expanduser("~"), ".cnvrg", ".sts")
        sts_file = download_file(sts_path, sts_local_file)

        if not sts_file or not os.path.exists(sts_file):
            raise UnknownStsError("Cant find sts")

        with open(sts_file) as content:
            self.sts_local_file = sts_local_file
            if not content:
                raise UnknownStsError("Cant find sts")
            sts_content = content.read().split("\n")
            self.key = sts_content[0]
            self.iv = sts_content[1]

    def decrypt(self, text):
        return decrypt(self.key, self.iv, text)

    def decrypt_dict(self, props: Dict, keys: List = None):
        return {k: decrypt(self.key, self.iv, v) if k in keys else v for k, v in props.items()}

