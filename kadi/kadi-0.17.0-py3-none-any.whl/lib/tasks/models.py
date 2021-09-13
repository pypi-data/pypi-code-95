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
from uuid import uuid4

from flask_babel import gettext as _
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID

from kadi.ext.db import db
from kadi.lib.db import composite_index
from kadi.lib.db import generate_check_constraints
from kadi.lib.db import TimestampMixin
from kadi.lib.utils import SimpleReprMixin


class Task(SimpleReprMixin, TimestampMixin, db.Model):
    """Model to represent tasks."""

    class Meta:
        """Container to store meta class attributes."""

        representation = ["id", "user_id", "name", "state"]
        """See :class:`.SimpleReprMixin`."""

        check_constraints = {
            "state": {
                "values": ["pending", "running", "revoked", "success", "failure"],
            },
            "progress": {"range": {"min": 0, "max": 100}},
        }
        """See :func:`kadi.lib.db.generate_check_constraints`."""

    __tablename__ = "task"

    __table_args__ = generate_check_constraints(Meta.check_constraints) + (
        composite_index("user_id", "name", "state"),
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    """The ID of the task, auto incremented."""

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    """The ID of the user that started the task."""

    name = db.Column(db.Text, nullable=False)
    """The name/type of the task."""

    arguments = db.Column(JSONB, nullable=False)
    """The arguments of the task.

    Stored in the following form as JSON:

    .. code-block:: js

        {
            "args": ["value_1"],
            "kwargs": {"arg_2": "value_2"},
        }
    """

    progress = db.Column(db.Integer, default=0, nullable=False)
    """The progress of the task.

    Needs to be an integer value between 0 and 100.
    """

    result = db.Column(JSONB, nullable=True)
    """The optional result of the task, depending on the type of task."""

    state = db.Column(db.Text, index=True, nullable=False)
    """The state of the task.

    One of ``"pending"``, ``"running"``, ``"revoked"``, ``"success"`` or ``"failure"``.
    """

    creator = db.relationship("User", back_populates="tasks")

    @property
    def is_revoked(self):
        """Check if a task is revoked.

        Will always refresh the task object to get up to date values, as revoking
        usually happens outside the current database session context (e.g. in another
        process).
        """
        db.session.refresh(self)
        return self.state == "revoked"

    @property
    def pretty_state(self):
        """Return the state of a task in a human-readable and translated format."""
        if self.state == "pending":
            return _("Pending")
        if self.state == "running":
            return _("Running")
        if self.state == "success":
            return _("Success")
        if self.state == "failure":
            return _("Failure")
        if self.state == "revoked":
            return _("Revoked")

        return _("Unknown")

    @classmethod
    def create(cls, *, creator, name, args=None, kwargs=None, state="pending"):
        """Create a new task and add it to the database session.

        :param creator: The user that started the task.
        :param name: The name/type of the task.
        :param args: (optional) The positional arguments of the task as list.
        :param kwargs: (optional) The keyword arguments of the task as dictionary.
        :param state: (optional) The state of the task.
        :return: The new :class:`.Task` object.
        """
        arguments = {
            "args": args if args is not None else [],
            "kwargs": kwargs if kwargs is not None else {},
        }

        task = cls(creator=creator, name=name, arguments=arguments, state=state)

        db.session.add(task)
        return task

    def revoke(self):
        """Revoke a task.

        Changes the task's state to ``"revoked"`` if the task is still ``"pending"`` or
        ``"running"``.
        """
        if self.state in ["pending", "running"]:
            self.state = "revoked"

    def update_progress(self, percent):
        """Update a tasks progress.

        :param percent: The progress in percent, which needs to be an integer or float
            value between 0 and 100.
        """
        if 0 <= percent <= 100:
            self.progress = int(percent)
