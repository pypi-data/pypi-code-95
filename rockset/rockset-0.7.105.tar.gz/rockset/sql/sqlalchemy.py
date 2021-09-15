"""Integration between SQLAlchemy and Rockset.

Some code based on:
https://github.com/zzzeek/sqlalchemy/blob/rel_0_5/lib/sqlalchemy/databases/sqlite.py
which is released under the MIT license.

https://github.com/dropbox/PyHive
released under Apache License, Version 2.0
"""

from __future__ import absolute_import
from __future__ import unicode_literals

from sqlalchemy import exc
from sqlalchemy import types
from sqlalchemy import util
from sqlalchemy.engine import default, reflection
from sqlalchemy.sql import compiler
from rockset import Client
from rockset.sql import dbapi

import rockset


class BaseType():
    __visit_name__ = None

    def __str__(self):
        return self.__visit_name__


class NullType(BaseType, types.NullType):
    __visit_name__ = rockset.document.DATATYPE_NULL
    hashable = True


class Int(BaseType, types.BigInteger):
    __visit_name__ = rockset.document.DATATYPE_INT


class Float(BaseType, types.Float):
    __visit_name__ = rockset.document.DATATYPE_FLOAT


class Bool(BaseType, types.Boolean):
    __visit_name__ = rockset.document.DATATYPE_BOOL


class String(BaseType, types.String):
    __visit_name__ = rockset.document.DATATYPE_STRING


class Bytes(BaseType, types.LargeBinary):
    __visit_name__ = rockset.document.DATATYPE_BYTES


class Array(NullType):
    __visit_name__ = rockset.document.DATATYPE_ARRAY


class Object(NullType):
    __visit_name__ = rockset.document.DATATYPE_OBJECT


class Date(BaseType, types.DATE):
    __visit_name__ = rockset.document.DATATYPE_DATE


class DateTime(BaseType, types.DATETIME):
    __visit_name__ = rockset.document.DATATYPE_DATETIME


class Time(BaseType, types.TIME):
    __visit_name__ = rockset.document.DATATYPE_TIME


class Time(BaseType, types.String):
    __visit_name__ = rockset.document.DATATYPE_TIMESTAMP


class MicrosecondInterval(BaseType, types.Interval):
    __visit_name__ = rockset.document.DATATYPE_MICROSECOND_INTERVAL

    def bind_processor(self, dialect):
        def process(value):
            return value

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value

        return process


class MonthInterval(Object):
    __visit_name__ = rockset.document.DATATYPE_MONTH_INTERVAL


class Geography(Object):
    __visit_name__ = rockset.document.DATATYPE_GEOGRAPHY


_type_map = {
    rockset.document.DATATYPE_NULL: NullType,
    rockset.document.DATATYPE_INT: Int,
    rockset.document.DATATYPE_FLOAT: Float,
    rockset.document.DATATYPE_BOOL: Bool,
    rockset.document.DATATYPE_STRING: String,
    rockset.document.DATATYPE_BYTES: Bytes,
    rockset.document.DATATYPE_OBJECT: Object,
    rockset.document.DATATYPE_ARRAY: Array,
    rockset.document.DATATYPE_DATE: Date,
    rockset.document.DATATYPE_DATETIME: DateTime,
    rockset.document.DATATYPE_TIME: Time,
    rockset.document.DATATYPE_MICROSECOND_INTERVAL: MicrosecondInterval,
    rockset.document.DATATYPE_MONTH_INTERVAL: MonthInterval,
    rockset.document.DATATYPE_GEOGRAPHY: Geography,
}


class _EverythingSet(object):
    """set contains *everything*"""
    def __contains__(self, _):
        return True


class RocksetIdentifierPreparer(compiler.IdentifierPreparer):
    # Just quote everything to make things simpler / easier to upgrade
    reserved_words = _EverythingSet()


