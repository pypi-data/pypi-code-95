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
from datetime import timedelta

from flask import current_app
from flask_babel import force_locale
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

import kadi.lib.constants as const
from .core import purge_record
from .files import package_files
from .files import remove_files
from .files import remove_temporary_files
from .models import File
from .models import Record
from .models import TemporaryFile
from .models import Upload
from .uploads import merge_chunks
from .uploads import remove_uploads
from kadi.ext.celery import celery
from kadi.ext.db import db
from kadi.lib.exceptions import KadiChecksumMismatchError
from kadi.lib.exceptions import KadiFilesizeExceededError
from kadi.lib.exceptions import KadiFilesizeMismatchError
from kadi.lib.publications import publish_record
from kadi.lib.tasks.core import launch_task
from kadi.lib.tasks.models import Task
from kadi.lib.utils import utcnow
from kadi.lib.web import get_locale
from kadi.modules.accounts.models import User


@celery.task(
    name="kadi.records.merge_chunks", soft_time_limit=const.ONE_HOUR, bind=True
)
def _merge_chunks_task(self, upload_id, **kwargs):
    task = Task.query.get(self.request.id)
    upload = Upload.query.get(upload_id)

    # Check if the upload was not deleted before the task actually started, which will
    # also be the case if a file to be replaced by the upload was deleted.
    if task.is_revoked or upload is None or upload.state != "processing":
        return None

    file = None

    try:
        file = merge_chunks(upload, task=task)

        if file is not None:
            task.result = {"file": str(file.id)}
        else:
            task.state = "failure"
            task.result = {"error": "File has already been deleted."}

    # Catches time limit exceeded exceptions as well.
    except Exception as e:
        db.session.rollback()
        task.state = "failure"

        if isinstance(
            e,
            (
                KadiFilesizeExceededError,
                KadiFilesizeMismatchError,
                KadiChecksumMismatchError,
            ),
        ):
            task.result = {"error": str(e)}
        elif isinstance(e, IntegrityError):
            task.result = {"error": "A file with that name already exists."}
        else:
            current_app.logger.exception(e)
            task.result = {"error": "Internal server error."}

    db.session.commit()
    return str(file.id) if file is not None else None


def start_merge_chunks_task(upload, user=None):
    """Merge the chunks of a local file upload in a background task.

    Uses :func:`kadi.modules.records.files.merge_chunks`. The created task will be kept
    in the database.

    Note that this function issues one or more database commits.

    :param upload: The upload that the chunks belong to.
    :param user: (optional) The user that started the task. Defaults to the current
        user.
    :return: The new task object if the task was started successfully, ``None``
        otherwise.
    """
    user = user if user is not None else current_user

    return launch_task(
        "kadi.records.merge_chunks", args=(str(upload.id),), user=user, keep=True
    )


@celery.task(
    name="kadi.records.package_files", soft_time_limit=const.ONE_HOUR, bind=True
)
def _package_files_task(self, record_id, **kwargs):
    task = Task.query.get(self.request.id)

    if task.is_revoked:
        return None

    record = Record.query.get(record_id)
    user = User.query.get(kwargs["_meta"]["user"])

    temporary_file = None

    try:
        temporary_file = package_files(record, user, task=task)

        if temporary_file is not None and not task.is_revoked:
            task.result = {"temporary_file_id": str(temporary_file.id)}

    # Catches time limit exceeded exceptions as well.
    except Exception as e:
        current_app.logger.exception(e)

        db.session.rollback()
        task.state = "failure"

    db.session.commit()
    return str(temporary_file.id) if temporary_file is not None else None


def start_package_files_task(record, user=None):
    """Package all local files of a record together in a background task.

    Uses :func:`kadi.modules.records.files.package_files`. The created task will be kept
    in the database and the user that started the task will get notified about its
    current status as well.

    Note that this function issues one or more database commits.

    :param record: The record whose files should be packaged.
    :param user: (optional) The user that started the task. Defaults to the current
        user.
    :return: The new task object if the task was started successfully, ``None``
        otherwise.
    """
    user = user if user is not None else current_user

    return launch_task(
        "kadi.records.package_files",
        args=(record.id,),
        user=user,
        keep=True,
        notify=True,
    )


