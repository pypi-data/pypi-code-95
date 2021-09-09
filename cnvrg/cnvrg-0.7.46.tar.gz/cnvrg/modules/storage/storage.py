from cnvrg.modules.base_module import CnvrgBase
from cnvrg.helpers.apis_helper import download_file
from cnvrg.modules.cnvrg_files import CnvrgFiles
from cnvrg.modules.errors import NotImplementedError
from cnvrg.modules import UnknownStsError
from cnvrg.helpers.crypto_helpers import decrypt
import os
from typing import Dict, List
import click
from cnvrg.helpers.parallel_helper import safe_parallel
from cnvrg.helpers import log_error


class Storage(CnvrgBase):
    def __init__(self, element: CnvrgFiles, working_dir: str, sts_path: str):
        self.element = element
        self.working_dir = working_dir
        self.init_sts(sts_path)
        self.conflicts = []

    def init_sts(self, sts_path):
        sts_content = download_file(sts_path)
        if not sts_content:
            raise UnknownStsError("Cant find sts")
        self.key, self.iv = sts_content.split("\n")

    def decrypt(self, text):
        return decrypt(self.key, self.iv, text)

    def decrypt_dict(self, props: Dict, keys: List = None):
        return {k: decrypt(self.key, self.iv, v) if k in keys else v for k,v in props.items()}

    def status(self):
        pass


    def download_file(self, local_path: str, storage_path: str):
        raise NotImplementedError

    def clone_commit(self, commit, **kwargs):
        self.download_files(self.element.fetch_commit(commit).get("blobs"))

    def download_single_file(self, file):
        local_p, storage_p = self.decrypt(file["local_path"]), self.decrypt(file["storage_path"])
        if local_p in self.conflicts:
            local_p = local_p + ".conflict"
        local_p = os.path.join(self.working_dir, local_p)
        self.get_dir(local_p)
        ##if file, download it
        if not local_p.endswith("/"): self.download_file(local_p, storage_p)

    def upload_single_file(self, file):
        if file.get("decrypted"):
            local_p, storage_p = file.get("local_path"), file.get("storage_path")
        else:
            local_p, storage_p = self.decrypt(file["local_path"]), self.decrypt(file["storage_path"])
        local_p = os.path.join(self.working_dir, local_p)
        self.upload_file(local_p, storage_p)


    def download_dirs(self, dirs: List):
        try:
            safe_parallel(self.download_single_file, dirs)
        except Exception as e:
            log_error(e)
            raise e

    def download_files(self, files: List, conflicts: List=None):
        try:
            self.conflicts = conflicts or []
            safe_parallel(self.download_single_file, files, progressbar={"desc": "Downloading files"})
            self.conflicts = []
        except Exception as e:
            log_error(e)
            click.secho("Cant download all files")
            raise e

    def delete_files(self, files: List, conflicts: List=None):
        conflicts = conflicts or []
        for file in files:
            if file in conflicts:
                src_name = os.path.join(self.working_dir, file)
                dest_name = src_name + ".deleted"
                os.rename(src_name, dest_name)
            else:
                os.remove(os.path.join(self.working_dir, file))

    def get_dir(self, filename):
        dirname = os.path.dirname(filename)
        if os.path.exists(dirname):
            return
        os.makedirs(dirname, exist_ok=True)

    def upload_files(self, files: List):
        try:
            safe_parallel(self.upload_single_file, files, progressbar={"desc": "Uploading files"})
        except Exception as e:
            raise e


    def upload_file(self, local_path: str, storage_path: str):
        raise NotImplementedError
