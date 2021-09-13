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
import math
from mimetypes import guess_type
from uuid import uuid4

from flask import current_app
from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError

from .extras import ExtrasJSONB
from kadi.ext.db import db
from kadi.lib.db import generate_check_constraints
from kadi.lib.db import TimestampMixin
from kadi.lib.db import unique_constraint
from kadi.lib.search.core import SearchableMixin
from kadi.lib.tags.core import TaggingMixin
from kadi.lib.utils import SimpleReprMixin


class Record(SimpleReprMixin, SearchableMixin, TimestampMixin, TaggingMixin, db.Model):
    """Model to represent records."""

    class Meta:
        """Container to store meta class attributes."""

        representation = ["id", "user_id", "identifier", "visibility", "state"]
        """See :class:`.SimpleReprMixin`."""

        search_mapping = "kadi.modules.records.mappings.RecordMapping"
        """See :class:`.SearchableMixin`."""

        revision = [
            "identifier",
            "title",
            "type",
            "description",
            "extras",
            "visibility",
            "state",
            "license[name]",
            "tags[name]",
        ]
        """See :func:`kadi.lib.revisions.core.setup_revisions`."""

        permissions = {
            "actions": [
                ("read", "View this record and its files."),
                ("update", "Edit this record and its files."),
                ("link", "Manage links of this record with other resources."),
                ("permissions", "Manage permissions of this record."),
                ("delete", "Delete this record."),
            ],
            "roles": [
                ("member", ["read"]),
                ("editor", ["read", "update", "link"]),
                ("admin", ["read", "update", "link", "permissions", "delete"]),
            ],
            "global_actions": [
                ("create", "Create records."),
                ("read", "View any record and its files."),
                ("update", "Edit any record and its files."),
                ("link", "Manage links of any record with other resources."),
                ("permissions", "Manage permissions of any record."),
                ("delete", "Delete any record."),
            ],
            "default_permissions": {"read": {"visibility": "public"}},
        }
        """Possible permissions and roles for records.

        See :mod:`kadi.modules.permissions`.
        """

        check_constraints = {
            "identifier": {"length": {"max": 50}},
            "title": {"length": {"max": 150}},
            "type": {"length": {"max": 50}},
            "description": {"length": {"max": 10000}},
            "state": {"values": ["active", "deleted", "purged"]},
            "visibility": {"values": ["private", "public"]},
        }
        """See :func:`kadi.lib.db.generate_check_constraints`."""

    __tablename__ = "record"

    __table_args__ = generate_check_constraints(Meta.check_constraints)

    id = db.Column(db.Integer, primary_key=True)
    """The ID of the record, auto incremented."""

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    """The ID of the user that created the record."""

    identifier = db.Column(db.Text, index=True, unique=True, nullable=False)
    """The unique identifier of the record.

    Restricted to a maximum length of 50 characters.
    """

    title = db.Column(db.Text, nullable=False)
    """The title of the record.

    Restricted to a maximum length of 150 characters.
    """

    type = db.Column(db.Text, nullable=True)
    """The optional type of the record.

    Restricted to a maximum length of 50 characters.
    """

    description = db.Column(db.Text, nullable=False)
    """The description of the record.

    Restricted to a maximum length of 10000 characters.
    """

    plain_description = db.Column(db.Text, nullable=False)
    """The plain description of the record.

    Equal to the normal description with the difference that most markdown is stripped
    out.
    """

    license_id = db.Column(db.Integer, db.ForeignKey("license.id"), nullable=True)
    """The ID of the optional license of the record."""

    extras = db.Column(ExtrasJSONB, nullable=False)
    """The extra metadata of the record.

    The extras are stored in JSON format as an array of objects. Each object contains
    some or all of the following properties:

    * **type**: The type of the extra, which is always present and is one of ``"str"``,
      ``"int"``, ``"float"``, ``"bool"``, ``"date"``, ``"dict"`` or ``"list"``.
      Dictionaries and lists contain nested values, the only difference between these
      types is that list values have no keys.
    * **key**: The key of the extra as string, which needs to be unique inside each
      array. Except for list values, it always needs to be present.
    * **value**: The value of the extra depending on its type. Defaults to ``null`` for
      simple values and an empty array for nested types.
    * **unit**: The optional unit of the value, which is only present when the type is
      one of ``"int"`` or ``"float"``. Defaults to ``null``.
    * **validation**: An object containing additional validation instructions for the
      values of non-nested types. Currently, ``"required"`` and ``"options"`` are
      supported.
    """

    visibility = db.Column(db.Text, index=True, nullable=False)
    """The default visibility of the record.

    One of ``"private"`` or ``"public"``.
    """

    state = db.Column(db.Text, index=True, nullable=False)
    """The state of the record.

    One of ``"active"``, ``"deleted"`` or ``"purged"``.
    """

    creator = db.relationship("User", back_populates="records")

    license = db.relationship("License", back_populates="records")

    files = db.relationship("File", lazy="dynamic", back_populates="record")

    tags = db.relationship(
        "Tag", secondary="record_tag", lazy="dynamic", back_populates="records"
    )

    collections = db.relationship(
        "Collection",
        secondary="record_collection",
        lazy="dynamic",
        back_populates="records",
    )

    links_to = db.relationship(
        "RecordLink",
        lazy="dynamic",
        back_populates="record_from",
        foreign_keys="RecordLink.record_from_id",
        cascade="all, delete-orphan",
    )

    linked_from = db.relationship(
        "RecordLink",
        lazy="dynamic",
        back_populates="record_to",
        foreign_keys="RecordLink.record_to_id",
        cascade="all, delete-orphan",
    )

    @property
    def active_files(self):
        """Get all active files of a record as a query."""
        return self.files.filter(File.state == "active")

    @classmethod
    def create(
        cls,
        *,
        creator,
        identifier,
        title,
        type=None,
        description="",
        plain_description="",
        license=None,
        extras=None,
        visibility="private",
        state="active",
    ):
        """Create a new record and add it to the database session.

        :param creator: The user that created the record.
        :param identifier: The unique identifier of the record.
        :param title: The title of the record.
        :param type: (optional) The type of the record.
        :param description: (optional) The description of the record.
        :param plain_description: (optional) The plain description of the record.
        :param license: (optional) The license of the record.
        :param extras: (optional) The extra metadata of the record.
        :param visibility: (optional) The default visibility of the record.
        :param state: (optional) The state of the record.
        :return: The new :class:`.Record` object.
        """
        extras = extras if extras is not None else []

        record = cls(
            creator=creator,
            identifier=identifier,
            title=title,
            type=type,
            description=description,
            plain_description=plain_description,
            license=license,
            extras=extras,
            visibility=visibility,
            state=state,
        )

        db.session.add(record)
        return record


