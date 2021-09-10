"""Contains methods for building out SQL."""
from typing import Any, List, Mapping, Optional, Set, Tuple

from apgw.constraint import (Assignments, BinaryConstraint, Constraints,
                             DictConstraint, GroupConstraint, Literal,
                             TextConstraint)
from apgw.types import SQL, InsertAssignments, LimitOffset, Record
from apgw.util import constraint_list_to_sql


def diff(source: Record, updates: Record, keys: Optional[Set[str]] = None) -> Record:
    """This returns the subset of :updates: that is different from :source: based on :keys:.

    :param source: the source item
    :param updates: the updates item
    :param keys: the subset of keys to check. If None, updates.keys() is used
    """
    output = {}

    if keys is None:
        keys = set(updates.keys())

    for key in keys:
        if key not in source:
            raise Exception("Key {} not found in source object".format(key))
        if key not in updates:
            raise Exception("Key {} not found in updates object".format(key))
        if source[key] != updates[key]:
            output[key] = updates[key]

    return output


def build_constraint(data: Mapping[str, Any], cols: List[str]) -> DictConstraint:
    """Builds a DictConstraint from a dict and a list of columns."""
    return DictConstraint(((col, data[col]) for col in cols))


def constraints_to_sql(
    constraints: Optional[Constraints],
    *,
    paren: bool = True,
    joiner: str = " and ",
    offset: int = 0,
    handle_null: bool = True,
) -> SQL:
    """This methods converts a constraints object to SQL and params.

    :param constraints: the constraints to convert
    :param paren: if True, each constraint will be surrounded by parens
    :param joiner: how to join the constraint strings together
    :param offset: the offset to use for the constraint placeholders
    :param handle_null: if True, constraint values of None will be handled specially
    """
    if constraints is None:
        return (None, [])

    if isinstance(constraints, TextConstraint):
        # Replaces all occurrences of '$0' with a numbered placeholder. This makes it so the calling
        # code doesn't have to know the exact numbers
        sql = constraints.sql
        placeholder = 1
        while sql.find("$0") != -1:
            sql = sql.replace("$0", "${}".format(placeholder + offset), 1)
            placeholder += 1

        return (sql, constraints.params or [])

    if isinstance(constraints, DictConstraint):
        constraint_list = [BinaryConstraint(k, v) for k, v in constraints.items()]
    elif isinstance(constraints, list):
        constraint_list = constraints
    elif isinstance(constraints, BinaryConstraint):
        constraint_list = [constraints]
    elif isinstance(constraints, GroupConstraint):
        return group_constraint_to_sql(
            constraints, offset=offset, handle_null=handle_null
        )
    else:
        raise Exception("Invalid constraint type")

    return constraint_list_to_sql(
        constraint_list,
        paren=paren,
        joiner=joiner,
        offset=offset,
        handle_null=handle_null,
    )


def group_constraint_to_sql(group: GroupConstraint, *, offset: int, handle_null) -> SQL:
    """This method converts a GroupConstraint object to SQL and params.

    :param group: the group constraint
    :param offset: the offset for parameter placeholders
    :param handle_null: if True, the constraint values of None will be handled specially
    """
    sql = ""
    params = []
    for constraint in group.constraints:
        (part_sql, part_params) = constraints_to_sql(
            constraint,
            paren=False,
            joiner=group.joiner,
            offset=offset,
            handle_null=handle_null,
        )
        offset += len(part_params)
        params.extend(part_params)
        if part_sql:
            part_sql = "(" + part_sql + ")"
            if not sql:
                sql = part_sql
            else:
                sql = f"{sql} {group.joiner} {part_sql}"
    return (sql, params)


def select_sql(
    table_name: str,
    constraints: Optional[Constraints] = None,
    *,
    columns: str = "*",
    group_by: Optional[str] = None,
    order_by: Optional[str] = None,
    limit: Optional[LimitOffset] = None,
) -> SQL:
    """Generates a select statement.

    :param table_name: the name of the table to select from
    :param constraints: the constraints for the select filter
    :param columns: the columns to select
    :param order_by: how to order the results
    :param limit: the limit and offset of the results
    """
    (constraint_sql, params) = constraints_to_sql(constraints)

    sql = "select {} from {}".format(columns, table_name)

    if constraint_sql:
        sql = "{} where {}".format(sql, constraint_sql)

    if group_by:
        sql = "{} group by {}".format(sql, group_by)

    if order_by:
        sql = "{} order by {}".format(sql, order_by)

    if limit:
        (limit_num, offset_num) = limit
        if limit_num:
            sql = "{} limit {}".format(sql, limit_num)
        if offset_num:
            sql = "{} offset {}".format(sql, offset_num)

    return (sql, params)


