import os
from stat import S_IREAD, S_IRGRP, S_IROTH
from posixpath import relpath
from requests.api import get
from rich.progress import Progress, BarColumn, DownloadColumn, TimeRemainingColumn
from turbineml.configuration import _config
from turbineml import volume_cache
from turbineml.internal.file_wrapper import FileWrapper
import requests
import tempfile
import shutil
import atexit

def _cleanup_temp_dir(dirname):
    shutil.rmtree(dirname)

def create_volume(project, tags=[], job=None):
    # TODO validate format of project
    headers = {"Authorization": "Bearer " + _config.get_api_key()}

    request_body = {
        "tags": tags,
        "createdByJob": job.job_id if job is not None else None
    }

    url = f"{_config.get_api_url()}volumes/{project}/create"
    r = requests.post(url, headers=headers, json=request_body)
    r.raise_for_status()
    
    response = r.json()
    volume_id = response["volumeId"]

    return Volume(project, volume_id)

def get_volume(project, volume_ref):
    # TODO validate format of project
    headers = {"Authorization": "Bearer " + _config.get_api_key()}

    url = f"{_config.get_api_url()}volumes/{project}/resolveRef?volumeRef={requests.utils.quote(volume_ref)}"
    r = requests.post(url, headers=headers)
    r.raise_for_status()
    
    response = r.json()
    volume_id = response["volumeId"]

    return Volume(project, volume_id)

def _iterate_upload_files(src_dir, target_path):
    for root, _, files in os.walk(src_dir):
        relative_dir = os.path.relpath(root, src_dir)
        if relative_dir == ".":
            relative_dir = ""
        for file in files:
            src_file = os.path.join(root, file)
            file_target_path = os.path.join(target_path, relative_dir, file)
            yield UploadFile(src_file, file_target_path)

def _get_total_size(upload_files):
    return sum(os.path.getsize(f.src_file) for f in upload_files)

def _canonicalize_path(path):
    return path.replace('\\', '/')


class UploadFile:
    def __init__(self, src_file, target_path, content_type="application/octet-stream") -> None:
        self.src_file = src_file
        self.target_path = target_path
        self.content_type = content_type

class Volume:
    def __init__(self, project, volume_id):
        # TODO validate format of project
        self.project = project
        self.volume_id = volume_id
        self.api_url = _config.get_api_url()

        # Ensure volume exists
        self._list_volume()
    
    def list_files(self):
        return [x['path'] for x in self._list_volume()]

    def upload_file(self, file, volume_path=None, content_type="application/octet-stream"):
        if volume_path is None:
            volume_path = os.path.basename(file)
        self.upload_files([UploadFile(file, volume_path, content_type)])
    
    def upload_files(self, files):
        total_size = _get_total_size(files)

        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            DownloadColumn(),
            TimeRemainingColumn(),
        ) as progress:
            files_text = "file" if len(files) == 1 else "files"
            task = progress.add_task(f"Uploading {len(files)} {files_text}...", total=total_size)

            def callback(bytes_read):
                nonlocal task
                progress.update(task, advance=bytes_read)

            for file in files:
                if isinstance(file.src_file, str):
                    file_stream = open(file.src_file, "rb")
                    close_file = True
                else:
                    file_stream = file.src_file
                    close_file = False

                file_wrapper = FileWrapper(file_stream, callback)
                headers = {
                    "Authorization": "Bearer " + _config.get_api_key(),
                    "content-type": file.content_type
                }
                url = f"{self.api_url}volumes/{self.project}/upload?volumeId={requests.utils.quote(self.volume_id)}&path={requests.utils.quote(file.target_path)}"
                r = requests.post(url, headers=headers, data=file_wrapper)
                if close_file:
                    file_stream.close()
                r.raise_for_status()
        
    def upload_dir(self, src_dir, target_path):
        self.upload_files(list(_iterate_upload_files(src_dir, target_path)))

    def commit(self):
        headers = {"Authorization": "Bearer " + _config.get_api_key()}
        r = requests.post(f"{self.api_url}volumes/{self.project}/commit?volumeId={requests.utils.quote(self.volume_id)}", headers=headers)
        r.raise_for_status()

    def open_file(self, filename, mode):
        return open(self.get_local(filename), mode)
    
    def get_local(self, filename):
        digest = self._get_digest(filename)
        return self._ensure_cached(digest)

    def checkout(self):
        self.precache()
        checkout_dir = tempfile.mkdtemp()
        atexit.register(_cleanup_temp_dir, checkout_dir)
        for src_file in self.list_files():
            relative_dir = os.path.dirname(src_file)
            output_dir = os.path.join(checkout_dir, relative_dir)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            shutil.copyfile(self.get_local(src_file), os.path.join(checkout_dir, src_file))
        return checkout_dir

    def precache(self):
        files = self._list_volume()

        print(f"Downloading {len(files)} files...")
        for file in files:
            self._ensure_cached(file['digest'])
        
    def _ensure_cached(self, digest):
        if volume_cache.file_exists(digest):
            return volume_cache.get_path(digest)
        target_file = volume_cache.get_path(digest)

        headers = {"Authorization": "Bearer " + _config.get_api_key()}
        r = requests.get(f"{self.api_url}volumes/{self.project}/getFile?digest={digest}", headers=headers, stream=True)
        r.raise_for_status()

        with open(target_file, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        os.chmod(target_file, S_IREAD|S_IRGRP|S_IROTH)
        return target_file


    def _get_digest(self, filename):
        filename = _canonicalize_path(filename)
        files = self._list_volume()
        digest = None
        for file in files:
            if file['path'] == filename:
                digest = file['digest']
        if digest is None:
            raise Exception("File not found: " + filename)
        return digest
    
    def _list_volume(self):
        headers = {"Authorization": "Bearer " + _config.get_api_key()}
        r = requests.get(f"{self.api_url}volumes/{self.project}/list?volumeId={requests.utils.quote(self.volume_id)}", headers=headers)
        r.raise_for_status()
        return r.json()
    
