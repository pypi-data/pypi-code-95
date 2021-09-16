# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for Presto in PyOkera
#
# pylint: disable=broad-except
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-locals
# pylint: disable=bad-continuation
# pylint: disable=broad-except

import unittest
import os
import pytest

import urllib3
import prestodb

from okera._thrift_api import TRecordServiceException
from okera.tests import pycerebro_test_common as common

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DB = 'test_views_db'
VIEW = 'testview'

DEFAULT_PRESTO_PORT = int(os.environ['ODAS_TEST_PORT_PRESTO_COORD_HTTPS'])
BAD_PRESTO_PORT = 1234

def create_view(conn, db, name, cols, external, skip_analysis, stmt):
    view_stmt = ''
    if external:
        view_stmt = 'CREATE EXTERNAL VIEW %s.%s ' % (db, name)
    else:
        view_stmt = 'CREATE VIEW %s.%s ' % (db, name)

    if cols:
        view_stmt += '('
        view_stmt += ', '.join(['%s %s' % (c[0], c[1]) for c in cols])
        view_stmt += ') '

    if skip_analysis:
        view_stmt += 'SKIP_ANALYSIS '

    view_stmt += 'AS %s' % stmt

    conn.execute_ddl(view_stmt)

def create_view_with_data(conn, db, name, cols, stmt):
    view_stmt = 'CREATE EXTERNAL VIEW %s.%s ' % (db, name)

    if cols:
        view_stmt += '('
        view_stmt += ', '.join(['%s %s' % (c[0], c[1]) for c in cols])
        view_stmt += ') '

    view_stmt += 'SKIP_ANALYSIS '

    view_stmt += 'USING VIEW DATA AS "%s"' % stmt

    conn.execute_ddl(view_stmt)

def cleanup(conn, db):
    conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % db)
    conn.execute_ddl('CREATE DATABASE %s' % db)

@pytest.mark.filterwarnings('ignore::urllib3.exceptions.InsecureRequestWarning')
@pytest.mark.filterwarnings('ignore:numpy.dtype size changed')
class ViewsTest(unittest.TestCase):
    def test_create_with_skip_no_external(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            cleanup(conn, DB)
            with pytest.raises(TRecordServiceException):
                create_view(
                    conn, DB, VIEW,
                    [('x', 'INT'), ('a', 'INT')],
                    external=False, skip_analysis=True,
                    stmt='select * from okera_sample.whoami')

    def test_create_with_skip_no_columns(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            cleanup(conn, DB)
            with pytest.raises(TRecordServiceException):
                create_view(
                    conn, DB, VIEW,
                    [],
                    external=True, skip_analysis=True,
                    stmt='select * from okera_sample.whoami')

    def test_create_with_skip_no_types(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            cleanup(conn, DB)
            with pytest.raises(TRecordServiceException):
                create_view(
                    conn, DB, VIEW,
                    [('x', ''), ('a', '')],
                    external=True, skip_analysis=True,
                    stmt='select * from okera_sample.whoami')

    def test_create_with_skip_table_no_exist(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            cleanup(conn, DB)
            create_view(
                conn, DB, VIEW,
                [('c1', 'int'), ('c2', 'int')],
                external=True, skip_analysis=True,
                stmt='select * from doesnot.exist')
            with pytest.raises(prestodb.exceptions.PrestoQueryError):
                conn.scan_as_json(
                    'select * from %s.%s' % (DB, VIEW), dialect='presto')

    def test_create_with_skip_stale(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            cleanup(conn, DB)
            create_view(
                conn, DB, VIEW,
                [('record', 'string'), ('c2', 'int')],
                external=True, skip_analysis=True,
                stmt='select record, 1 from okera_sample.sample')
            with pytest.raises(prestodb.exceptions.PrestoQueryError):
                conn.scan_as_json(
                    'select * from %s.%s' % (DB, VIEW), dialect='presto')

    def test_create_with_skip_working(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            cleanup(conn, DB)
            create_view(
                conn, DB, VIEW,
                [('record', 'string'), ('c2', 'int')],
                external=True, skip_analysis=True,
                stmt='select record, 1 as c2 from okera_sample.sample')
            conn.scan_as_json(
                'select * from %s.%s' % (DB, VIEW), dialect='presto')

    def test_create_with_skip_presto_functions(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            cleanup(conn, DB)
            create_view(
                conn, DB, VIEW,
                [('dob_parts', 'array<string>'), ('dob', 'string')],
                external=True, skip_analysis=True,
                stmt='''select
                            split(dob, "-") as dob_parts, dob
                        from okera_sample.users
                        limit 10''')
            rows = conn.scan_as_json(
                'select * from %s.%s' % (DB, VIEW), dialect='presto')
            for row in rows:
                assert row['dob'] == '-'.join(row['dob_parts'])

    def test_create_view_data(self):
        ctx = common.get_test_context()
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            cleanup(conn, DB)
            stmt = 'not a query'
            create_view_with_data(
                conn, DB, VIEW,
                [('dob_parts', 'array<string>'), ('dob', 'string')],
                stmt=stmt)
            views = conn.list_datasets(db=DB, name=VIEW)
            assert len(views) == 1
            assert views[0].view_expanded_text == stmt
