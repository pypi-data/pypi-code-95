import os
import math
import json
import time
import hashlib
import fnmatch
import mimetypes
import threading

from queue import Queue
from pathlib import Path
from os import path, walk
from cnvrg.helpers.url_builder_helper import url_join
from cnvrg.modules.storage.progress import Progressbar

import cnvrg.modules.storage as storage
import cnvrg.helpers.apis_helper as apis_helper


# File type check util
def filter_by_mimetypes(filters, current_path):
    """
    mimetypes for files will return in the following format: "TYPE/EXACT_TYPE", for ex. 'image/jpeg'
    This function will receive general types in the filters list (for ex. ['image']), and will only return
    True for files that match any of the filters
    @param filters: Allowed file types.
    @param path: File to test against filters
    @return: True if file passed filters, False if file is filtered
    """
    # This means its a directory
    if not filters:
        return True
    if not mimetypes.guess_type(current_path)[0]:
        return False
    mime_type = mimetypes.guess_type(current_path)[0].split('/')[0]
    return mime_type in filters


class FileUploader:
    def __init__(self, element=None):
        self.element = element
        self.storage_client = storage.storage_factory(element=element)

    def upload_multiple_files(self, fileable, files=None, commit_sha1=None, prefix=None):
        if files is not None:
            chunks = FileUploader.chunk_file_list(files, math.ceil(len(files) / 1000))

            progress = Progressbar(total=len(files))

            progress_bar_lock = threading.Lock()

            files_queue = Queue(5000)
            progress_queue = Queue(5000)

            work = threading.Event()
            work.set()

            files_collector_thread = threading.Thread(
                target=FileUploader.files_collector,
                args=(files_queue, progress, progress_bar_lock, fileable, commit_sha1, chunks, prefix)
            )
            files_collector_thread.start()

            files_reporter_thread = threading.Thread(
                target=FileUploader.files_reporter,
                args=(progress_queue, progress, progress_bar_lock, fileable, commit_sha1)
            )
            files_reporter_thread.start()

            thread_pool = []
            for i in range(len(chunks)):
                t = threading.Thread(
                    target=FileUploader.worker,
                    args=(work, files_queue, progress_queue, self.storage_client)
                )
                t.start()
                thread_pool.append(t)

            files_collector_thread.join()
            files_reporter_thread.join()

            work.clear()

            for t in thread_pool:
                t.join()

    @staticmethod
    def files_collector(file_queue, progress, progress_bar_lock, fileable, commit_sha1, chunks, prefix):
        for chunk in chunks:
            try:
                blob_vs = FileUploader.create_blob_versions(fileable, commit_sha1, chunk, prefix)
                for k, v in blob_vs["files"].items():
                    try:
                        file_queue.put({
                            "full_path": k,
                            "source": v["local_path"],
                            "target": v["path"],
                            "bv_id": str(v["bv_id"])
                        })
                    except Exception:
                        with progress_bar_lock:
                            progress.progress += 1
                        print("Failed to upload {}".format(k))

                with progress_bar_lock:
                    progress.progress += len(chunk) - len(blob_vs["files"])

            except Exception as e:
                with progress_bar_lock:
                    progress.progress += len(chunk)
                print(e)

    @staticmethod
    def files_reporter(progress_queue, progress, progress_bar_lock, fileable, commit_sha1):
        uploaded_files = []

        while progress.progress < progress.total:
            try:
                file = progress_queue.get_nowait()

                with progress_bar_lock:
                    progress.progress += 1

                if file is not None:
                    uploaded_files.append(file["bv_id"])

                    if len(uploaded_files) >= 1000 or progress.progress >= progress.total:
                        FileUploader.save_blob_versions_to_commit(fileable, uploaded_files, commit_sha1)
                        uploaded_files = []
            except Exception:
                time.sleep(1)

        progress.finish()

    @staticmethod
    def worker(work, files_queue, progress_queue, storage_client):
        while work.is_set():
            try:
                file = files_queue.get_nowait()
                try:
                    storage_client.upload_single_file(file["source"], file["target"])
                    progress_queue.put(file)
                except Exception as e:
                    progress_queue.put(None)
                    print("Failed to upload {}".format(file["full_path"]))
                    print(e)

            except Exception as e:
                print(e)
                time.sleep(1)

    @staticmethod
    def chunk_file_list(file_list, num_chunks):
        chunks = []
        for i in range(0, num_chunks):
            chunks.append(file_list[i::num_chunks])
        return chunks

    @staticmethod
    def get_recursive_tree(file_path, is_absolute, is_dir, depth=False):
        trees = []
        if is_absolute:
            if depth:
                while str(file_path) != Path(file_path).anchor and str(file_path) != ".":
                    tmp_path = Path(file_path)
                    tmp_parent = tmp_path.parent
                    trees.append("{}/".format(str(tmp_parent)))
                    file_path = tmp_parent
            else:
                if is_dir and not file_path.endswith("/"):
                    file_path = "{}/".format(file_path)
                trees.append(file_path)
        else:
            while str(file_path) != Path(file_path).anchor and str(file_path) != ".":
                tmp_path = Path(file_path)
                tmp_parent = tmp_path.parent
                trees.append("{}/".format(str(tmp_parent)))
                file_path = tmp_parent
        return trees

    @staticmethod
    def get_files_and_dirs_recursive(root_dir=".", regex="*", filters=None):
        full_paths = [url_join(FileUploader.get_relative_path(root_dir), "/")]
        for root, dirs, files in walk(root_dir, topdown=False):
            for name in files:
                full_paths.append(FileUploader.get_relative_path(path.join(root, name)))
            for name in dirs:
                full_paths.append(url_join(FileUploader.get_relative_path(path.join(root, name)), "/"))

        if filters:
            full_paths = [item for item in files if filter_by_mimetypes(filters, item)]

        return fnmatch.filter(full_paths, regex)

    @staticmethod
    def get_relative_path(full_path):
        if full_path.startswith("./"):
            full_path = full_path[2:]
        return full_path

    @staticmethod
    def sha1(full_path):
        BUF_SIZE = 65536
        sha1 = hashlib.sha1()

        with open(full_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)

        return sha1.hexdigest()

    @staticmethod
    def create_blob_versions(fileable, commit_sha1, full_paths, prefix):
        owner = fileable.owner
        files = {}
        for full_path in full_paths:
            full_path = full_path.replace("./", "")
            is_file = os.path.isfile(full_path)
            is_directory = os.path.isdir(full_path)
            is_absolute = os.path.isabs(full_path)
            if is_absolute:
                relative_path = os.path.basename(full_path)
            else:
                relative_path = full_path

            if is_file:
                prefix_full_path = os.path.join(prefix, relative_path) if prefix else relative_path
                content_type = mimetypes.guess_type(full_path, strict=True)
                files.update({
                    prefix_full_path: {
                        "absolute_path": "{}/".format(os.path.dirname(os.path.abspath(full_path))),
                        "local_path": full_path,
                        "content_type": content_type[0] or "plain/text",
                        "file_name": os.path.basename(full_path),
                        "file_size": os.path.getsize(full_path),
                        "relative_path": prefix_full_path,
                        "sha1": FileUploader.sha1(full_path)
                    }
                })
            elif is_directory:
                files.update({
                    full_path: {
                        "absolute_path": "{}/".format(url_join(os.getcwd(), full_path)),
                        "relative_path": full_path
                    }
                })

        resp = apis_helper.post_v2(url_join(owner, "files", "create_blob_versions"), data={
            "fileable_type": "Project",
            "fileable_slug": fileable.slug.lower(),
            "commit": commit_sha1,
            "files": json.dumps(files)
        })

        return resp.json().get("result")

    @staticmethod
    def save_blob_versions_to_commit(fileable, blob_ids, commit_sha1):
        owner = fileable.owner
        resp = apis_helper.post_v2(url_join(owner, "files", "save_blob_versions_to_commit"), data={
            "fileable_type": "Project",
            "fileable_slug": fileable.slug,
            "commit": commit_sha1,
            "blob_ids": blob_ids
        })

        return resp.json()
