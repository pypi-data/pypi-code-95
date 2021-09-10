"""Contains the DB wrapper class."""
from contextlib import asynccontextmanager
from time import time
from typing import (Any, AsyncIterator, Awaitable, Iterable, List, Optional,
                    cast)

from asyncpg import Connection, connect

import apgw.builder as builder
from apgw.constraint import Assignments, Constraints
from apgw.types import (ConnectionArgs, InsertAssignments, LimitOffset, Params,
                        Record, Records, RecordsAndCount)


class DBBase:
    """A simple wrapper around asyncpg to alleviate some boilerplate."""

    def __init__(self) -> None:
        """Initializes the DB instance. """
        self._conn: Optional[Connection] = None
        self._is_in_transaction: bool = False

    @property
    def is_open(self) -> bool:
        """Returns True if the instance is connected."""
        return bool(self._conn)

    @property
    def is_in_transaction(self) -> bool:
        """Returns True if the connection is in a transaction."""
        return self._is_in_transaction

    @property
    def conn(self) -> Connection:
        if self._conn is None:
            raise Exception("Connection is not open")
        return self._conn

    @property
    def should_auto_open(self) -> bool:
        """Returns True if the connection can and should be opened automatically."""
        return not self.is_open

    def log(
        self,
        sql: str,
        params: Optional[Params],
        duration: float,
        error: Optional[Exception],
    ) -> None:
        """Hook for logging out sql, params, along with duration and error information.
        Override to do something with this information.
        """

    async def auto_open(self) -> bool:
        """Opens the database if it should auto open."""
        if self.should_auto_open:
            await self.open()
            return True
        return False

    async def get_connection_args(self) -> ConnectionArgs:
        raise NotImplementedError()

    async def connect(self, connection_args: ConnectionArgs) -> "Connection":
        """Override this method to customize how the connection is open. For instance you could
        use a connection pool's acquire method.
        """
        return await connect(**connection_args)

    async def disconnect(self, connection: Connection):
        """Override this method to customize how the connection is closed. For instance you could
        use a connection pool's release method.
        """
        await connection.close()

    async def open(self) -> "DBBase":
        """Opens the connection."""
        if not self._conn:
            conn_args = await self.get_connection_args()
            self._conn = await self.connect(conn_args)
        return self

    async def close(self) -> "DBBase":
        """Closes the connection."""
        if self._conn:
            await self.disconnect(self._conn)
            self._conn = None
        return self

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator["DBBase"]:
        """Run a command in a database transaction."""
        if self._is_in_transaction:
            yield self
        else:
            await self.auto_open()
            async with self.conn.transaction():
                self._is_in_transaction = True
                try:
                    yield self
                finally:
                    self._is_in_transaction = False

    async def __aenter__(self) -> "DBBase":
        """Asynchronous context manager entry point."""
        await self.open()
        return self

    async def __aexit__(self, exc_type: type, exc: Exception, trace) -> None:
        """Asynchronous context manager exit point."""
        await self.close()

    async def execute(self, sql: Optional[str], params: Optional[Params] = None):
        """This method passes through to self.conn.execute.

        :param sql: the parameterized sql to execute
        :param params: a list of params
        """
        if not sql:
            raise Exception("No SQL provided")

        await self.auto_open()
        start = time()
        error: Optional[Exception] = None

        try:
            if params:
                await self.conn.execute(sql, *params)
            else:
                await self.conn.execute(sql)
        except Exception as ex:
            error = ex
            raise
        finally:
            self.log(sql, params, time() - start, error)

    async def executemany(
        self, sql: Optional[str], params: Optional[List[Iterable[Any]]] = None
    ):
        """This method passes through to self.conn.execute.

        :param sql: the parameterized sql to execute
        :param params: a list of params
        """
        if not sql:
            raise Exception("No SQL provided")

        await self.auto_open()
        start = time()
        error: Optional[Exception] = None

        try:
            if params:
                await self.conn.executemany(sql, params)
            else:
                await self.conn.executemany(sql)
        except Exception as ex:
            error = ex
            raise
        finally:
            self.log(sql, params, time() - start, error)

    async def fetch(
        self, sql: Optional[str], params: Optional[Params] = None
    ) -> Records:
        """This method passes through to self.conn.fetch.

        :param sql: the parameterized sql to execute
        :param params: a list of params
        """
        if not sql:
            raise Exception("No SQL provided")

        await self.auto_open()
        start = time()
        error: Optional[Exception] = None

        try:
            if params:
                return await self.conn.fetch(sql, *params)

            return await self.conn.fetch(sql)
        except Exception as ex:
            error = ex
            raise
        finally:
            self.log(sql, params, time() - start, error)

    async def fetchrow(
        self, sql: Optional[str], params: Optional[Params] = None
    ) -> Optional[Record]:
        """This method passes through to self.conn.fetchrow.

        :param sql: the parameterized sql to execute
        :param params: a list of params
        """
        if not sql:
            raise Exception("No SQL provided")

        await self.auto_open()
        start = time()
        error: Optional[Exception] = None

        try:
            if params:
                return await self.conn.fetchrow(sql, *params)

            return await self.conn.fetchrow(sql)
        except Exception as ex:
            error = ex
            raise
        finally:
            self.log(sql, params, time() - start, error)

    async def select(
        self,
        table_name: str,
        constraints: Optional[Constraints] = None,
        *,
        columns: str = "*",
        group_by: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[LimitOffset] = None,
    ) -> Records:
        """Selects records from the database.

        :param table_name: the name of the table to select from
        :param constraints: the constraints for the select filter
        :param columns: the columns to select
        :param order_by: how to order the results
        :param limit: the limit and offset of the results
        """
        (sql, params) = builder.select_sql(
            table_name,
            constraints,
            columns=columns,
            group_by=group_by,
            order_by=order_by,
            limit=limit,
        )

        return await self.fetch(sql, params)

    async def select_and_count(
        self,
        table_name: str,
        constraints: Optional[Constraints] = None,
        *,
        columns: str = "*",
        group_by: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[LimitOffset] = None,
    ) -> RecordsAndCount:
        """Counts records that match a constraint and then returns a limited set of them

        :param table_name: the name of the table to select from
        :param constraints: the constraints for the select filter
        :param columns: the columns to select
        :param order_by: how to order the results
        :param limit: the limit and offset of the results
        """
        count_record = cast(
            Record,
            await self.select_one(
                table_name,
                constraints,
                columns="count(*) as c",
                group_by=group_by,
                order_by=None,
            ),
        )
        records = await self.select(
            table_name,
            constraints,
            columns=columns,
            group_by=group_by,
            order_by=order_by,
            limit=limit,
        )
        return (records, cast(int, count_record["c"]))

    async def select_one(
        self,
        table_name: str,
        constraints: Optional[Constraints] = None,
        *,
        columns: str = "*",
        group_by: Optional[str] = None,
        order_by: Optional[str] = None,
    ) -> Optional[Record]:
        """Selects a single record from the database.

        :param table_name: the name of the table to select from
        :param constraints: the constraints for the select filter
        :param columns: the columns to select
        :param order_by: how to order the results
        """
        (sql, params) = builder.select_sql(
            table_name,
            constraints,
            columns=columns,
            group_by=group_by,
            order_by=order_by,
            limit=(1, None),
        )

        return await self.fetchrow(sql, params)

    async def exists(
        self, table_name: str, constraints: Optional[Constraints] = None
    ) -> bool:
        """Returns True if the record exists, False otherwise.

        :param table_name: the name of the table to select from
        :param constraits: the filtering constraints
        """
        (sql, params) = builder.select_sql(table_name, constraints)

        return await self.fetchrow(sql, params) is not None

    async def insert(
        self,
        table_name: str,
        assignments: InsertAssignments,
        *,
        returning: Optional[str] = None,
    ) -> Record:
        """Inserts a record into the database.

        :param table_name: the name of the table to insert on
        :param assignments: the insert assignments
        :param returning: a returning column list
        """
        (sql, params) = builder.insert_sql(table_name, assignments, returning=returning)

        output = await self.fetchrow(sql, params)
        return cast(Record, output)

    async def insert_many(
        self,
        table_name: str,
        assignments_list: List[InsertAssignments],
        *,
        returning: Optional[str] = None,
    ) -> Records:
        """Inserts many records into the database.

        :param table_name: the name of hte table to insert on
        :param assignments: the list of insert assignments
        :param returning: a returning column list
        """
        (sql, params) = builder.insert_many_sql(
            table_name, assignments_list, returning=returning
        )

        output = await self.executemany(sql, params)
        return cast(Records, output)

    async def create(
        self, table_name: str, assignments: InsertAssignments, *, returning: str = "*"
    ) -> Record:
        """A wrapper around #insert with a default value on returning of '*'

        :param table_name: the name of the table to insert on
        :param assignments: the insert assignments
        :param returning: a returning column list
        """
        if returning is None:
            raise Exception("Must specify returning")

        return await self.insert(table_name, assignments, returning=returning)

    async def update(
        self,
        table_name: str,
        assignments: Assignments,
        constraints: Optional[Constraints] = None,
        *,
        timestamp_col: Optional[str] = "updated_at",
        returning: Optional[str] = None,
    ) -> Records:
        """Updates records in the database.

        :param table_name: the name of the table to update
        :param assignments: the updates to make
        :param constraints: the filter for the updates
        :param timestamp_col: the 'updated_at' column, if any
        :param returning: the list of colums to return from the update statement
        """
        (sql, params) = builder.update_sql(
            table_name,
            assignments,
            constraints,
            timestamp_col=timestamp_col,
            returning=returning,
        )

        return await self.fetch(sql, params)

    async def delete(
        self,
        table_name: str,
        constraints: Optional[Constraints] = None,
        *,
        returning: Optional[str] = None,
    ) -> Records:
        """Deletes records from the database.

        :param table_name: the name of the table to delete from
        :param constraints: the delete constraints
        :param returning: a returning column list
        """
        (sql, params) = builder.delete_sql(table_name, constraints, returning=returning)

        return await self.fetch(sql, params)


class DB(DBBase):
    """A DBBase implementation that has static connection args."""

    def __init__(self, conn_args: ConnectionArgs, *, auto_open: bool = False) -> None:
        """Initializes the DB instance.

        :param conn_args: the connection arguments
        :param auto_open: if the connection should automatically open
        """
        super().__init__()
        self._conn_args = conn_args
        self._auto_open = auto_open

    @property
    def should_auto_open(self) -> bool:
        return self._auto_open and not self.is_open

    async def get_connection_args(self) -> ConnectionArgs:
        return self._conn_args

    def log(
        self, sql: str, params: Optional[Params], duration: float, error: bool
    ) -> None:
        pass
