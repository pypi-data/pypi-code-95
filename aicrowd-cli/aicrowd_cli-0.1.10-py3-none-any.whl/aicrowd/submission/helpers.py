"""
Submission related tasks
"""
import json
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Tuple

import requests
from requests_toolbelt import MultipartEncoderMonitor
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.table import Table

# pylint: disable=unused-import
from aicrowd.challenge.helpers import must_get_api_key, parse_cli_challenge

# pylint: enable=unused-import
from aicrowd.constants import RAILS_HOST
from aicrowd.submission.exceptions import (
    ChallengeNotFoundException,
    SubmissionFileException,
    SubmissionUploadException,
)
from aicrowd.utils.jupyter import is_jupyter
from aicrowd.utils.utils import zip_fs_path
from aicrowd_api.submission import (
    create_rails_submission,
    get_submission_upload_details,
)


def calculate_min_table_width(table: Table):
    """
    Calculates minumum width needed to display table text properly

    Args:
        table: rich table
    """
    console = Console(width=200)
    width = (
        sum(table._calculate_column_widths(console, console.options))
        + table._extra_width
    )
    term_width = shutil.get_terminal_size().columns
    return max(width, term_width)


def get_upload_details(challenge_slug: str, api_key: str) -> Tuple[dict, bool]:
    """
    Contacts AIcrowd website for getting presigned url for uploading

    Args:
        challenge_slug: challenge slug
        api_key: AIcrowd API Key

    Returns:
        the data and whether the request was successful or not
    """
    log = logging.getLogger()

    r = get_submission_upload_details(api_key, challenge_slug)

    # temporary hack until /api stops redirecting
    if r.status_code // 100 == 3:
        redirected_to = r.headers["Location"]
        expected_redirect = f"https://{RAILS_HOST}"

        if redirected_to.startswith(expected_redirect):
            redirected_to = redirected_to[len(expected_redirect) :]
        else:
            log.error("Unexpected redirect location: %s", redirected_to)
            # got redirected to a weird place
            raise ChallengeNotFoundException(
                "Something went wrong with fetching challenge details"
            )

        challenge_problem = re.match(
            r"/challenges/([^/]*)/problems/([^/]*)/.*", redirected_to
        ).groups()
        logging.info("[metachallenge?] Got redirected to %s", redirected_to)

        # inform caller about meta_challenge
        return {
            "meta_challenge": True,
            "meta_challenge_id": challenge_problem[0],
            "challenge_id": challenge_problem[1],
        }, True

    try:
        resp = r.json()

        if not r.ok or not resp.get("success"):
            log.error(
                "Request to API failed\nReason: %s\nMessage: %s", r.reason, r.text
            )
            return resp, False

        return resp.get("data"), True
    except json.JSONDecodeError as e:
        log.error("Error while extracting details from API request: %s", e)
        raise ChallengeNotFoundException(
            "There was some error in contacting AIcrowd servers",
            "Please run this command with -v or -vv or .. -vvvvv to get more details",
        ) from e