class RecordLink(SimpleReprMixin, TimestampMixin, db.Model):
    """Model to represent directional links between records containing metadata."""

    class Meta:
        """Container to store meta class attributes."""

        representation = ["id", "name", "record_from_id", "record_to_id"]
        """See :class:`.SimpleReprMixin`."""

        check_constraints = {
            "name": {"length": {"max": 150}},
        }
        """See :func:`kadi.lib.db.generate_check_constraints`."""

    __tablename__ = "record_link"

    __table_args__ = generate_check_constraints(Meta.check_constraints)

    id = db.Column(db.Integer, primary_key=True)
    """The ID of the link, auto incremented."""

    name = db.Column(db.Text, nullable=False)
    """The name or type of the link.

    Restricted to a maximum length of 150 characters.
    """

    record_from_id = db.Column(db.Integer, db.ForeignKey("record.id"), nullable=False)
    """The ID of the record the link points from."""

    record_to_id = db.Column(db.Integer, db.ForeignKey("record.id"), nullable=False)
    """The ID of the record the link points to."""

    record_from = db.relationship(
        "Record", foreign_keys=record_from_id, back_populates="links_to"
    )

    record_to = db.relationship(
        "Record", foreign_keys=record_to_id, back_populates="linked_from"
    )

    @classmethod
    def create(cls, *, name, record_from, record_to):
        """Create a new record link and add it to the database session.

        :param name: The name or type of the link.
        :param record_from: The record the link points from.
        :param record_to: The record the link points to.
        :return: The new :class:`.RecordLink` object.
        """
        record_link = cls(name=name, record_from=record_from, record_to=record_to)

        db.session.add(record_link)
        return record_link


