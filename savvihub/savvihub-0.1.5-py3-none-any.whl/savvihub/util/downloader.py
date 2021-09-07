import concurrent.futures
import os

from requests_futures.sessions import FuturesSession

from savvihub.util.constant import PARALLEL_WORKERS
from savvihub.util.file_object import DownloadableFileObject


class Downloader:
    @classmethod
    def download(cls, local_path, file, progressable=None):
        dirname = os.path.dirname(local_path)
        basename = os.path.basename(local_path)
        d = DownloadableFileObject(file.download_url.url, dirname, basename)
        return d.download(progressable=progressable)

    @classmethod
    def bulk_download(cls, local_base_path, remote_files, progressable=None):
        if len(remote_files) <= 0:
            return []

        session = FuturesSession(max_workers=PARALLEL_WORKERS)
        futures = []
        for remote_file in remote_files:
            if remote_file.is_dir:
                continue

            d = DownloadableFileObject(
                remote_file.download_url.url, local_base_path, remote_file.path
            )
            futures.append(d.download(session, progressable=progressable))

        concurrent.futures.wait(futures)
        return [future.result() for future in futures]
