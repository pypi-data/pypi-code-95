# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import glob
import os
import re
import shutil
import sys

import click
from flask import current_app

from kadi.cli.main import kadi
from kadi.cli.utils import check_env
from kadi.cli.utils import danger
from kadi.cli.utils import echo
from kadi.cli.utils import success
from kadi.cli.utils import warning
from kadi.ext.db import db
from kadi.lib.exceptions import KadiChecksumMismatchError
from kadi.lib.storage.core import create_filepath
from kadi.lib.storage.local import LocalStorage
from kadi.lib.tasks.models import Task
from kadi.modules.records.files import remove_files
from kadi.modules.records.files import remove_temporary_files
from kadi.modules.records.models import File
from kadi.modules.records.models import TemporaryFile
from kadi.modules.records.models import Upload
from kadi.modules.records.uploads import remove_uploads


@kadi.group()
def files():
    """Utility commands for local file management."""


def _remove_path(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


@files.command()
@click.option("--i-am-sure", is_flag=True)
@check_env
def clean(i_am_sure):
    """Remove all files in the configured local storage paths.

    Aside from the files stored in STORAGE_PATH, this command will also delete all
    general user uploads stored in MISC_UPLOADS_PATH.

    Should preferably only be run while the application and celery are not running.
    """
    storage_path = current_app.config["STORAGE_PATH"]
    misc_uploads_path = current_app.config["MISC_UPLOADS_PATH"]

    if not i_am_sure:
        warning(
            f"This will remove all data in '{storage_path}' and '{misc_uploads_path}'."
            " If you are sure you want to do this, use the flag --i-am-sure."
        )
        sys.exit(1)

    for item in os.listdir(storage_path):
        _remove_path(os.path.join(storage_path, item))

    for item in os.listdir(misc_uploads_path):
        _remove_path(os.path.join(misc_uploads_path, item))

    success("Storage cleaned successfully.")


@files.command()
def check():
    """Check the configured local storage path for inconsistencies.

    Each local file, temporary file and upload from the database will be checked for
    corresponding data in the configured storage path (STORAGE_PATH) and vice versa.

    Should preferably only be run while the application and celery are not running.
    """
    inconsistencies = 0
    inconsistent_items = []
    storage = LocalStorage()

    # Check local files.
    files_query = File.query.filter_by(storage_type="local")
    echo(f"Checking {files_query.count()} local files in database...")

    for file in files_query.order_by("created_at"):
        filepath = create_filepath(str(file.id))

        # If an active file exists in storage, we validate its integrity by verifying
        # its checksum, otherwise there is an inconsistency.
        if file.state == "active":
            if os.path.isfile(filepath):
                try:
                    storage.verify_checksum(filepath, file.checksum)
                except KadiChecksumMismatchError:
                    inconsistencies += 1
                    inconsistent_items.append(file)
                    danger(
                        f"[{inconsistencies}] Mismatched checksum for active file"
                        f" object in database with ID '{file.id}' and data at"
                        f" '{filepath}'."
                    )
            else:
                inconsistencies += 1
                inconsistent_items.append(file)
                danger(
                    f"[{inconsistencies}] Found orphaned active file object in database"
                    f" with ID '{file.id}'."
                )

        # Inactive files will be handled by the periodic cleanup task eventually.
        elif file.state == "inactive":
            pass

        # Deleted file objects should not have any data associated with them anymore.
        elif file.state == "deleted" and os.path.isfile(filepath):
            inconsistencies += 1
            inconsistent_items.append(file)
            danger(
                f"[{inconsistencies}] Found deleted file object in database with ID"
                f" '{file.id}' and data at '{filepath}'."
            )

    # Check uploads.
    uploads_query = Upload.query
    echo(f"Checking {uploads_query.count()} uploads in database...")

    for upload in uploads_query.order_by("created_at"):
        # Active uploads will either be handled if they are finished, be it successful
        # or not, or by the periodic cleanup task eventually.
        if upload.state == "active":
            pass

        # Inactive uploads will be handled by the periodic cleanup task eventually.
        elif upload.state == "inactive":
            pass

        # If an upload is still processing, check if the corresponding task is still
        # pending. If so, it is up to the task to decide if the processing should
        # complete or not, otherwise the task may have been canceled forcefully.
        elif upload.state == "processing":
            task = Task.query.filter(
                Task.name == "kadi.records.merge_chunks",
                Task.arguments["args"][0].astext == str(upload.id),
            ).first()

            if task.state != "pending":
                inconsistencies += 1
                inconsistent_items.append(upload)
                inconsistent_items.append(task)
                danger(
                    f"[{inconsistencies}] Found processing upload object in database"
                    f" with ID '{upload.id}' and non-pending task with ID '{task.id}'."
                )

    # Check temporary files.
    temporary_files_query = TemporaryFile.query
    echo(f"Checking {temporary_files_query.count()} temporary files in database...")

    for temporary_file in temporary_files_query.order_by("created_at"):
        filepath = create_filepath(str(temporary_file.id))

        # Active temporary files should exist in storage.
        if temporary_file.state == "active" and not os.path.isfile(filepath):
            inconsistencies += 1
            inconsistent_items.append(temporary_file)
            danger(
                f"[{inconsistencies}] Found orphaned active temporary file object in"
                f" database with ID '{temporary_file.id}'."
            )

        # Inactive temporary files will be handled by the periodic cleanup task
        # eventually.
        elif temporary_file.state == "inactive":
            pass

    # Check file storage.
    storage_path = current_app.config["STORAGE_PATH"]
    filename_re = re.compile(
        "^([0-9a-f]{{2}}{sep}[0-9a-f]{{2}}{sep}[0-9a-f]{{2}}{sep}[0-9a-f]{{2}}"
        "-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}})(-[0-9]+)?$".format(
            sep=os.sep
        )
    )

    echo(f"Checking file storage at '{storage_path}'...")

    for path in glob.iglob(os.path.join(storage_path, "**", "*"), recursive=True):
        if os.path.isfile(path):
            filename = os.path.relpath(path, storage_path)
            match = filename_re.match(filename)

            # This should normally not happen, but we check for it just in case.
            if match is None:
                warning(f"Found unexpected data at '{path}'.")
                continue

            object_id = match.group(1).replace(os.sep, "")

            # Matched a potential file, upload or temporary file.
            if match.group(2) is None:
                if (
                    File.query.get(object_id) is None
                    and Upload.query.get(object_id) is None
                    and TemporaryFile.query.get(object_id) is None
                ):
                    inconsistencies += 1
                    inconsistent_items.append(path)
                    danger(f"[{inconsistencies}] Found orphaned file data at '{path}'.")

            # Matched a potential chunk.
            else:
                upload = Upload.query.get(object_id)
                chunk_index = match.group(2)[1:]

                if (
                    upload is None
                    or upload.chunks.filter_by(index=chunk_index).first() is None
                ):
                    inconsistencies += 1
                    inconsistent_items.append(path)
                    danger(
                        f"[{inconsistencies}] Found orphaned chunk data at '{path}'."
                    )

    if inconsistencies == 0:
        success("Files checked successfully.")
    else:
        warning(
            f"Found {inconsistencies}"
            f" {'inconsistency' if inconsistencies == 1 else 'inconsistencies'}."
        )

        if click.confirm(
            "Do you want to resolve all inconsistencies automatically by deleting all"
            " inconsistent data and/or database entries?"
        ):
            for item in inconsistent_items:
                if isinstance(item, File):
                    remove_files(item)

                elif isinstance(item, Upload):
                    remove_uploads(item)

                elif isinstance(item, TemporaryFile):
                    remove_temporary_files(item)

                elif isinstance(item, Task):
                    item.revoke()
                    db.session.commit()

                elif isinstance(item, str):
                    storage.delete(item)
                    storage.remove_empty_parent_dirs(item, num_dirs=3)

            success("Inconsistencies resolved successfully.")
