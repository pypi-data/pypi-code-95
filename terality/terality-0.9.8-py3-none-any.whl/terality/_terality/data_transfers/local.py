from pathlib import Path
from typing import List

from common_client_scheduler.requests_responses import AwsCredentials

from .common import DataTransfer
from .. import global_client


def upload_local_files(path: str, transfer_id: str, aws_credentials: AwsCredentials) -> None:
    """
    Copy files from a local directory to a Terality-owned S3 bucket.

    Args:
        path: path to a single file or a directory. If a directory, all files in the directory will be uploaded.
    """
    paths: List[str] = (
        [path] if Path(path).is_file() else [str(path_) for path_ in sorted(Path(path).iterdir())]
    )
    for file_num, _ in enumerate(paths):
        DataTransfer.upload_local_file(
            global_client().get_upload_config(),
            aws_credentials,
            paths[file_num],
            f"{transfer_id}/{file_num}.data",
        )
