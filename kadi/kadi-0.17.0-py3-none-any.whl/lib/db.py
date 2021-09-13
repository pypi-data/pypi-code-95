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
from datetime import timezone

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.schema import Index

from kadi.ext.db import db
from kadi.lib.utils import utcnow


class UTCDateTime(db.TypeDecorator):
    """Custom timezone aware DateTime type using UTC.

    As dates are currently saved without timezone information (and always interpreted as
    UTC), the timezone information has to be removed from datetime objects before
    persisting, as otherwise they are converted to local time. When retrieving the
    value, the timezone will be added back in.
    """

    impl = db.DateTime

    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert to UTC and then remove the timezone."""
        if value is None:
            return value

        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        """Replace the missing timezone with UTC."""
        if value is None:
            return value

        return value.replace(tzinfo=timezone.utc)


class TimestampMixin:
    """Mixin for SQLAlchemy models to add timestamp columns."""

    created_at = db.Column(UTCDateTime, default=utcnow, nullable=False)
    """The date and time an object has been created at.

    Always uses the current UTC time.
    """

    last_modified = db.Column(UTCDateTime, default=utcnow, nullable=False)
    """The date and time an object was last modified.

    After calling :meth:`register_timestamp_listener` this timestamp will automatically
    get updated if any column (including multivalued relationships) of the model using
    this mixin is updated. Always uses the current UTC time as initial value.
    """

    @classmethod
    def _before_flush_timestamp(cls, session, flush_context, instances):
        for obj in session.dirty:
            if isinstance(obj, cls) and session.is_modified(obj):
                update_timestamp = True

                # Do not update the timestamp if the state of the object (if present) is
                # not active, except for when it just changed.
                if getattr(obj, "state", "active") != "active":
                    history = db.inspect(obj).attrs.state.load_history()

                    if not history.deleted or history.deleted[0] != "active":
                        # Do not return here, as that seems to break the event chain.
                        update_timestamp = False

                if update_timestamp:
                    # Do not update the timestamp if only changes in relationships
                    # occured and none of the related objects' state (if present) is
                    # active.
                    for attr in db.inspect(obj).attrs:
                        history = attr.load_history()
                        items = list(history.added) + list(history.deleted)

                        for item in items:
                            if (
                                not isinstance(item, db.Model)
                                or getattr(item, "state", "active") == "active"
                            ):
                                obj.last_modified = utcnow()
                                break

    @classmethod
    def register_timestamp_listener(cls):
        """Register a listener to automatically update the last modification timestamp.

        Uses SQLAlchemy's ``before_flush`` event.
        """
        db.event.listen(
            db.session, "before_flush", cls._before_flush_timestamp, propagate=True
        )

    def update_timestamp(self):
        """Manually trigger an update to the last modification timestamp."""
        if getattr(self, "state", "active") == "active":
            self.last_modified = utcnow()


def update_object(obj, **kwargs):
    r"""Convenience function to update database objects.

    Only columns (i.e. attributes) that actually exist will get updated.

    :param obj: The object to update.
    :param \**kwargs: The columns to update and their respective values.
    """
    for key, value in kwargs.items():
        if hasattr(obj, key):
            setattr(obj, key, value)


def composite_index(*cols):
    r"""Generate a composite index.

    :param \*cols: The names of the columns.
    :return: The Index instance.
    """
    return Index(f"ix_{'_'.join(cols)}", *cols)


def unique_constraint(tablename, *cols):
    r"""Generate a unique constraint.

    :param tablename: The name of the table.
    :param \*cols: The names of the columns.
    :return: The UniqueConstraint instance.
    """
    return UniqueConstraint(*cols, name=f"uq_{tablename}_{'_'.join(cols)}")


def check_constraint(constraint, name):
    """Generate a check constraint.

    :param constraint: The constraint expression as string.
    :param name: The name of the constraint.
    :return: The CheckConstraint instance.
    """
    return CheckConstraint(constraint, name=f"ck_{name}")


def length_constraint(col, min_value=None, max_value=None):
    """Generate a length check constraint for a column.

    :param col: The name of the column.
    :param min_value: (optional) Minimum length.
    :param max_value: (optional) Maximum length.
    :return: The CheckConstraint instance.
    """
    constraint = ""
    if min_value is not None:
        constraint += f"char_length({col}) >= {min_value}"

    if max_value is not None:
        if min_value is not None:
            constraint += " AND "
        constraint += f"char_length({col}) <= {max_value}"

    return check_constraint(constraint, name=f"{col}_length")


def range_constraint(col, min_value=None, max_value=None):
    """Generate a range check constraint for a column.

    :param col: The name of the column.
    :param min_value: (optional) Minimum value.
    :param max_value: (optional) Maximum value.
    :return: The CheckConstraint instance.
    """
    constraint = ""

    if min_value is not None:
        constraint += f"{col} >= {min_value}"

    if max_value is not None:
        if min_value is not None:
            constraint += " AND "
        constraint += f"{col} <= {max_value}"

    return check_constraint(constraint, name=f"{col}_range")


def values_constraint(col, values):
    """Generate a values check constraint for a column.

    :param col: The name of the column.
    :param values: List of values.
    :return: The CheckConstraint instance.
    """
    values = values if values is not None else []
    values = ", ".join(f"'{value}'" for value in values)

    constraint = f"{col} IN ({values})"
    return check_constraint(constraint, name=f"{col}_values")


def generate_check_constraints(constraints):
    """Generate database check constraints.

    Supports check constraints of type ``"length"``, ``"range"`` and ``"values"``. The
    constraints have to be given in the following form:

    .. code-block:: python3

        {
            "col_1": {"length": {"min": 0, "max": 10}},
            "col_2": {"range": {"min": 0, "max": 10}},
            "col_3": {"values": ["val_1", "val_2"]},
        }

    :param constraints: Dictionary of constraints to generate.
    :return: A tuple of CheckConstraint instances.
    """
    results = []
    for col, constraint in constraints.items():
        for name, args in constraint.items():
            if name == "length":
                results.append(
                    length_constraint(
                        col, min_value=args.get("min"), max_value=args.get("max")
                    )
                )
            elif name == "range":
                results.append(
                    range_constraint(
                        col, min_value=args.get("min"), max_value=args.get("max")
                    )
                )
            elif name == "values":
                results.append(values_constraint(col, args))

    return tuple(results)


def get_class_by_tablename(tablename):
    """Get the model class mapped to a certain database table name.

    :param tablename: Name of the table.
    :return: The class reference or ``None`` if the table does not exist.
    """
    for mapper in db.Model.registry.mappers:
        if getattr(mapper.class_, "__tablename__", None) == tablename:
            return mapper.class_

    return None


def get_class_of_relationship(model, attr):
    """Get the class of a relationship.

    :param model: The model that contains the relationship.
    :param attr: Name of the relationship.
    :return: The class reference.
    """
    return getattr(model, attr).property.mapper.class_


def is_column(model, attr):
    """Check if a models attribute is a normal column.

    :param model: The model that contains the column.
    :param attr: Name of the attribute.
    :return: ``True`` if the attribute is a column, ``False`` otherwise.
    """
    return isinstance(getattr(model, attr).property, ColumnProperty)


def get_column_type(model, attr):
    """Get the type of a column.

    :param model: The model that contains the column.
    :param attr: Name of the column.
    :return: The type of the column or ``None`` if the attribute is not a normal column.
    """
    if is_column(model, attr):
        return getattr(model, attr).property.columns[0].type

    return None


def is_relationship(model, attr):
    """Check if a models attribute is a relationship.

    :param model: The model that contains the column.
    :param attr: Name of the attribute.
    :return: ``True`` if the attribute is a relationship, ``False`` otherwise.
    """
    return isinstance(getattr(model, attr).property, RelationshipProperty)


def is_many_relationship(model, attr):
    """Check if a models attribute is a many-relationship.

    :param model: The model that contains the column.
    :param attr: Name of the attribute.
    :return: ``True`` if the attribute is a many-relationship, ``False`` otherwise.
    """
    if not is_relationship(model, attr):
        return False

    return getattr(model, attr).property.uselist
