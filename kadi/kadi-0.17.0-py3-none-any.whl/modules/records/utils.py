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

from .models import Record
from .models import RecordLink
from kadi.ext.db import db
from kadi.lib.conversion import truncate
from kadi.lib.web import url_for
from kadi.modules.permissions.core import get_permitted_objects


def get_permitted_record_links(record_or_id, direction=None, user=None):
    """Convenience function to get all links of a record that a user can access.

    In this context having access to a record link means having read permission for each
    record the given record links to or is linked from.

    :param record_or_id: The record or ID of a record whose links should be obtained.
    :param direction: (optional) A direction to limit the returned record links, one of
        ``"to"`` for (outgoing) records linked to from the given record or ``"from"``
        for (incoming) records that link to the given record.
    :param user: (optional) The user to check for access permissions. Defaults to the
        current user.
    :return: The permitted record link objects as query.
    """
    user = user if user is not None else current_user
    record_id = record_or_id.id if isinstance(record_or_id, Record) else record_or_id

    record_ids_query = (
        get_permitted_objects(user, "read", "record")
        .filter(Record.state == "active")
        .with_entities(Record.id)
    )

    # Records linked to from the given record.
    filter_to = db.and_(
        RecordLink.record_from_id == record_id,
        RecordLink.record_to_id.in_(record_ids_query),
    )
    # Records that link to the given record.
    filter_from = db.and_(
        RecordLink.record_to_id == record_id,
        RecordLink.record_from_id.in_(record_ids_query),
    )

    if direction == "to":
        filters = [filter_to]
    elif direction == "from":
        filters = [filter_from]
    else:
        filters = [filter_to, filter_from]

    return RecordLink.query.filter(db.or_(*filters))


def _append_node(nodes, record):
    nodes.append(
        {
            "id": record.id,
            "identifier": truncate(record.identifier, 25),
            "identifier_full": record.identifier,
            "type": truncate(record.type, 25),
            "type_full": record.type,
            "url": url_for("records.view_record", id=record.id),
        }
    )


def _collect_link_data(
    record_id, nodes, links, processed_record_ids, added_record_ids, user
):
    new_record_ids = set()
    link_indices = {}
    link_lengths = {}

    record_links_query = (
        get_permitted_record_links(record_id, user=user)
        .order_by(RecordLink.created_at.desc())
        .limit(100)
    )

    for record_link in record_links_query:
        # Skip all links involving records that were already checked for their links.
        if (
            record_link.record_from_id in processed_record_ids
            or record_link.record_to_id in processed_record_ids
        ):
            continue

        source = record_link.record_from
        target = record_link.record_to

        for record in [source, target]:
            new_record_ids.add(record.id)

            if record.id not in added_record_ids:
                _append_node(nodes, record)
                added_record_ids.add(record.id)

        # The link indices are used to calculate the "curve" of a link when rendering
        # it. The index of a link is increased for each link that has the same source
        # and target, starting at 1.
        link_index = 1
        key = (source.id, target.id)

        if key in link_indices:
            link_indices[key] += 1
            link_index = link_indices[key]
        else:
            link_indices[key] = link_index

        # The link lengths are used to apply varying strengths of link forces to the
        # corresponding nodes based on the length of the (truncated) link name. Only the
        # largest length between each source and target record is taken, after all links
        # have been processed.
        link_name = truncate(record_link.name, 25)
        link_length = len(link_name)
        key = (
            (source.id, target.id) if source.id < target.id else (target.id, source.id)
        )

        if key in link_lengths:
            link_lengths[key] = max(link_length, link_lengths[key])
        else:
            link_lengths[key] = link_length

        links.append(
            {
                "source": source.id,
                "target": target.id,
                "name": link_name,
                "name_full": record_link.name,
                "link_index": link_index,
                "link_length": link_length,
            }
        )

    for link in links:
        key = (
            (link["source"], link["target"])
            if link["source"] < link["target"]
            else (link["target"], link["source"])
        )

        if key in link_lengths:
            link["link_length"] = link_lengths[key]

    processed_record_ids.add(record_id)
    return new_record_ids


def get_record_links_graph(record, depth=1, user=None):
    """Get all links of a record for visualizing them in a graph.

    Used in conjunction with "d3" to visualize all returned nodes and links in a force
    directed graph.

    :param record: The record to start with.
    :param depth: (optional) The link depth.
    :param user: (optional) The user to check for access permissions regarding the
        linked records. Defaults to the current user.
    :return: A dictionary containing the record links (``"links"``) as well as all
        records involved in the links (``"nodes"``).
    """
    user = user if user is not None else current_user

    nodes = []
    links = []

    # Records to still check for their links.
    record_ids_to_process = {record.id}
    # Records already checked for their links.
    processed_record_ids = set()
    # Records already added to the node list.
    added_record_ids = set()

    # Add the start record itself to the nodes.
    _append_node(nodes, record)
    added_record_ids.add(record.id)

    for _ in range(0, depth):
        # Newly added records in the last iteration that are not processed yet.
        new_record_ids = set()

        for record_id in record_ids_to_process:
            new_record_ids |= _collect_link_data(
                record_id,
                nodes,
                links,
                processed_record_ids,
                added_record_ids,
                user,
            )

        record_ids_to_process = new_record_ids

    return {"nodes": nodes, "links": links}
