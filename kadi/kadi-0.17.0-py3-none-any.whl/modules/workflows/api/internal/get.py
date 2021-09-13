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
from flask_login import login_required

from kadi.lib.api.blueprint import bp
from kadi.lib.api.core import internal_endpoint
from kadi.lib.api.core import json_response
from kadi.lib.api.utils import create_pagination_data
from kadi.lib.conversion import normalize
from kadi.lib.web import paginated
from kadi.lib.web import qparam
from kadi.modules.records.files import get_permitted_files
from kadi.modules.records.models import File
from kadi.modules.workflows.core import parse_tool_file


@bp.get("/workflows/tools/select", v=None)
@login_required
@internal_endpoint
@paginated
@qparam("filter", parse=normalize)
def select_workflow_tools(page, per_page, qparams):
    """Select local workflow tool files.

    For use in the experimental workflow editor.
    """
    paginated_files = (
        get_permitted_files(term=qparams["filter"])
        .filter(
            File.storage_type == "local",
            File.magic_mimetype == "application/x-tool+xml",
        )
        .order_by(File.name)
        .paginate(page, per_page, False)
    )

    items = [
        {
            "id": file.id,
            "file": file.name,
            "record": file.record.identifier,
            "tool": parse_tool_file(file),
        }
        for file in paginated_files.items
    ]
    data = {
        "items": items,
        **create_pagination_data(
            paginated_files.total, page, per_page, "api.select_workflow_tools"
        ),
    }

    return json_response(200, data)