def insert_sql(
    table_name: str, assignments: InsertAssignments, *, returning: Optional[str] = None
) -> SQL:
    """Generates an insert statement.

    :param table_name: the name of the table to insert on
    :param assignments: the insert assignments
    :param returning: a returning column list
    """
    assign: List[Tuple[str, Any]]

    if isinstance(assignments, list):
        assign = assignments
    else:
        assign = list(assignments.items())

    columns = ", ".join(c for (c, _) in assign)
    placeholder_list = []
    params = []
    placeholder = 1

    for (_, val) in assign:
        if isinstance(val, Literal):
            placeholder_list.append(val.value)
        else:
            placeholder_list.append("${}".format(placeholder))
            placeholder += 1
            params.append(val)
    placeholders = ", ".join(placeholder_list)

    sql = "insert into {table_name} ({columns}) values ({placeholders})".format(
        table_name=table_name, columns=columns, placeholders=placeholders
    )

    if returning:
        sql = "{} returning {}".format(sql, returning)

    return (sql, params)


def insert_many_sql(
    table_name: str,
    assignments_list: List[InsertAssignments],
    *,
    returning: Optional[str] = None,
) -> SQL:
    """Builds out SQL and params for insert many."""
    one_sql: Optional[str] = None
    params_list = []

    for assignments in assignments_list:
        (sql, params) = insert_sql(table_name, assignments, returning=returning)
        if not one_sql:
            one_sql = sql
        params_list.append(params)

    return (one_sql, params_list)


def update_sql(
    table_name: str,
    assignments: Assignments,
    constraints: Optional[Constraints] = None,
    *,
    timestamp_col: Optional[str] = "updated_at",
    returning: Optional[str] = None,
) -> SQL:
    """Generates an update statement.

    :param table_name: the name of the table to update
    :param assignments: the updates to make
    :param constraints: the filter for the updates
    :param timestamp_col: the 'updated_at' column, if any
    :param returning: the list of colums to return from the update statement
    """
    if timestamp_col:
        if assignments:
            if isinstance(assignments, TextConstraint):
                raise Exception(
                    "Cannot combine timestamp_col and TextConstraint for update"
                )

            if isinstance(assignments, DictConstraint):
                assignments[timestamp_col] = Literal("now()")
            elif isinstance(assignments, BinaryConstraint):
                assignments = [
                    assignments,
                    BinaryConstraint(timestamp_col, Literal("now()")),
                ]
            else:
                assignments.append(BinaryConstraint(timestamp_col, Literal("now()")))
        else:
            assignments = [BinaryConstraint(timestamp_col, Literal("now()"))]

    (assign_sql, assign_params) = constraints_to_sql(
        assignments, paren=False, joiner=", ", handle_null=False
    )
    (constraint_sql, constraint_params) = constraints_to_sql(
        constraints, paren=True, offset=len(assign_params)
    )

    if not assign_sql:
        raise Exception("No assigments given for update")

    sql = "update {} set {}".format(table_name, assign_sql)

    if constraint_sql:
        sql = "{} where {}".format(sql, constraint_sql)

    if returning:
        sql = "{} returning {}".format(sql, returning)

    return (sql, assign_params + constraint_params)


def delete_sql(
    table_name: str,
    constraints: Optional[Constraints] = None,
    *,
    returning: Optional[str] = None,
) -> SQL:
    """Generates a delete statement.

    :param table_name: the name of the table to delete from
    :param constraints: the delete constraints
    :param returning: a returning column list
    """
    (constraint_sql, params) = constraints_to_sql(constraints)

    sql = "delete from {}".format(table_name)

    if constraint_sql:
        sql = "{} where {}".format(sql, constraint_sql)

    if returning:
        sql = "{} returning {}".format(sql, returning)

    return (sql, params)
