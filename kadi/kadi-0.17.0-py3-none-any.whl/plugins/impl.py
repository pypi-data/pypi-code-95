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
# pylint: disable=missing-function-docstring
from flask import render_template

from kadi.modules.records.previews import _get_builtin_preview_data
from kadi.modules.workflows.core import get_custom_mimetype
from kadi.plugins import hookimpl


@hookimpl(tryfirst=True)
def kadi_get_custom_mimetype(file, base_mimetype):
    return get_custom_mimetype(file, base_mimetype)


@hookimpl(tryfirst=True)
def kadi_get_preview_data(file):
    return _get_builtin_preview_data(file)


@hookimpl(tryfirst=True)
def kadi_get_preview_templates():
    return render_template("records/snippets/preview_file.html")
