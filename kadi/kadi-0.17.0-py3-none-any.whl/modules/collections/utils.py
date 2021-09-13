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
from flask_login import current_user

from .models import Collection
from kadi.modules.permissions.core import get_permitted_objects
from kadi.modules.records.models import Record


def get_parent_collections(collection, user=None):
    """Get all parents of a collection that a user can access.

    In this context having access to a collection means having read permission for it.
    Note that as soon as a parent collection is not accessible or inactive, no further
    potential parents are collected.

    :param collection: The collection to get the parents of.
    :param user: (optional) The user to check for access permissions when retrieving the
        collections. Defaults to the current user.
    :return: A list of parent collections starting with the immediate parent of the
        given collection.
    """
    user = user if user is not None else current_user

    collection_ids_query = (
        get_permitted_objects(user, "read", "collection")
        .filter(Collection.state == "active")
        .with_entities(Collection.id)
    )
    collection_ids = {c.id for c in collection_ids_query}

    parents = []
    current_parent = collection.parent

    while current_parent is not None:
        if current_parent.id not in collection_ids:
            return parents

        parents.append(current_parent)
        current_parent = current_parent.parent

    return parents


def get_child_collections(collection, user=None):
    """Recursively get all children of a collection that a user can access.

    In this context having access to a collection means having read permission for it.
    Note that if a collection is not accessible or inactive, no further potential
    children of this collection are collected.

    :param collection: The collection to get the children of.
    :param user: (optional) The user to check for access permissions when retrieving the
        collections. Defaults to the current user.
    :return: A list of child collections in unspecified order.
    """
    user = user if user is not None else current_user

    collection_ids_query = (
        get_permitted_objects(user, "read", "collection")
        .filter(Collection.state == "active")
        .with_entities(Collection.id)
    )
    collection_ids = {c.id for c in collection_ids_query}

    children = []
    collections_to_process = [collection]

    while collections_to_process:
        current_collection = collections_to_process.pop()

        for child in current_collection.children:
            if child.id not in collection_ids:
                continue

            children.append(child)
            collections_to_process.append(child)

    return children


def get_child_collection_records(collection, actions=None, user=None):
    """Recursively get all records of a collection hierarchy that a user can access.

    In this context, the collection hierarchy refers to the given collection and all its
    direct or indirect children. Having access to a child collection or record means
    having read permission for it.

    Uses :func:`get_child_collections` to determine the children of the given
    collection.

    :param collection: The collection to get the children and records of.
    :param actions: (optional) Further actions to check the access permissions of the
        records for.
    :param user: (optional) The user to check for access permissions when retrieving the
        collections and records. Defaults to the current user.
    :return: The records as query. Note that duplicate records are already filtered out.
    """
    actions = actions if actions is not None else []
    user = user if user is not None else current_user

    child_collections = get_child_collections(collection, user=user)
    collection_ids = [collection.id] + [c.id for c in child_collections]

    records_query = get_permitted_objects(user, "read", "record").filter(
        Record.state == "active"
    )

    for action in set(actions):
        records_query = get_permitted_objects(user, action, "record").intersect(
            records_query
        )

    return (
        records_query.join(Record.collections)
        .filter(Collection.id.in_(collection_ids))
        .distinct()
    )