class RocksetDialect(default.DefaultDialect):
    """Define dialect properties as shown in:
    https://docs.sqlalchemy.org/en/13/core/internals.html#sqlalchemy.engine.interfaces.Dialect
    """
    name = 'rockset'
    driver = 'rockset'

    positional = False
    paramstyle = 'named'

    statement_compiler = compiler.SQLCompiler
    type_compiler = compiler.GenericTypeCompiler
    preparer = RocksetIdentifierPreparer
    default_schema_name = 'commons'

    supports_alter = False
    supports_unicode_statements = True
    supports_unicode_binds = True
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    preexecute_autoincrement_sequences = False

    supports_default_values = False
    supports_sequences = False
    supports_native_enum = False
    supports_native_boolean = True

    @classmethod
    def dbapi(cls):
        return dbapi

    def create_connect_args(self, url):
        kwargs = {
            'api_server': '{}:{}'.format(url.host, url.port or 443),
            'api_key': url.password or url.username,
        }
        return ([], kwargs)

    @reflection.cache
    def get_schema_names(self, connection, **kw):
        rs_client = connection.connect().connection._client()
        return [w['name'] for w in rs_client.Workspace.list()]

    @reflection.cache
    def get_table_names(self, connection, schema=None, **kw):
        rs_client = connection.connect().connection._client()
        schema = schema or RocksetDialect.default_schema_name
        return [c.name for c in rs_client.Collection.list(workspace=schema)]

    @reflection.cache
    def get_view_names(self, connection, schema=None, **kw):
        return []

    def _get_table_columns(self, connection, table_name, schema):
        full_schema = self.identifier_preparer.quote_identifier(schema)
        full_table = self.identifier_preparer.quote_identifier(table_name)
        query = 'SELECT * FROM {0}.{1} LIMIT 1'.format(full_schema, full_table)
        try:
            sa_conn = connection.connect()
            dbapi_conn = sa_conn.connection
            dbapi_cursor = dbapi_conn.cursor()
            dbapi_cursor.execute(query)
            # for collections with 0 fields return a single null fake column
            # sqlalchemy.engine.reflection.reflecttable otherwise thinks that
            # the table does not exist
            fields = dbapi_cursor.description
            if not fields:
                return [('null', 'null')]
            return [(f[0], f[1]) for f in fields]
        except (dbapi.DatabaseError, exc.DatabaseError) as e:
            # Check if table exists
            msg = hasattr(e, 'message') and e.message or None
            code = hasattr(e, 'code') and e.code or 0
            if 'does not exist' in msg or code == 404:
                raise exc.NoSuchTableError(table_name)
            else:
                raise e

    @reflection.cache
    def get_columns(self, connection, table_name, schema=None, **kw):
        schema = schema or RocksetDialect.default_schema_name
        columns = []
        for (field_name, field_type
            ) in self._get_table_columns(connection, table_name, schema):
            if field_type not in _type_map:
                raise exc.SQLAlchemyError(
                    'query returned unsupported '
                    'datatype {} in field {}.{}.{} '.format(
                        field_type, schema, table_name, field_name
                    )
                )
            columns.append(
                {
                    'name': field_name,
                    'type': _type_map.get(field_type, types.String),
                    'nullable': (field_name != '_id'),
                    'default': None
                }
            )
        return columns

    def has_table(self, connection, table_name, schema=None):
        try:
            self._get_table_columns(connection, table_name, schema)
            return True
        except exc.NoSuchTableError:
            return False

    @reflection.cache
    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        # no support for foreign keys.
        return []

    @reflection.cache
    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        # no support for primary keys.
        return {'constrained_columns': ['_id'], 'name': '_id_pk'}

    @reflection.cache
    def get_indexes(self, connection, table_name, schema=None, **kw):
        # no need for primary keys.
        return []

    def do_rollback(self, dbapi_connection):
        # No transactions in Rockset
        pass

    def _check_unicode_returns(self, connection, additional_tests=None):
        # requests gives back Unicode strings
        return True

    def _check_unicode_description(self, connection):
        # requests gives back Unicode strings
        return True
