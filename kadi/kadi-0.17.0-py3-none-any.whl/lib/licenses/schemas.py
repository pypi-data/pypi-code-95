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
from marshmallow import fields
from marshmallow import ValidationError

from kadi.lib.conversion import strip
from kadi.lib.licenses.models import License
from kadi.lib.schemas import KadiSchema
from kadi.lib.schemas import NonEmptyString


def _validate_license_name(name):
    if License.query.filter_by(name=name).first() is None:
        raise ValidationError("Not a valid license.")


class LicenseSchema(KadiSchema):
    """Schema to represent licenses.

    See :class:`.License`.
    """

    name = NonEmptyString(
        required=True, filters=[strip], validate=_validate_license_name
    )

    title = fields.String(dump_only=True)

    url = fields.String(dump_only=True)
