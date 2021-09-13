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
from sqlalchemy.exc import IntegrityError

from kadi.ext.db import db
from kadi.lib.db import generate_check_constraints
from kadi.lib.utils import SimpleReprMixin


class Tag(SimpleReprMixin, db.Model):
    """Model to represent object tags."""

    class Meta:
        """Container to store meta class attributes."""

        representation = ["id", "name"]
        """See :class:`.SimpleReprMixin`."""

        check_constraints = {
            "name": {"length": {"max": 50}},
        }
        """See :func:`kadi.lib.db.generate_check_constraints`."""

    __tablename__ = "tag"

    __table_args__ = generate_check_constraints(Meta.check_constraints)

    id = db.Column(db.Integer, primary_key=True)
    """The ID of the tag, auto incremented."""

    name = db.Column(db.Text, index=True, unique=True, nullable=False)
    """The unique name of the tag.

    Restricted to a maximum length of 50 characters.
    """

    records = db.relationship(
        "Record", secondary="record_tag", lazy="dynamic", back_populates="tags"
    )

    collections = db.relationship(
        "Collection", secondary="collection_tag", lazy="dynamic", back_populates="tags"
    )

    @classmethod
    def create(cls, *, name):
        """Create a new tag and add it to the database session.

        :param name: The name of the tag.
        :return: The new :class:`.Tag` object.
        """
        tag = cls(name=name)
        db.session.add(tag)
        return tag

    @classmethod
    def get_or_create(cls, name):
        """Return an existing tag or create one if it does not exist yet.

        :param name: The name of the tag.
        :return: The new or existing :class:`.Tag` object.
        """
        tag_query = cls.query.filter_by(name=name)
        tag = tag_query.first()

        if not tag:
            # Start a new savepoint, so only the latest changes are rolled back if
            # necessary.
            db.session.begin_nested()
            tag = cls.create(name=name)

            try:
                # Release the savepoint, the new tag is not actually committed yet.
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return tag_query.first()

        return tag
