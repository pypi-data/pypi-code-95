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
from flask_babel import lazy_gettext as _l
from wtforms import BooleanField
from wtforms import FileField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Length

from .models import Group
from kadi.lib.conversion import lower
from kadi.lib.conversion import normalize
from kadi.lib.conversion import strip
from kadi.lib.forms import check_duplicate_identifier
from kadi.lib.forms import DynamicMultiSelectField
from kadi.lib.forms import KadiForm
from kadi.lib.forms import LFTextAreaField
from kadi.lib.forms import validate_identifier


class BaseGroupForm(KadiForm):
    """Base form class for use in creating or updating groups."""

    title = StringField(
        _l("Title"),
        filters=[normalize],
        validators=[
            DataRequired(),
            Length(max=Group.Meta.check_constraints["title"]["length"]["max"]),
        ],
    )

    identifier = StringField(
        _l("Identifier"),
        filters=[lower, strip],
        validators=[
            DataRequired(),
            Length(max=Group.Meta.check_constraints["identifier"]["length"]["max"]),
            validate_identifier,
        ],
        description=_l("Unique identifier of this group."),
    )

    description = LFTextAreaField(
        _l("Description"),
        validators=[
            Length(max=Group.Meta.check_constraints["description"]["length"]["max"])
        ],
    )

    visibility = SelectField(
        _l("Visibility"),
        choices=[
            (v, v.capitalize())
            for v in Group.Meta.check_constraints["visibility"]["values"]
        ],
        description=_l(
            "Public visibility automatically grants any logged-in user read permissions"
            " for this group. More fine-grained permissions can be specified"
            " separately."
        ),
    )

    image = FileField(_l("Image"))


class NewGroupForm(BaseGroupForm):
    """A form for use in creating new groups."""

    submit = SubmitField(_l("Create group"))

    def validate_identifier(self, identifier):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(identifier, Group)


class EditGroupForm(BaseGroupForm):
    """A form for use in editing existing groups.

    :param group: The group to edit, used for prefilling the form.
    """

    remove_image = BooleanField(_l("Remove current image"))

    submit = SubmitField(_l("Save changes"))

    submit_quit = SubmitField(_l("Save changes and quit"))

    def __init__(self, group, *args, **kwargs):
        self.group = group
        super().__init__(*args, obj=group, **kwargs)

    def validate_identifier(self, identifier):
        # pylint: disable=missing-function-docstring
        check_duplicate_identifier(identifier, Group, exclude=self.group)


class AddMembersForm(KadiForm):
    """A form for use in adding members (i.e. user roles) to a group."""

    users = DynamicMultiSelectField(_l("Users"), coerce=int)

    role = SelectField(
        _l("Role"),
        choices=[(r, r.capitalize()) for r, _ in Group.Meta.permissions["roles"]],
    )

    submit = SubmitField(_l("Add members"))

    def validate(self, extra_validators=None):
        success = super().validate(extra_validators=extra_validators)

        if success and self.users.data:
            return True

        return False
