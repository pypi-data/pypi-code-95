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
from flask_login import current_user

from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import internal_endpoint
from kadi.lib.api.core import json_error_response
from kadi.lib.api.core import json_response
from kadi.lib.tasks.models import Task
from kadi.modules.permissions.utils import permission_required
from kadi.modules.records.models import Record
from kadi.modules.records.tasks import start_package_files_task


@bp.post("/records/<int:id>/files/download", v=None)
@permission_required("read", "record", "id")
@internal_endpoint
def download_record_files(id):
    """Prepare a download of all local files of a record.

    The archive to be downloaded will be created in a background task, which the user
    will be notified about.
    """
    record = Record.query.get_active_or_404(id)

    task = Task.query.filter(
        Task.name == "kadi.records.package_files",
        Task.state.in_(["pending", "running"]),
        Task.user_id == current_user.id,
    ).first()

    if task:
        return json_error_response(
            429, description=f"A packaging task is already {task.state}."
        )

    task = start_package_files_task(record)

    if not task:
        return json_error_response(503, description="Error starting packaging task.")

    return json_response(202)
