import os
import xxhash
import shutil
import requests
import pathlib
import errno

from http import HTTPStatus
from tqdm import tqdm
from multiprocessing.pool import ThreadPool
from collections import namedtuple
from slai.clients.cli import get_cli_client
from slai.exceptions import DatasetNotFound
from slai.constants import DATASET_IO_THREAD_COUNT

DataSetNode = namedtuple("DataSetNode", "name parent_name hash index")


class DataSet:
    def __init__(self, name, local_path=None, public=False, version=None, create=False):
        self.name = name
        self.local_path = local_path
        self.public = public
        self.create = create
        self.version = version
        self.metatable = {}

        self.cli_client = get_cli_client()

    def add_file(self, file_path, dir=None):
        if not self.local_path:
            raise RuntimeError("download_dataset_first")

        if dir is not None:
            shutil.copy(file_path, f"{self.local_path}/{dir}/")
        else:
            shutil.copy(file_path, f"{self.local_path}/")

    def add_files(self, files=[], dir=None):
        for f in files:
            self.add_file(f, dir)

    def add_directory(self, *, path, dir=None):
        if dir is not None:
            shutil.copytree(path, f"{self.local_path}/{dir}/{path}")
        else:
            shutil.copytree(path, f"{self.local_path}/{path}")

    def _handle_bad_request(self, response_body):
        msg = response_body["detail"]["non_field_errors"][0]
        if msg == "dataset_not_found":
            raise DatasetNotFound

    def download(self):
        try:
            self.dataset_object = self.cli_client.retrieve_dataset(
                name=self.name,
                version=self.version,
                public=self.public,
                create=self.create,
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == HTTPStatus.BAD_REQUEST:
                self._handle_bad_request(e.response.json())
                return
            else:
                raise

        self.metatable = self._load_metatable()
        self.diff_table = {}

        if not self.local_path:
            self.local_path = f"./{self.name}"
            pathlib.Path(self.local_path).mkdir(parents=True, exist_ok=True)

        objects = []
        for file_id, obj in self.dataset_object["object_urls"].items():
            objects.append({"url": obj["url"], "path": obj["path"], "file_id": file_id})

        res_map = self._async_pool(objects, self._fetch_file)
        for file_id, success in res_map.items():
            if not success:
                raise RuntimeError("download_failed")

    def _fetch_file(self, obj):
        try:
            r = requests.get(obj["url"], stream=True)
        except requests.exceptions.ConnectionError:
            return (obj["file_id"], False)

        if r.status_code == HTTPStatus.OK:
            file = f"{self.local_path}/{obj['path']}"

            if not os.path.exists(os.path.dirname(file)):
                try:
                    os.makedirs(os.path.dirname(file))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise

            with open(f"{file}", "wb") as f:
                for chunk in r:
                    f.write(chunk)

        return (obj["file_id"], True)

    def _put_file(self, obj):
        with open(f"{self.local_path}/{obj['path']}", "rb") as f:
            try:
                r = requests.put(
                    f"{obj['url']}",
                    data=f.read(),
                )
            except requests.exceptions.ConnectionError:
                return (obj["file_id"], False)

            r.raise_for_status()

        return (obj["file_id"], True)

    def _async_pool(self, objects, callback):
        res_map = {}

        with tqdm(total=len(objects)) as progress_bar:
            for i, res in tqdm(
                enumerate(
                    ThreadPool(DATASET_IO_THREAD_COUNT).imap_unordered(
                        callback, objects
                    )
                )
            ):
                progress_bar.update()
                res_map[res[0]] = res[1]

        progress_bar.close()
        return res_map

    def path(self):
        return self.local_path

    def diff(self):
        self._checksum_local_path()

        for file_id, value in self.diff_table.items():
            print(f"{file_id}: {value}")

    def save(self):
        changes = self._checksum_local_path()
        if changes:
            self.dataset_object = self.cli_client.update_dataset(
                name=self.name, public=self.public, diff_table=self.diff_table
            )

            objects = []
            for file_id, obj in self.dataset_object["object_urls"].items():
                objects.append(
                    {"url": obj["url"], "path": obj["path"], "file_id": file_id}
                )

            res_map = self._async_pool(objects, self._put_file)
            for file_id, success in res_map.items():
                if not success:
                    raise RuntimeError("upload_failed")

            self.metatable = self._load_metatable()
            self.diff_table = {}

    def describe(self):
        if not self.metatable:
            return

        return self.metatable.values()

    def reset(self):
        raise NotImplementedError

    def _load_metatable(self):
        metatable = {}
        for file_id, node in self.dataset_object["metatable"].items():
            node = DataSetNode(
                name=node[0], parent_name=node[1], hash=node[2], index=node[3]
            )
            metatable[file_id] = node

        return metatable

    def _regenerate_metatable(self):
        metatable = {}
        for dirpath, _, fnames in os.walk(self.local_path):
            path = dirpath.replace(str(self.local_path), "", 1)
            if len(path) > 0 and path[0] == "/":
                path = path[1:]

            for f in fnames:
                node = DataSetNode(
                    name=f,
                    parent_name=path,
                    hash=xxhash.xxh128(
                        open(f"{self.local_path}/{path}/{f}", "rb").read()
                    ).hexdigest(),
                    index=0,
                )
                file_id = xxhash.xxh128_hexdigest(f"{path}/{f}")
                metatable[file_id] = node

        return metatable

    def _checksum_local_path(self):
        self.diff_table = {}

        changes = False

        if not self.local_path:
            raise RuntimeError("download_dataset_first")

        self.next_metatable = self._regenerate_metatable()

        for file_id, node in self.next_metatable.items():
            if file_id in self.metatable:
                existing_node = self.metatable[file_id]

                if node.hash != existing_node.hash:
                    node = node._replace(index=existing_node.index + 1)
                    self.diff_table[file_id] = {
                        "node": node._asdict(),
                        "action": "modified",
                    }
                    changes = True
            else:
                node = node._replace(index=0)

                self.diff_table[file_id] = {
                    "node": node._asdict(),
                    "action": "created",
                }
                changes = True

        file_ids = set(self.metatable.keys())
        next_file_ids = set(self.next_metatable.keys())

        deleted_file_ids = file_ids.difference(next_file_ids)

        if len(deleted_file_ids) > 0:
            changes = True

        for file_id in list(deleted_file_ids):
            self.diff_table[file_id] = {
                "node": self.metatable[file_id]._asdict(),
                "action": "deleted",
            }

        return changes
