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
from elasticsearch_dsl import Q
from flask import current_app
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from .files import remove_files
from .files import remove_temporary_files
from .models import File
from .models import Record
from .models import RecordLink
from .models import TemporaryFile
from .models import Upload
from .uploads import remove_uploads
from kadi.ext.db import db
from kadi.lib.conversion import strip_markdown
from kadi.lib.db import update_object
from kadi.lib.exceptions import KadiPermissionError
from kadi.lib.licenses.models import License
from kadi.lib.resources.utils import search_resources
from kadi.lib.revisions.core import create_revision
from kadi.lib.revisions.core import delete_revisions
from kadi.lib.tags.models import Tag
from kadi.modules.collections.models import Collection
from kadi.modules.collections.utils import get_child_collections
from kadi.modules.permissions.core import add_role
from kadi.modules.permissions.core import delete_permissions
from kadi.modules.permissions.core import get_permitted_objects
from kadi.modules.permissions.core import has_permission
from kadi.modules.permissions.core import setup_permissions
from kadi.plugins import run_hook


def create_record(
    *,
    identifier,
    title,
    creator=None,
    type=None,
    description="",
    license=None,
    extras=None,
    visibility="private",
    state="active",
    tags=None,
):
    """Create a new record.

    This will also create all default permissions of the record.

    Note that this function issues a database commit or rollback.

    :param identifier: See :attr:`.Record.identifier`.
    :param title: See :attr:`.Record.title`.
    :param creator: (optional) The user that created the record. Defaults to the
        current user.
    :param type: (optional) See :attr:`.Record.type`.
    :param description: (optional) See :attr:`.Record.description`.
    :param license: (optional) The name of the license to reference the record with. See
        also :class:`.License`.
    :param extras: (optional) See :attr:`.Record.extras`.
    :param visibility: (optional) See :attr:`.Record.visibility`.
    :param state: (optional) See :attr:`.Record.state`.
    :param tags: (optional) A list of tag names to tag the record with. See also
        :class:`.Tag`.
    :return: The created record or ``None`` if the record could not be created.
    """
    creator = creator if creator is not None else current_user
    license = License.query.filter_by(name=license).first()

    record = Record.create(
        identifier=identifier,
        title=title,
        creator=creator,
        type=type,
        description=description,
        plain_description=strip_markdown(description),
        license=license,
        extras=extras,
        visibility=visibility,
        state=state,
    )

    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        return None

    if tags is not None and not record.set_tags(tags):
        db.session.rollback()
        return False

    setup_permissions("record", record.id)
    add_role(creator, "record", record.id, "admin")

    create_revision(record, user=creator)

    db.session.commit()

    try:
        run_hook("kadi_post_record_create", record=record)
    except Exception as e:
        current_app.logger.exception(e)

    return record


def update_record(record, tags=None, **kwargs):
    r"""Update an existing record.

    Note that this function issues a database commit or rollback.

    :param record: The record to update.
    :param tags: (optional) A list of tag names to tag the record with. See also
        :class:`.Tag`.
    :param \**kwargs: Keyword arguments that will be passed to
        :func:`kadi.lib.db.update_object`. If the name of a license is given via
        ``license``, the reference to the license object will be updated accordingly.
    :return: ``True`` if the record was updated successfully, ``False`` otherwise.
    """
    if record.state != "active":
        return False

    if "description" in kwargs:
        kwargs["plain_description"] = strip_markdown(kwargs["description"])

    if kwargs.get("license") is not None:
        kwargs["license"] = License.query.filter_by(name=kwargs["license"]).first()

    update_object(record, **kwargs)

    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        return False

    if tags is not None and not record.set_tags(tags):
        db.session.rollback()
        return False

    revision_created = create_revision(record)

    db.session.commit()

    if revision_created:
        try:
            run_hook("kadi_post_record_update", record=record)
        except Exception as e:
            current_app.logger.exception(e)

    return True


def delete_record(record):
    """Delete an existing record.

    This will perform a soft deletion, i.e. the records's state will be set to
    ``"deleted"``.

    :param record: The record to delete.
    """
    if record.state == "active":
        record.state = "deleted"
        create_revision(record)


def restore_record(record):
    """Restore a deleted record.

    :param record: The record to restore.
    """
    if record.state == "deleted":
        record.state = "active"
        create_revision(record)


def purge_record(record):
    """Purge an existing record.

    This will completely delete the record from the database including all its files.

    Note that this function may issue one or more database commits.

    :param record: The record to delete.
    """
    remove_files(record.files)

    temporary_files = TemporaryFile.query.filter(TemporaryFile.record_id == record.id)
    remove_temporary_files(temporary_files)

    uploads = Upload.query.filter(Upload.record_id == record.id)
    remove_uploads(uploads)

    delete_revisions(record)
    delete_permissions("record", record.id)

    db.session.delete(record)