class S3Uploader:
    """
    Upload files to s3 with progress bar
    """

    def __init__(self, host: str, fields: dict, file_path: str):
        """
        Args:
            host: s3 host to upload to
            fields: s3 related fields
            file_path: the file to upload
        """
        self.host = host
        self.fields = fields

        file_path = Path(file_path)

        self.file_name = file_path.name
        self.file_size = file_path.stat().st_size

        self.fields["key"] = self.fields["key"].replace("${filename}", self.file_name)
        self.fields["file"] = (self.file_name, file_path.open("rb"))

        self.progress = Progress(
            TextColumn("[bold blue]{task.fields[file_name]}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
        )
        self.progress.console.is_jupyter = is_jupyter()
        self.task_id = self.progress.add_task(
            "upload", file_name=self.file_name, start=False, total=self.file_size
        )

    def track_progress(self, monitor: MultipartEncoderMonitor):
        """
        shows progress bar showing how much has been uploaded

        Args:
            monitor: requests_toolbelt Monitor
        """
        self.progress.update(self.task_id, completed=monitor.bytes_read, refresh=True)

    def upload(self):
        """
        upload file to s3
        """
        self.progress.start_task(self.task_id)
        m = MultipartEncoderMonitor.from_fields(
            self.fields, callback=self.track_progress
        )

        with self.progress:
            return (
                requests.post(
                    self.host, data=m, headers={"Content-Type": m.content_type}
                ),
                self.fields["key"],
            )


def upload_submission(host: str, fields: dict, file_path: str) -> str:
    """
    uploads a file to s3 using presigned url details

    Args:
        host: s3 host to upload to
        fields: s3 related keys
        file_path: the file to be uploaded

    Returns:
        whether it was successful or not
    """
    log = logging.getLogger()

    r, s3_key = S3Uploader(host, fields, file_path).upload()

    if not r.ok:
        log.error(
            "Couldn't upload file to s3\nReason: %s\nMessage: %s", r.reason, r.text
        )
        return None

    return s3_key


def notify_rails_upload(
    challenge_slug: str,
    submitted_url: str,
    api_key: str,
    description: str,
    problem_slug: str = None,
) -> dict:
    """
    notify rails about the uploaded file on s3

    Args:
        challenge_slug: challenge slug
        submitted_url: the url to which the submitted file was uploaded to
        description: submission description
        problem_slug: Used when submitting to a meta challenge

    Returns:
        submission details from AIcrowd API
    """
    log = logging.getLogger()

    if problem_slug is None:
        payload = {"challenge_id": challenge_slug}
    else:
        payload = {"meta_challenge_id": challenge_slug, "challenge_id": problem_slug}

    payload.update(
        {
            "description": description,
            "submission_files": [{"submission_file_s3_key": submitted_url}],
        }
    )

    r = create_rails_submission(api_key, payload)

    if not r.ok:
        log.error("Request to API failed\nReason: %s\nMessage: %s", r.reason, r.text)
        raise SubmissionUploadException(
            f"Couldn't decode response from AIcrowd servers. {r.reason}", r.text
        )

    try:
        return r.json()
    except json.JSONDecodeError as e:
        log.error("Couldn't json-decode rails response")
        raise SubmissionUploadException(
            "Couldn't decode response from AIcrowd servers"
        ) from e


def print_submission_links(challenge_slug: str, problem_slug: str, submission_id: int):
    """
    prints helpful links related to the submission

    Args:
        challenge_slug: challenge slug
        problem_slug: when submitting to a meta challenge
        submission_id: rails submission id
    """
    if submission_id is None:
        return

    if problem_slug:
        challenge_url = (
            f"https://{RAILS_HOST}/challenges/{challenge_slug}/problems/{problem_slug}"
        )
    else:
        challenge_url = f"https://{RAILS_HOST}/challenges/{challenge_slug}"

    submission_base_url = f"{challenge_url}/submissions"

    table = Table(title="Important links", show_header=False, leading=1, box=box.SQUARE)
    table.add_column(justify="right")
    table.add_column(overflow="fold")

    table.add_row("This submission", f"{submission_base_url}/{submission_id}")
    table.add_row("All submissions", f"{submission_base_url}?my_submissions=true")
    table.add_row("Leaderboard", f"{challenge_url}/leaderboards")
    table.add_row(
        "Discussion forum", f"https://discourse.aicrowd.com/c/{challenge_slug}"
    )
    table.add_row("Challenge page", f"{challenge_url}")

    width = calculate_min_table_width(table)

    console = Console(width=width)
    table.min_width = width
    console.print(Panel("[bold]Successfully submitted!"), justify="center")
    console.print(table)


def submit_file(
    challenge_slug: str,
    file_path: str,
    description: str,
    api_key: str,
    print_links: bool,
) -> dict:
    """
    Submits a file given it's path and challenge_slug with given description

    Args:
        challenge_slug: challenge slug
        file_path: path to the file to be uploaded
        description: description for the submission
        api_key: AIcrowd API Key
        print_links: should helpful links be printed?

    Returns:
        a message from AIcrowd API
    """
    log = logging.getLogger()
    problem_slug = None

    if not Path(file_path).is_file():
        raise SubmissionFileException(f"Bad file {file_path}")

    s3_presigned_details, success = get_upload_details(challenge_slug, api_key)

    if s3_presigned_details.get("meta_challenge"):
        challenge_slug = s3_presigned_details.get("meta_challenge_id")
        problem_slug = s3_presigned_details.get("challenge_id")

        s3_presigned_details, success = get_upload_details(challenge_slug, api_key)

    if not success:
        log.error(
            "Error in getting presigned url for s3 upload: %s",
            s3_presigned_details.get("message"),
        )
        raise SubmissionUploadException(
            "Something went wrong while uploading your submission",
            s3_presigned_details.get("message"),
        )

    s3_key = upload_submission(
        s3_presigned_details["url"], s3_presigned_details["fields"], file_path
    )
    if s3_key is None:
        raise SubmissionUploadException(
            "Couldn't submit file. Please recheck the files and details provided"
        )

    response = notify_rails_upload(
        challenge_slug, s3_key, api_key, description, problem_slug
    )
    if not response.get("success"):
        log.error("Couldn't notify AIcrowd servers about uploaded submission")
        raise SubmissionUploadException(
            response.get(
                "message", "Something went wrong while contacting AIcrowd servers"
            )
        )

    if print_links:
        print_submission_links(
            challenge_slug, problem_slug, response.get("data", {}).get("submission_id")
        )

    return response.get("data")


def zip_assets(assets_dir: str, target_zip_path: str):
    """
    Zip the files under assets directory

    Args:
        assets_dir: Directory containing submission assets
        target_zip_path: Path to zip file to add the entries to
    """
    console = Console()
    if not os.path.exists(assets_dir):
        os.mkdir(assets_dir)
        console.print("WARNING: Assets dir is empty", style="bold red")
    zip_fs_path(assets_dir, target_zip_path)


def delete_and_copy_dir(src: str, dst: str):
    """
    Delete if the src exists and copy files from src to dst

    Args:
        src: Source path
        dst: Destination path
    """
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
