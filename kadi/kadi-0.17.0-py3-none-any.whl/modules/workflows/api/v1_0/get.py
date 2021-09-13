# Copyright 2021 Karlsruhe Institute of Technology
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
from flask_login import login_required

from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import json_response
from kadi.lib.api.core import scopes_required
from kadi.lib.api.utils import create_pagination_data
from kadi.lib.api.utils import status
from kadi.lib.conversion import normalize
from kadi.lib.web import paginated
from kadi.lib.web import qparam
from kadi.modules.records.files import get_permitted_files
from kadi.modules.records.models import File
from kadi.modules.records.schemas import FileSchema
from kadi.modules.workflows.core import parse_tool_file


@bp.get("/workflows")
@login_required
@scopes_required("record.read")
@paginated
@qparam(
    "filter",
    parse=normalize,
    description="A query to filter the workflow files by name or record identifier.",
)
@status(
    200,
    "Return a paginated list of workflow files, sorted by last modification date in"
    " descending order.",
)
def get_workflows(page, per_page, qparams):
    """Get all local workflow files.

    For convenience, each file additionally contains the identifier of its record as
    ``record_identifier``.
    """
    paginated_files = (
        get_permitted_files(term=qparams["filter"])
        .filter(
            File.storage_type == "local",
            File.magic_mimetype == "application/x-flow+json",
        )
        .order_by(File.last_modified.desc())
        .paginate(page, per_page, False)
    )

    items = [
        {"record_identifier": file.record.identifier, **FileSchema().dump(file)}
        for file in paginated_files.items
    ]
    data = {
        "items": items,
        **create_pagination_data(
            paginated_files.total, page, per_page, "api.get_workflows"
        ),
    }

    return json_response(200, data)


@bp.get("/workflows/tools")
@login_required
@scopes_required("record.read")
@paginated
@qparam(
    "filter",
    parse=normalize,
    description="A query to filter the tool files by name or record identifier.",
)
@status(
    200,
    "Return a paginated list of tool files, sorted by last modification date in"
    " descending order.",
)
def get_workflow_tools(page, per_page, qparams):
    """Get all local workflow tool files.

    For convenience, each file additionally contains the identifier of its record as
    ``record_identifier`` and the parsed tool content as ``tool``.
    """
    paginated_files = (
        get_permitted_files(term=qparams["filter"])
        .filter(
            File.storage_type == "local",
            File.magic_mimetype == "application/x-tool+xml",
        )
        .order_by(File.last_modified.desc())
        .paginate(page, per_page, False)
    )

    items = [
        {
            "record_identifier": file.record.identifier,
            "tool": parse_tool_file(file),
            **FileSchema().dump(file),
        }
        for file in paginated_files.items
    ]
    data = {
        "items": items,
        **create_pagination_data(
            paginated_files.total, page, per_page, "api.get_workflow_tools"
        ),
    }

    return json_response(200, data)