class File(SimpleReprMixin, TimestampMixin, db.Model):
    """Model to represent files belonging to records."""

    class Meta:
        """Container to store meta class attributes."""

        representation = [
            "id",
            "user_id",
            "record_id",
            "name",
            "size",
            "mimetype",
            "state",
        ]
        """See :class:`.SimpleReprMixin`."""

        revision = ["name", "size", "mimetype", "checksum", "state"]
        """See :func:`kadi.lib.revisions.core.setup_revisions`."""

        check_constraints = {
            "name": {"length": {"max": 256}},
            "size": {"range": {"min": 0}},
            "mimetype": {"length": {"max": 256}},
            "state": {"values": ["active", "inactive", "deleted"]},
            "checksum": {"length": {"max": 256}},
            "storage_type": {"values": ["local"]},
        }
        """See :func:`kadi.lib.db.generate_check_constraints`."""

    __tablename__ = "file"

    __table_args__ = generate_check_constraints(Meta.check_constraints) + (
        Index(
            "uq_file_record_id_name",
            "record_id",
            "name",
            unique=True,
            postgresql_where=Column("state") == "active",
        ),
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    """The UUID of the file."""

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    """The ID of the user that created the file."""

    record_id = db.Column(db.Integer, db.ForeignKey("record.id"), nullable=False)
    """The ID of the record the file belongs to."""

    name = db.Column(db.Text, nullable=False)
    """The name of the file.

    Restricted to a maximum length of 256 characters.
    """

    size = db.Column(db.BigInteger, nullable=False)
    """The size of the file in bytes.

    Must be a value >= 0.
    """

    checksum = db.Column(db.Text, nullable=True)
    """MD5 checksum to verify the integrity of the file.

    Restricted to a maximum length of 256 characters.
    """

    mimetype = db.Column(db.Text, nullable=False)
    """Regular MIME type of the file, possibly user-provided.

    Restricted to a maximum length of 256 characters.
    """

    magic_mimetype = db.Column(db.Text, nullable=True)
    """MIME type based on magic numbers in a file's content."""

    storage_type = db.Column(db.Text, nullable=False)
    """Storage type of the file.

    Currently only ``"local"``.
    """

    state = db.Column(db.Text, index=True, nullable=False)
    """The state of the file.

    One of ``"active"``, ``"inactive"`` or ``"deleted"``.
    """

    creator = db.relationship("User", back_populates="files")

    record = db.relationship("Record", back_populates="files")

    @classmethod
    def create(
        cls,
        *,
        creator,
        record,
        name,
        size,
        checksum=None,
        mimetype="application/octet-stream",
        magic_mimetype=None,
        storage_type="local",
        state="inactive",
    ):
        """Create a new file and add it to the database session.

        :param creator: The user that created the file.
        :param record: The record the file belongs to.
        :param name: The name of the file.
        :param size: The size of the file in bytes.
        :param checksum: (optional) The checksum of the file.
        :param mimetype: (optional) The regular MIME type of the file.
        :param magic_mimetype: (optional) The MIME type of the file based on its
            content.
        :param storage_type: (optional) The storage type of the file.
        :param state: (optional) The state of the file.
        :return: The new :class:`.File` object.
        """
        file = cls(
            creator=creator,
            record=record,
            name=name,
            size=size,
            checksum=checksum,
            mimetype=mimetype,
            magic_mimetype=magic_mimetype,
            storage_type=storage_type,
            state=state,
        )

        db.session.add(file)
        return file


class TemporaryFile(SimpleReprMixin, TimestampMixin, db.Model):
    """Model to represent temporary files."""

    class Meta:
        """Container to store meta class attributes."""

        representation = [
            "id",
            "user_id",
            "record_id",
            "type",
            "name",
            "size",
            "mimetype",
            "state",
        ]
        """See :class:`.SimpleReprMixin`."""

        check_constraints = {
            "name": {"length": {"max": 256}},
            "size": {"range": {"min": 0}},
            "mimetype": {"length": {"max": 256}},
            "state": {"values": ["active", "inactive"]},
        }
        """See :func:`kadi.lib.db.generate_check_constraints`."""

    __tablename__ = "temporary_file"

    __table_args__ = generate_check_constraints(Meta.check_constraints)

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    """The UUID of the temporary file."""

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    """The ID of the user that created the temporary file."""

    record_id = db.Column(db.Integer, db.ForeignKey("record.id"), nullable=False)
    """The ID of the record the temporary file belongs to."""

    type = db.Column(db.Text, nullable=True)
    """The optional type of the temporary file."""

    name = db.Column(db.Text, nullable=False)
    """The name of the temporary file.

    Restricted to a maximum length of 256 characters.
    """

    size = db.Column(db.BigInteger, nullable=False)
    """The size of the temporary file in bytes.

    Must be a value >= 0.
    """

    mimetype = db.Column(db.Text, nullable=False)
    """MIME type of the temporary file.

    Restricted to a maximum length of 256 characters.
    """

    state = db.Column(db.Text, index=True, nullable=False)
    """The state of the temporary file.

    One of ``"active"`` or ``"inactive"``.
    """

    creator = db.relationship("User", back_populates="temporary_files")

    # Not a linked relationship, so the timestamp of a related record does not
    # automatically update when the collection changes.
    record = db.relationship("Record")

    @classmethod
    def create(
        cls, *, creator, record, name, size, type=None, mimetype=None, state="inactive"
    ):
        """Create a new temporary file and add it to the database session.

        :param creator: The user that created the temporary file.
        :param record: The record the temporary file belongs to.
        :param name: The name of the temporary file.
        :param size: The size of the temporary file in bytes.
        :param type: (optional) The type of the temporary file.
        :param mimetype: (optional) The MIME type of the temporary file. Defaults to a
            MIME type based on the filename or ``"application/octet-stream"`` if it
            cannot be guessed.
        :param state: (optional) The state of the temporary file.
        :return: The new :class:`.TemporaryFile` object.
        """
        if mimetype is None:
            mimetype = guess_type(name)[0] or "application/octet-stream"

        temporary_file = cls(
            creator=creator,
            record=record,
            name=name,
            size=size,
            type=type,
            mimetype=mimetype,
            state=state,
        )

        db.session.add(temporary_file)
        return temporary_file


class Upload(SimpleReprMixin, TimestampMixin, db.Model):
    """Model to represent uploads of local files belonging to records."""

    class Meta:
        """Container to store meta class attributes."""

        representation = [
            "id",
            "user_id",
            "record_id",
            "file_id",
            "name",
            "chunk_count",
            "size",
            "mimetype",
            "state",
        ]
        """See :class:`.SimpleReprMixin`."""

        check_constraints = {
            "name": {"length": {"max": 256}},
            "size": {"range": {"min": 0}},
            "chunk_count": {"range": {"min": 1}},
            "mimetype": {"length": {"max": 256}},
            "state": {"values": ["active", "inactive", "processing"]},
            "checksum": {"length": {"max": 256}},
        }
        """See :func:`kadi.lib.db.generate_check_constraints`."""

    __tablename__ = "upload"

    __table_args__ = generate_check_constraints(Meta.check_constraints)

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    """The UUID of the upload."""

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    """The ID of the user that initiated the upload."""

    record_id = db.Column(db.Integer, db.ForeignKey("record.id"), nullable=False)
    """The ID of the record the upload belongs to."""

    file_id = db.Column(UUID(as_uuid=True), db.ForeignKey("file.id"), nullable=True)
    """The ID of a file to be overwritten the upload belongs to."""

    name = db.Column(db.Text, nullable=False)
    """The filename of the upload.

    Restricted to a maximum length of 256 characters.
    """

    chunk_count = db.Column(db.Integer, nullable=False)
    """Number of chunks an upload is split into.

    Must be a value >= 1.
    """

    size = db.Column(db.BigInteger, nullable=False)
    """The total size of the upload in bytes.

    Must be a value >= 0.
    """

    checksum = db.Column(db.Text, nullable=True)
    """Optional MD5 checksum to verify the integrity of the upload.

    Restricted to a maximum length of 256 characters.
    """

    mimetype = db.Column(db.Text, nullable=False)
    """MIME type of the upload, possibly user-provided.

    Restricted to a maximum length of 256 characters.
    """

    state = db.Column(db.Text, index=True, nullable=False)
    """The state of the upload.

    One of ``"active"``,  ``"inactive"`` or ``"processing"``.
    """

    creator = db.relationship("User", back_populates="uploads")

    # Not a linked relationship, so the timestamp of a related record does not
    # automatically update when the collection changes.
    record = db.relationship("Record")

    # Not a linked relationship, so the timestamp of a related file does not
    # automatically update when the collection changes.
    file = db.relationship("File")

    chunks = db.relationship("Chunk", lazy="dynamic", back_populates="upload")

    @property
    def active_chunks(self):
        """Get all active chunks of an upload as query."""
        return self.chunks.filter(Chunk.state == "active")

    @classmethod
    def create(
        cls,
        *,
        creator,
        record,
        name,
        size,
        file=None,
        chunk_count=None,
        checksum=None,
        mimetype="application/octet-stream",
        state="active",
    ):
        """Create a new upload and add it to the database session.

        :param creator: The user that initiated the upload.
        :param record: The record the upload belongs to.
        :param name: The name of the upload.
        :param size: The total size of the upload in bytes.
        :param file: (optional) A file the upload should replace.
        :param chunk_count: (optional) The number of chunks of the upload. If not
            provided explicitely it will be calculated based on the upload's size and
            the chunk size configured in the application's configuration.
        :param checksum: (optional) The checksum of the upload.
        :param mimetype: (optional) The MIME type of the upload.
        :param state: The state of the upload.
        :return: The new :class:`.Upload` object.
        """
        if chunk_count is None:
            chunksize = current_app.config["UPLOAD_CHUNK_SIZE"]
            chunk_count = math.ceil(size / chunksize) if size > 0 else 1

        upload = cls(
            record=record,
            creator=creator,
            name=name,
            size=size,
            file=file,
            chunk_count=chunk_count,
            checksum=checksum,
            mimetype=mimetype,
            state=state,
        )

        db.session.add(upload)
        return upload


class Chunk(SimpleReprMixin, db.Model):
    """Model to represent file chunks."""

    class Meta:
        """Container to store meta class attributes."""

        representation = ["id", "upload_id", "index", "size", "state"]
        """See :class:`.SimpleReprMixin`."""

        check_constraints = {
            "state": {"values": ["active", "inactive"]},
            "index": {"range": {"min": 0}},
            "size": {"range": {"min": 0}},
        }
        """See :func:`kadi.lib.db.generate_check_constraints`."""

    __tablename__ = "chunk"

    __table_args__ = generate_check_constraints(Meta.check_constraints) + (
        unique_constraint("chunk", "upload_id", "index"),
    )

    id = db.Column(db.Integer, primary_key=True)
    """The ID of the chunk, auto incremented."""

    upload_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("upload.id"), nullable=False
    )
    """The ID of the upload the chunk belongs to."""

    index = db.Column(db.Integer, nullable=False)
    """The index of the chunk inside its upload.

    Must be a value >= 0.
    """

    size = db.Column(db.Integer, nullable=False)
    """The size of the chunk in bytes.

    Must be a value >= 0.
    """

    state = db.Column(db.Text, default="inactive", index=True, nullable=False)
    """The state of the chunk.

    One of ``"active"`` or ``"inactive"``.
    """

    upload = db.relationship("Upload", back_populates="chunks")

    @classmethod
    def create(cls, *, upload, index, size, state="inactive"):
        """Create a new chunk and add it to the database session.

        :param upload: The upload the chunk belongs to.
        :param index: The index of the chunk.
        :param size: The size of the chunk in bytes.
        :param state: (optional) The state of the chunk.
        :return: The new :class:`.Chunk` object.
        """
        chunk = cls(upload=upload, index=index, size=size, state=state)

        db.session.add(chunk)
        return chunk

    @classmethod
    def update_or_create(cls, *, upload, index, size, state="inactive"):
        """Update an existing chunk or create one if it does not exist yet.

        :param upload: The upload the chunk belongs to.
        :param index: The index of the chunk.
        :param size: The size of the chunk in bytes.
        :param state: (optional) The state of the chunk.
        :return: The new or updated :class:`.Chunk` object.
        """
        chunk_query = cls.query.filter_by(upload=upload, index=index)
        chunk = chunk_query.first()

        if not chunk:
            # Start a new savepoint, so only the latest changes are rolled back if
            # necessary.
            db.session.begin_nested()
            chunk = cls.create(upload=upload, index=index, size=size, state=state)

            try:
                # Release the savepoint, the new chunk is not actually committed yet.
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

                chunk = chunk_query.first()
                chunk.size = size
                chunk.state = state
        else:
            chunk.size = size
            chunk.state = state

        return chunk


# Auxiliary table to link records with collections.
db.Table(
    "record_collection",
    db.Column("record_id", db.Integer, db.ForeignKey("record.id"), primary_key=True),
    db.Column(
        "collection_id", db.Integer, db.ForeignKey("collection.id"), primary_key=True
    ),
)


# Auxiliary table for record tags.
db.Table(
    "record_tag",
    db.Column("record_id", db.Integer, db.ForeignKey("record.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)