def link_records(name, record_from, record_to, user=None):
    """Link two records together.

    :param name: The name of the record link.
    :param record_from: The record that is being linked from.
    :param record_to: The record that is being linked to.
    :param user: (optional) The user performing the link operation. Defaults to the
        current user.
    :return: The new record link or ``None`` if it could not be created, in case both
        given records refer to the same object.
    :raises KadiPermissionError: If the user performing the operation does not have the
        necessary permissions.
    """
    user = user if user is not None else current_user

    if record_from == record_to:
        return None

    if not has_permission(user, "link", "record", record_from.id) or not has_permission(
        user, "link", "record", record_to.id
    ):
        raise KadiPermissionError("No permission to link records.")

    return RecordLink.create(name=name, record_from=record_from, record_to=record_to)


def _make_extra_key_query(extra_type, extra_key):
    should_query = []

    # Check if the value should be matched exactly.
    if extra_key.startswith('"') and extra_key.endswith('"') and len(extra_key) >= 2:
        extra_key = extra_key[1:-1]
    else:
        should_query.append(Q("match", **{f"extras_{extra_type}.key": extra_key}))

    should_query.append(Q("term", **{f"extras_{extra_type}.key.keyword": extra_key}))

    return Q("bool", should=should_query)


def _make_nested_extra_key_query(extra_type, extra_key):
    should_query = []

    # Check if the key value should be matched exactly.
    if extra_key.startswith('"') and extra_key.endswith('"') and len(extra_key) >= 2:
        extra_key = extra_key[1:-1]
    else:
        should_query.append(
            Q(
                "nested",
                path=f"extras_{extra_type}",
                query=Q("match", **{f"extras_{extra_type}.key": extra_key}),
            )
        )

    should_query.append(
        Q(
            "nested",
            path=f"extras_{extra_type}",
            query=Q("term", **{f"extras_{extra_type}.key.keyword": extra_key}),
        )
    )

    return Q("bool", should=should_query)


def _dict_to_query(query_dict):
    extra_type = str(query_dict.get("type", ""))
    extra_key = str(query_dict.get("key", ""))

    if extra_type == "str":
        str_query = []
        str_value = str(query_dict.get("str", ""))

        if str_value:
            should_query = []

            # Check if the string value should be matched exactly.
            if (
                str_value.startswith('"')
                and str_value.endswith('"')
                and len(str_value) >= 2
            ):
                str_value = str_value[1:-1]
            else:
                should_query.append(Q("match", extras_str__value=str_value))

            should_query.append(Q("term", extras_str__value__keyword=str_value))
            str_query.append(Q("bool", should=should_query))

        if extra_key:
            str_query.append(_make_extra_key_query("str", extra_key))

        return Q("nested", path="extras_str", query=Q("bool", must=str_query))

    if extra_type == "numeric":
        int_query = []
        float_query = []

        numeric_dict = query_dict.get("numeric")
        if not isinstance(numeric_dict, dict):
            numeric_dict = {}

        min_value = str(numeric_dict.get("min", ""))
        max_value = str(numeric_dict.get("max", ""))
        unit_value = str(numeric_dict.get("unit", ""))

        if min_value:
            int_query.append(Q("range", extras_int__value={"gt": min_value}))
            float_query.append(Q("range", extras_float__value={"gt": min_value}))

        if max_value:
            int_query.append(Q("range", extras_int__value={"lt": max_value}))
            float_query.append(Q("range", extras_float__value={"lt": max_value}))

        if unit_value:
            int_query.append(Q("match", extras_int__unit=unit_value))
            float_query.append(Q("match", extras_float__unit=unit_value))

        if extra_key:
            int_query.append(_make_extra_key_query("int", extra_key))
            float_query.append(_make_extra_key_query("float", extra_key))

        return Q(
            "bool",
            should=[
                Q("nested", path="extras_int", query=Q("bool", must=int_query)),
                Q("nested", path="extras_float", query=Q("bool", must=float_query)),
            ],
        )

    if extra_type == "bool":
        bool_query = []
        bool_value = str(query_dict.get("bool", ""))

        if bool_value.lower() == "true":
            bool_query.append(Q("term", extras_bool__value=True))
        elif bool_value.lower() == "false":
            bool_query.append(Q("term", extras_bool__value=False))

        if extra_key:
            bool_query.append(_make_extra_key_query("bool", extra_key))

        return Q("nested", path="extras_bool", query=Q("bool", must=bool_query))

    if extra_type == "date":
        date_query = []

        date_dict = query_dict.get("date")
        if not isinstance(date_dict, dict):
            date_dict = {}

        min_value = str(date_dict.get("min", ""))
        max_value = str(date_dict.get("max", ""))

        if min_value:
            date_query.append(Q("range", extras_date__value={"gt": min_value}))

        if max_value:
            date_query.append(Q("range", extras_date__value={"lt": max_value}))

        if extra_key:
            date_query.append(_make_extra_key_query("date", extra_key))

        return Q("nested", path="extras_date", query=Q("bool", must=date_query))

    if extra_key:
        return Q(
            "bool",
            should=[
                _make_nested_extra_key_query(extra_type, extra_key)
                for extra_type in ["str", "int", "float", "bool", "date"]
            ],
        )

    return None