@celery.task(
    name="kadi.records.publish_record", soft_time_limit=const.ONE_HOUR, bind=True
)
def _publish_record_task(self, record_id, provider, locale, **kwargs):
    task = Task.query.get(self.request.id)

    if task.is_revoked:
        return None

    record = Record.query.get(record_id)
    user = User.query.get(kwargs["_meta"]["user"])

    success = False

    try:
        # Since the result template may contain translatable strings and we cannot get
        # the user's locale the usual way, we instead force the locale that was given to
        # us.
        with force_locale(locale):
            success, template = publish_record(record, provider, user=user, task=task)

        if not task.is_revoked:
            if not success:
                task.state = "failure"

            task.result = {"template": template}

    # Catches time limit exceeded exceptions as well.
    except Exception as e:
        current_app.logger.exception(e)

        db.session.rollback()
        task.state = "failure"

    db.session.commit()
    return success


def start_publish_record_task(record, provider, user=None, force_locale=True):
    """Publish a record using a given provider in a background task.

    The created task will be kept in the database and the user that started the task
    will get notified about its current status as well.

    Note that this function issues one or more database commits.

    :param record: The record to publish.
    :param provider: The provider to use for publishing.
    :param user: (optional) The user that started the task. Defaults to the current
        user.
    :param force_locale: (optional) Flag indicating whether the current locale as
        returned by :func:`kadi.lib.web.get_locale` should be used inside the task. If
        ``False``, the default locale will be used instead given by ``LOCALE_DEFAULT``
        as configured in the application's configuration.
    :return: The new task object if the task was started successfully, ``None``
        otherwise.
    """
    user = user if user is not None else current_user

    if force_locale:
        locale = get_locale()
    else:
        locale = current_app.config["LOCALE_DEFAULT"]

    return launch_task(
        "kadi.records.publish_record",
        args=(record.id, provider, locale),
        user=user,
        keep=True,
        notify=True,
    )


@celery.task(name="kadi.records.purge_record")
def _purge_record_task(record_id, **kwargs):
    record = Record.query.get(record_id)

    try:
        purge_record(record)
    except Exception as e:
        current_app.logger.exception(e)

        db.session.rollback()
        # In case the state of the record was set to "purged" before, make sure to reset
        # it so another attempt can be made to delete it as part of the periodic task.
        record.state = "deleted"

    db.session.commit()


def start_purge_record_task(record):
    """Purge an existing record in a background task.

    Uses :func:`kadi.modules.records.core.purge_record`.

    :param record: The record to purge.
    """
    return launch_task("kadi.records.purge_record", args=(record.id,))


def clean_files(inside_task=False):
    """Clean all deleted and expired files.

    Note that this function may issue one or more database commits.

    :param inside_task: (optional) A flag indicating whether the function is executed in
        a task. In that case, additional information will be logged.
    """

    # Delete expired and inactive uploads.
    active_expiration_date = utcnow() - timedelta(
        seconds=current_app.config["UPLOADS_MAX_AGE"]
    )
    # Leave inactive uploads intact for at least a small amount of time, so their status
    # can always be queried if something went wrong while processing it.
    inactive_expiration_date = utcnow() - timedelta(minutes=5)
    uploads = Upload.query.filter(
        db.or_(
            db.and_(
                Upload.state == "active", Upload.last_modified < active_expiration_date
            ),
            db.and_(
                Upload.state == "inactive",
                Upload.last_modified < inactive_expiration_date,
            ),
        )
    )

    if inside_task and uploads.count() > 0:
        current_app.logger.info(
            f"Deleting {uploads.count()} expired or inactive upload(s)."
        )

    remove_uploads(uploads)

    # Delete expired temporary files.
    expiration_date = utcnow() - timedelta(
        seconds=current_app.config["TEMPORARY_FILES_MAX_AGE"]
    )
    temporary_files = TemporaryFile.query.filter(
        TemporaryFile.last_modified < expiration_date
    )

    if inside_task and temporary_files.count() > 0:
        current_app.logger.info(
            f"Deleting {temporary_files.count()} expired temporary file(s)."
        )

    remove_temporary_files(temporary_files)

    # Delete expired inactive files.
    expiration_date = utcnow() - timedelta(
        seconds=current_app.config["INACTIVE_FILES_MAX_AGE"]
    )
    files = File.query.filter(
        File.state == "inactive", File.last_modified < expiration_date
    )

    if inside_task and files.count() > 0:
        current_app.logger.info(f"Deleting {files.count()} inactive file(s).")

    remove_files(files, delete_from_db=False)


@celery.task(name="kadi.records.clean_files")
def _clean_files_task(**kwargs):
    clean_files(inside_task=True)
