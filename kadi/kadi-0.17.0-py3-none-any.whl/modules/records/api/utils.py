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
from flask import current_app
from flask_login import current_user

from kadi.ext.db import db
from kadi.lib.api.core import json_error_response
from kadi.lib.format import filesize
from kadi.modules.records.models import File
from kadi.modules.records.models import Upload


def check_max_upload_size(size):
    """Check the maximum configured size of a single upload.

    Uses the value ``MAX_UPLOAD_SIZE`` in the application's configuration.

    :param size: The size of an upload to check.
    :return: An error response or ``None`` if the size is not exceeded.
    """
    max_size = current_app.config["MAX_UPLOAD_SIZE"]
    if max_size is not None and size > max_size:
        return json_error_response(
            413, description=f"Maximum upload size exceeded ({filesize(max_size)})."
        )

    return None


def check_upload_user_quota(user=None, additional_size=0):
    """Check the maximum configured size of a user's upload quota.

    Uses the value ``MAX_UPLOAD_USER_QUOTA`` in the application's configuration.

    :param user: (optional) The user to check the quota of. Defaults to the current
        user.
    :param additional_size: (optional) Additional size to add to or subtract from the
        user's total.
    :return: An error response or ``None`` if the size is not exceeded.
    """
    user = user if user is not None else current_user

    max_quota = current_app.config["MAX_UPLOAD_USER_QUOTA"]
    if max_quota is not None:
        total_file_size = (
            user.files.filter(File.state == "active", File.storage_type == "local")
            .with_entities(db.func.sum(File.size))
            .scalar()
        )

        # Processing uploads are taken into account as well, even if there is the
        # possibility that they might not actually finish.
        total_upload_size = (
            user.uploads.filter(Upload.state == "processing")
            .with_entities(db.func.sum(Upload.size))
            .scalar()
        )

        total_size = (total_file_size or 0) + (total_upload_size or 0)

        if (total_size + additional_size) > max_quota:
            return json_error_response(
                413,
                description=f"Maximum upload quota exceeded ({filesize(max_quota)}).",
            )

    return None