def search_records(
    query,
    extras=None,
    sort="_score",
    collections=None,
    child_collections=False,
    tags=None,
    record_types=None,
    mimetypes=None,
    hide_public=False,
    page=1,
    per_page=10,
):
    """Search for and filter all records that the current user can read.

    Uses :func:`kadi.lib.resources.utils.search_resources`.

    :param query: The search query as string to search for the title, identifier and
        plain description of the record.
    :param extras: (optional) A list of dictionaries to specifiy search queries within
        the extra metadata of records. Each query can contain a link type, a key, a type
        and one or multiple values depending on the type. See also
        :attr:`.Record.extras`.

        **Example:**

        .. code-block:: python3

            [
                {
                    # The link type, one of "and" or "or". Note that the link type of
                    # the first query does not actually matter and can be left out.
                    "link": "and",
                    # The key of the metadata entry.
                    "key": "sample key",
                    # The type of the metadata entry, one of "str", "numeric", bool" or
                    # "date". Note that there are no separate types for integer and
                    # float values.
                    "type": "str",
                    # The string value of the metadata entry if the type is "str".
                    "str": "string",
                    # The numeric value of the metadata entry if the type is "numeric".
                    # Either a minimum value, a maximum value or both can be specified.
                    # Specifying a unit is optional.
                    "numeric": {"min": 0, "max": 1, "unit": "cm"},
                    # The boolean value of the metadata entry if the type is "bool", one
                    # of True, "true", False or "false".
                    "bool": True,
                    # The formatted date value of the metadata entry if the type is
                    # "date". Either a minimum value, a maximum value or both can be
                    # specified.
                    "date": {
                        "min": "2020-07-01T00:00:00.000Z",
                        "max": "2020-07-02T00:00:00.000Z",
                    },
                },
            ]

    :param sort: (optional) See :func:`kadi.lib.resources.utils.search_resources`.
    :param collections: (optional) A list of collection IDs the searched records need to
        belong to. All given collections are filtered using an *OR* operation.
    :param child_collections: (optional) Flag indicating whether the records of the
        children of the given collections should be included.
    :param tags: (optional) A list of tag names to filter the records with before
        searching. All given tags are filtered using an *OR* operation.
    :param record_types: (optional) A list of record types to filter the records with
        before searching. All given types are filtered using an *OR* operation.
    :param mimetypes: (optional) A list of MIME types to filter the records with before
        searching based on a record's files. All given MIME types are filtered using an
        *OR* operation.
    :param hide_public: (optional) Flag indicating whether to exclude records with
        public visibility.
    :param page: (optional) See :func:`kadi.lib.resources.utils.search_resources`.
    :param per_page: (optional) See :func:`kadi.lib.resources.utils.search_resources`.
    :return: The search results as returned by
        :func:`kadi.lib.resources.utils.search_resources`.
    """
    records_query = get_permitted_objects(current_user, "read", "record").filter(
        Record.state == "active"
    )

    if collections:
        if child_collections:
            collection_ids = []

            for collection in Collection.query.filter(Collection.id.in_(collections)):
                child_collections = get_child_collections(collection)
                collection_ids += [collection.id] + [c.id for c in child_collections]

            collections = collection_ids

        records_query = records_query.join(Record.collections).filter(
            Collection.id.in_(collections)
        )

    if tags:
        records_query = records_query.join(Record.tags).filter(Tag.name.in_(tags))

    if record_types:
        records_query = records_query.filter(Record.type.in_(record_types))

    if mimetypes:
        records_query = records_query.join(File).filter(
            File.mimetype.in_(mimetypes), File.state == "active"
        )

    if hide_public:
        records_query = records_query.filter(Record.visibility != "public")

    record_ids = [r.id for r in records_query.with_entities(Record.id)]
    query_str = query

    if query_str:
        base_query_params = {
            "query": query_str,
            "fields": [
                "identifier",
                "identifier.text",
                "title",
                "title.text",
                "plain_description",
            ],
        }

        exact_query = Q("multi_match", boost=5, **base_query_params)
        fuzzy_query = Q("multi_match", fuzziness="AUTO:2,6", **base_query_params)

        query = Q("bool", should=[exact_query, fuzzy_query])

    if extras:
        q_or_relations = []
        q_and_relations = []

        # Multiple queries with different link types are effectively combined as:
        # (Q1 AND Q2) OR (Q3 AND Q4). The first link type does not actually matter.
        for extra in extras:
            extra_query = _dict_to_query(extra)

            if extra_query:
                if extra.get("link") == "or":
                    if q_and_relations:
                        q_or_relations.append(Q("bool", must=q_and_relations))

                    q_and_relations = [extra_query]
                else:
                    q_and_relations.append(extra_query)

        q_or_relations.append(Q("bool", must=q_and_relations))
        extras_query = Q("bool", should=q_or_relations)

        # If both a general and extras query are given, they are combined using an AND
        # operation.
        if query_str:
            query = Q("bool", must=[query, extras_query])
        else:
            query = extras_query

    return search_resources(
        Record,
        query=query,
        sort=sort,
        filter_ids=record_ids,
        page=page,
        per_page=per_page,
    )
