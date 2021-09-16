# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for managing attributes
#
# pylint: disable=bad-continuation
# pylint: disable=line-too-long
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines

import unittest

from okera.tests import pycerebro_test_common as common

class AttributesTest(unittest.TestCase):

    # skip_cascade is a flag to skip tests for known bugs, remove when fixed
    def _validate(self, conn, db, attr, tags, sql, expected, skip_cascade=False):
        # Create the view and then assign the tag, validate tag INHERITANCE
        conn.execute_ddl("DROP VIEW IF EXISTS %s.v" % db)
        conn.execute_ddl("CREATE VIEW %s.v AS %s" % (db, sql))

        conn.execute_ddl("drop attribute if exists %s.a1" % db)
        conn.execute_ddl("create attribute %s.a1" % db)
        for tag in tags:
            conn.assign_attribute(db, attr, tag[0], tag[1], tag[2], cascade=True)

        print(conn.execute_ddl_table_output('DESCRIBE %s.v' % db))
        self.assertEqual(
            expected,
            str(conn.execute_ddl_table_output('DESCRIBE %s.v' % db)))

        # Recreate the view (tagged already assigned), validate tag CASCADE
        if not skip_cascade:
            conn.execute_ddl("DROP VIEW IF EXISTS %s.v" % db)
            conn.execute_ddl("CREATE VIEW %s.v AS %s" % (db, sql))
            print(conn.execute_ddl_table_output('DESCRIBE %s.v' % db))
            self.assertEqual(
                expected,
                str(conn.execute_ddl_table_output('DESCRIBE %s.v' % db)))

    def test_specific(self):
        # Not a test, just skeleton to test a specific scenario
        db = 'attr_test_db'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("drop database if exists %s cascade" % db)
            conn.execute_ddl("create database if not exists %s" % db)

            self._validate(conn, db, 'a1',
                [['chase', 'subscription_currency', 'currency.country']],
                'select ** from chase.subscription_currency',
                """
+------------------------+--------+---------+-----------------+
|          name          |  type  | comment |    attributes   |
+------------------------+--------+---------+-----------------+
|   currency__country    | string |         | attr_test_db.a1 |
| currency__currencycode | string |         |                 |
+------------------------+--------+---------+-----------------+""".strip(), skip_cascade=True)

    def test_unnest_attributes(self):
        db = 'attr_test_db'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("drop database if exists %s cascade" % db)
            conn.execute_ddl("create database if not exists %s" % db)

            # No tags
            self._validate(conn, db, 'a1', [],
                """select productkey, partyroles.item.partykey as partykey
                   from chase.zd1238_4, chase.zd1238_4.partyroles""",
                """
+------------+--------+---------+------------+
|    name    |  type  | comment | attributes |
+------------+--------+---------+------------+
| productkey | string |         |            |
|  partykey  | string |         |            |
+------------+--------+---------+------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'zd1238_4', 'productkey'],
                 ['chase', 'zd1238_4', 'partyroles.partykey']],
                """select productkey, partyroles.item.partykey as partykey
                   from chase.zd1238_4, chase.zd1238_4.partyroles""",
                """
+------------+--------+---------+-----------------+
|    name    |  type  | comment |    attributes   |
+------------+--------+---------+-----------------+
| productkey | string |         | attr_test_db.a1 |
|  partykey  | string |         | attr_test_db.a1 |
+------------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'zd1238_4', 'productkey']],
                """select productkey, partyroles.item.partykey as partykey
                   from chase.zd1238_4, chase.zd1238_4.partyroles""",
                """
+------------+--------+---------+-----------------+
|    name    |  type  | comment |    attributes   |
+------------+--------+---------+-----------------+
| productkey | string |         | attr_test_db.a1 |
|  partykey  | string |         |                 |
+------------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'zd1238_4', 'partyroles.partykey']],
                """select productkey, partyroles.item.partykey as partykey
                   from chase.zd1238_4, chase.zd1238_4.partyroles""",
                """
+------------+--------+---------+-----------------+
|    name    |  type  | comment |    attributes   |
+------------+--------+---------+-----------------+
| productkey | string |         |                 |
|  partykey  | string |         | attr_test_db.a1 |
+------------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex', 'strarray_t', 'str_arr']],
                """select id, str_arr.item
                   from rs_complex.strarray_t, rs_complex.strarray_t.str_arr""",
                """
+------+--------+---------+-----------------+
| name |  type  | comment |    attributes   |
+------+--------+---------+-----------------+
|  id  | bigint |         |                 |
| item | string |         | attr_test_db.a1 |
+------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_t', 'a1']],
                """select unnest_alias.item, unnest_alias.item.f1 as f1
                   from rs_complex.array_struct_t,
                   rs_complex.array_struct_t.a1 unnest_alias""",
                """
+------+--------------+---------+-----------------+
| name |     type     | comment |    attributes   |
+------+--------------+---------+-----------------+
| item |   struct<    |         | attr_test_db.a1 |
|      |   f1:string, |         |                 |
|      |   f2:string  |         |                 |
|      |      >       |         |                 |
|  f1  |    string    |         |                 |
+------+--------------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'subscription_currency', 'currency.country']],
                'select ** from chase.subscription_currency',
                """
+------------------------+--------+---------+-----------------+
|          name          |  type  | comment |    attributes   |
+------------------------+--------+---------+-----------------+
|   currency__country    | string |         | attr_test_db.a1 |
| currency__currencycode | string |         |                 |
+------------------------+--------+---------+-----------------+""".strip())

            # FIXME: this is not cascading correctly
            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_t', 'a1.f1']],
                """select unnest_alias.item, unnest_alias.item.f1 as f1
                   from rs_complex.array_struct_t,
                   rs_complex.array_struct_t.a1 unnest_alias""",
                """
+------+--------------+---------+-----------------+
| name |     type     | comment |    attributes   |
+------+--------------+---------+-----------------+
| item |   struct<    |         |                 |
|      |   f1:string, |         | attr_test_db.a1 |
|      |   f2:string  |         |                 |
|      |      >       |         |                 |
|  f1  |    string    |         | attr_test_db.a1 |
+------+--------------+---------+-----------------+""".strip(), skip_cascade=True)

            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_t', 'a1.f2']],
                """select a1.item.f2 as f2, a1.item.f1 as f1
                   from rs_complex.array_struct_t, rs_complex.array_struct_t.a1""",
                """
+------+--------+---------+-----------------+
| name |  type  | comment |    attributes   |
+------+--------+---------+-----------------+
|  f2  | string |         | attr_test_db.a1 |
|  f1  | string |         |                 |
+------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_t', 'a1.f2'],
                 ['rs_complex', 'array_struct_t', 'a1.f1']],
                """select a1.item.f2 as f2, a1.item.f1 as f1
                   from rs_complex.array_struct_t, rs_complex.array_struct_t.a1""",
                """
+------+--------+---------+-----------------+
| name |  type  | comment |    attributes   |
+------+--------+---------+-----------------+
|  f2  | string |         | attr_test_db.a1 |
|  f1  | string |         | attr_test_db.a1 |
+------+--------+---------+-----------------+""".strip())

            # FIXME: this is not cascading correctly
            self._validate(conn, db, 'a1',
               [['rs_complex', 'array_struct_t', 'a1.f1'],
                 ['rs_complex', 'array_struct_t', 'a1.f2']],
                """select a1.item as item, a1.item.f1 as f1
                   from rs_complex.array_struct_t, rs_complex.array_struct_t.a1""",
                """
+------+--------------+---------+-----------------+
| name |     type     | comment |    attributes   |
+------+--------------+---------+-----------------+
| item |   struct<    |         |                 |
|      |   f1:string, |         | attr_test_db.a1 |
|      |   f2:string  |         | attr_test_db.a1 |
|      |      >       |         |                 |
|  f1  |    string    |         | attr_test_db.a1 |
+------+--------------+---------+-----------------+""".strip(), skip_cascade=True)

            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_array', 'a1.a2'],
                 ['rs_complex', 'array_struct_array', 'a1.f1']],
                """select a1.item.a2 as a2, a1.item.f1 as f1
                   from rs_complex.array_struct_array,
                   rs_complex.array_struct_array.a1""",
                """
+------+---------------+---------+-----------------+
| name |      type     | comment |    attributes   |
+------+---------------+---------+-----------------+
|  a2  | array<string> |         | attr_test_db.a1 |
|  f1  |     string    |         | attr_test_db.a1 |
+------+---------------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'zd1238_4', 'partyroles.partykey']],
                """select partyroles.item.partykey as partykey,
                          tokenize(partyroles.item.partykey) as tokenized_key
                   from chase.zd1238_4 c, c.partyroles
                   where partyroles.item.partykey =
                      '1a43fd68-31d0-46a4-b3f0-bc42730ed5f7'""",
                """
+---------------+--------+---------+-----------------+
|      name     |  type  | comment |    attributes   |
+---------------+--------+---------+-----------------+
|    partykey   | string |         | attr_test_db.a1 |
| tokenized_key | string |         |                 |
+---------------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex_parquet', 'spark_gzip', 'int32'],
                 ['rs_complex_parquet', 'spark_gzip', 'str_arr'],
                 ['rs_complex_parquet', 'spark_gzip', 'int_arr']],
                """select int32, str_arr.item as str_arr, int_arr.item as int_arr
                   from rs_complex_parquet.spark_gzip,
                        rs_complex_parquet.spark_gzip.str_arr,
                        rs_complex_parquet.spark_gzip.int_arr""",
                """
+---------+--------+---------+-----------------+
|   name  |  type  | comment |    attributes   |
+---------+--------+---------+-----------------+
|  int32  |  int   |         | attr_test_db.a1 |
| str_arr | string |         | attr_test_db.a1 |
| int_arr |  int   |         | attr_test_db.a1 |
+---------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'zd1211', 'accountnumber'],
                 ['chase', 'zd1211', 'productdetails.subproducts']],
                """select accountnumber, subproducts.item
                   from chase.zd1211, chase.zd1211.productdetails.subproducts
                   where accountnumber in ('65360119', '26509759')""",
"""
+---------------+--------+---------+-----------------+
|      name     |  type  | comment |    attributes   |
+---------------+--------+---------+-----------------+
| accountnumber | string |         | attr_test_db.a1 |
|      item     | string |         | attr_test_db.a1 |
+---------------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_array', 'a1.f1']],
                """select b.* from rs_complex.array_struct_array a, a.a1 b
                   where b.item.f1 = 'ab'""",
"""
+------+---------------+---------+-----------------+
| name |      type     | comment |    attributes   |
+------+---------------+---------+-----------------+
|  f1  |     string    |         | attr_test_db.a1 |
|  f2  |     string    |         |                 |
|  a2  | array<string> |         |                 |
+------+---------------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'product', 'productkey'],
                 ['chase', 'product', 'feescharges.feeamount'],
                 ['chase', 'product', 'feescharges.feename']],
                """select p.productkey, fc.item.feename as feename,
                   fc.item.feeamount as feeamount from chase.product p, p.feescharges fc
                   where fc.item.feeamount = '10.1' and fc.item.feename = 'STOPCHEQUE'""",
"""
+------------+--------+---------+-----------------+
|    name    |  type  | comment |    attributes   |
+------------+--------+---------+-----------------+
| productkey | string |         | attr_test_db.a1 |
|  feename   | string |         | attr_test_db.a1 |
| feeamount  | string |         | attr_test_db.a1 |
+------------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'zd1211', 'accountnumber'],
                ['chase', 'zd1211', 'productdetails.subproducts']],
                """select accountnumber, subproducts.item from chase.zd1211,
                   chase.zd1211.productdetails.subproducts
                   where accountnumber in ('65360119', '26509759')""",
"""
+---------------+--------+---------+-----------------+
|      name     |  type  | comment |    attributes   |
+---------------+--------+---------+-----------------+
| accountnumber | string |         | attr_test_db.a1 |
|      item     | string |         | attr_test_db.a1 |
+---------------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex_parquet', 'array_struct_t', 'a1'],
                 ['rs_complex_parquet', 'array_struct_t', 'a1.f1']],
                """select t1.item, t1.item.f1 as f1
                   from rs_complex_parquet.array_struct_t, rs_complex.array_struct_t,
                        rs_complex_parquet.array_struct_t.a1 t1
                   join rs_complex.array_struct_t.a1 t2 ON (t1.item.f1 = t2.item.f1)""",
"""
+------+--------------+---------+-----------------+
| name |     type     | comment |    attributes   |
+------+--------------+---------+-----------------+
| item |   struct<    |         | attr_test_db.a1 |
|      |   f1:string, |         | attr_test_db.a1 |
|      |   f2:string  |         |                 |
|      |      >       |         |                 |
|  f1  |    string    |         | attr_test_db.a1 |
+------+--------------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex_parquet', 'array_struct_t', 'a1.f1']],
                """select a1.* from rs_complex_parquet.array_struct_t,
                   rs_complex_parquet.array_struct_t.a1""",
"""
+------+--------+---------+-----------------+
| name |  type  | comment |    attributes   |
+------+--------+---------+-----------------+
|  f1  | string |         | attr_test_db.a1 |
|  f2  | string |         |                 |
+------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex_parquet', 'array_struct_t', 'a1.f1'],
                 ['rs_complex_parquet', 'array_struct_t', 'a1.f2']],
                """select a1.* from rs_complex_parquet.array_struct_t,
                   rs_complex_parquet.array_struct_t.a1""",
"""
+------+--------+---------+-----------------+
| name |  type  | comment |    attributes   |
+------+--------+---------+-----------------+
|  f1  | string |         | attr_test_db.a1 |
|  f2  | string |         | attr_test_db.a1 |
+------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'product', 'limits.transactionlimits.description'],
                 ['chase', 'product', 'limits.transactionlimits.transactionname']],
                """select tlimits.* from chase.product p,
                   p.limits.transactionlimits tlimits""",
"""
+-----------------+--------+---------+-----------------+
|       name      |  type  | comment |    attributes   |
+-----------------+--------+---------+-----------------+
| transactionname | string |         | attr_test_db.a1 |
|   description   | string |         | attr_test_db.a1 |
|  minimumamount  | string |         |                 |
|  maximumamount  | string |         |                 |
|   resetperiod   | string |         |                 |
+-----------------+--------+---------+-----------------+""".strip())

            #
            # FIXME: this is not right. Not inheriting inside f1. The cascade value
            # is actually correct.
            #
            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_array', 'a1'],
                 ['rs_complex', 'array_struct_array', 'a1.f1'],
                 ['rs_complex', 'array_struct_array', 'a1.a2']],
                """select a.*, b.* from rs_complex.array_struct_array a, a.a1 b""",
"""
+------+--------------------+---------+-----------------+
| name |        type        | comment |    attributes   |
+------+--------------------+---------+-----------------+
|  a1  |   array<struct<    |         | attr_test_db.a1 |
|      |      f1:string,    |         |                 |
|      |      f2:string,    |         |                 |
|      |   a2:array<string> |         |                 |
|      |         >>         |         |                 |
|  f1  |       string       |         | attr_test_db.a1 |
|  f2  |       string       |         |                 |
|  a2  |   array<string>    |         | attr_test_db.a1 |
+------+--------------------+---------+-----------------+""".strip(), skip_cascade=True)

            self._validate(conn, db, 'a1',
                [['functional', 'allcomplextypes', 'id'],
                 ['functional', 'allcomplextypes', 'nested_struct_col.f1']],
                """select * from functional.allcomplextypes,
                   functional.allcomplextypes.int_array_col""",
"""
+---------------------------+----------------------------+---------+-----------------+
|            name           |            type            | comment |    attributes   |
+---------------------------+----------------------------+---------+-----------------+
|             id            |            int             |         | attr_test_db.a1 |
|       int_array_col       |         array<int>         |         |                 |
|      array_array_col      |     array<array<int>>      |         |                 |
|       map_array_col       |   array<map<string,int>>   |         |                 |
|      struct_array_col     |       array<struct<        |         |                 |
|                           |          f1:bigint,        |         |                 |
|                           |          f2:string         |         |                 |
|                           |             >>             |         |                 |
|        int_map_col        |      map<string,int>       |         |                 |
|       array_map_col       |   map<string,array<int>>   |         |                 |
|       struct_map_col      |     map<string,struct<     |         |                 |
|                           |          f1:bigint,        |         |                 |
|                           |          f2:string         |         |                 |
|                           |             >>             |         |                 |
|       int_struct_col      |          struct<           |         |                 |
|                           |           f1:int,          |         |                 |
|                           |            f2:int          |         |                 |
|                           |             >              |         |                 |
|     complex_struct_col    |          struct<           |         |                 |
|                           |           f1:int,          |         |                 |
|                           |        f2:array<int>,      |         |                 |
|                           |      f3:map<string,int>    |         |                 |
|                           |             >              |         |                 |
|     nested_struct_col     |          struct<           |         |                 |
|                           |           f1:int,          |         | attr_test_db.a1 |
|                           |          f2:struct<        |         |                 |
|                           |          f11:bigint,       |         |                 |
|                           |          f12:struct<       |         |                 |
|                           |            f21:bigint      |         |                 |
|                           |               >            |         |                 |
|                           |              >             |         |                 |
|                           |             >              |         |                 |
| complex_nested_struct_col |          struct<           |         |                 |
|                           |           f1:int,          |         |                 |
|                           |       f2:array<struct<     |         |                 |
|                           |          f11:bigint,       |         |                 |
|                           |     f12:map<string,struct< |         |                 |
|                           |            f21:bigint      |         |                 |
|                           |               >>           |         |                 |
|                           |              >>            |         |                 |
|                           |             >              |         |                 |
|            item           |            int             |         |                 |
|            year           |            int             |         |                 |
|           month           |            int             |         |                 |
+---------------------------+----------------------------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['functional', 'allcomplextypes', 'array_array_col'],
                 ['functional', 'allcomplextypes', 'nested_struct_col.f2.f12.f21']],
                """select * from functional.allcomplextypes,
                   functional.allcomplextypes.int_map_col""",
"""
+---------------------------+----------------------------+---------+-----------------+
|            name           |            type            | comment |    attributes   |
+---------------------------+----------------------------+---------+-----------------+
|             id            |            int             |         |                 |
|       int_array_col       |         array<int>         |         |                 |
|      array_array_col      |     array<array<int>>      |         | attr_test_db.a1 |
|       map_array_col       |   array<map<string,int>>   |         |                 |
|      struct_array_col     |       array<struct<        |         |                 |
|                           |          f1:bigint,        |         |                 |
|                           |          f2:string         |         |                 |
|                           |             >>             |         |                 |
|        int_map_col        |      map<string,int>       |         |                 |
|       array_map_col       |   map<string,array<int>>   |         |                 |
|       struct_map_col      |     map<string,struct<     |         |                 |
|                           |          f1:bigint,        |         |                 |
|                           |          f2:string         |         |                 |
|                           |             >>             |         |                 |
|       int_struct_col      |          struct<           |         |                 |
|                           |           f1:int,          |         |                 |
|                           |            f2:int          |         |                 |
|                           |             >              |         |                 |
|     complex_struct_col    |          struct<           |         |                 |
|                           |           f1:int,          |         |                 |
|                           |        f2:array<int>,      |         |                 |
|                           |      f3:map<string,int>    |         |                 |
|                           |             >              |         |                 |
|     nested_struct_col     |          struct<           |         |                 |
|                           |           f1:int,          |         |                 |
|                           |          f2:struct<        |         |                 |
|                           |          f11:bigint,       |         |                 |
|                           |          f12:struct<       |         |                 |
|                           |            f21:bigint      |         | attr_test_db.a1 |
|                           |               >            |         |                 |
|                           |              >             |         |                 |
|                           |             >              |         |                 |
| complex_nested_struct_col |          struct<           |         |                 |
|                           |           f1:int,          |         |                 |
|                           |       f2:array<struct<     |         |                 |
|                           |          f11:bigint,       |         |                 |
|                           |     f12:map<string,struct< |         |                 |
|                           |            f21:bigint      |         |                 |
|                           |               >>           |         |                 |
|                           |              >>            |         |                 |
|                           |             >              |         |                 |
|            key            |           string           |         |                 |
|           value           |            int             |         |                 |
|            year           |            int             |         |                 |
|           month           |            int             |         |                 |
+---------------------------+----------------------------+---------+-----------------+""".strip())

            #
            # TODO: maps are not supported
            #
            self._validate(conn, db, 'a1',
                [['functional', 'allcomplextypes', 'complex_nested_struct_col.f2.f12.key']],
                """select f12.key from functional.allcomplextypes,
                   functional.allcomplextypes.complex_nested_struct_col.f2.f12""",
"""
+------+--------+---------+------------+
| name |  type  | comment | attributes |
+------+--------+---------+------------+
| key  | string |         |            |
+------+--------+---------+------------+""".strip())

            self._validate(conn, db, 'a1',
                [['functional', 'allcomplextypes', 'int_array_col']],
                """select a.id, int_array_col.item from
                   functional.allcomplextypes a, a.int_array_col""",
"""
+------+------+---------+-----------------+
| name | type | comment |    attributes   |
+------+------+---------+-----------------+
|  id  | int  |         |                 |
| item | int  |         | attr_test_db.a1 |
+------+------+---------+-----------------+""".strip())

    def test_full_unnest_attributes(self):
        db = 'attr_test_db'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl("drop database if exists %s cascade" % db)
            conn.execute_ddl("create database if not exists %s" % db)

            # No tags
            self._validate(conn, db, 'a1', [],
                'select ** from chase.zd1238_4',
                """
+-----------------------------------------------+---------+---------+------------+
|                      name                     |   type  | comment | attributes |
+-----------------------------------------------+---------+---------+------------+
|                subscriptionkey                |  string |         |            |
|              partyroles__partykey             |  string |         |            |
|             partyroles__tenantkey             |  string |         |            |
|                partyroles__role               |  string |         |            |
|            partyroles__partyrolekey           |  string |         |            |
|            partyroles__createddate            |  string |         |            |
|            partyroles__updateddate            |  string |         |            |
|                   productkey                  |  string |         |            |
|                 productversion                |   int   |         |            |
|                  producttype                  |  string |         |            |
|             parentsubscriptionkey             |  string |         |            |
|              parentaccountnumber              |  string |         |            |
|                 accountnumber                 |  string |         |            |
|                    sortcode                   |  string |         |            |
|                  productname                  |  string |         |            |
|               requiredexternalid              |  string |         |            |
|               currency__country               |  string |         |            |
|             currency__currencycode            |  string |         |            |
|                 periodiccycle                 |  string |         |            |
|               subscriptionstatus              |  string |         |            |
|                  createddate                  |  string |         |            |
|                  updateddate                  |  string |         |            |
|    feeconfigurations__applicationfrequency    |  string |         |            |
|   feeconfigurations__chargeincludedindicator  | boolean |         |            |
|        feeconfigurations__chargingcycle       |  string |         |            |
|     feeconfigurations__decision__tablekey     |  string |         |            |
|       feeconfigurations__decision__input      |  string |         |            |
| feeconfigurations__event__eventidentification |  string |         |            |
|      feeconfigurations__event__eventname      |  string |         |            |
|          feeconfigurations__feeamount         |  string |         |            |
|      feeconfigurations__feecap__capamount     |  string |         |            |
|    feeconfigurations__feecap__capoccurrence   |  string |         |            |
|    feeconfigurations__feecap__cappingperiod   |  string |         |            |
|         feeconfigurations__feecategory        |  string |         |            |
|      feeconfigurations__feeidentification     |  string |         |            |
|           feeconfigurations__feename          |  string |         |            |
|        feeconfigurations__feerate__rate       |  string |         |            |
|   feeconfigurations__feerate__notionalvalue   |  string |         |            |
|           feeconfigurations__feetype          |  string |         |            |
|         feeconfigurations__maximumfee         |  string |         |            |
|         feeconfigurations__minimumfee         |  string |         |            |
|           feeconfigurations__taxrate          |  string |         |            |
|    feeconfigurations__statementdescription    |  string |         |            |
|   feeconfigurations__validityperiod__enddate  |  string |         |            |
|  feeconfigurations__validityperiod__startdate |  string |         |            |
|            kafka_message_timestamp            |  bigint |         |            |
+-----------------------------------------------+---------+---------+------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'zd1238_4', 'productkey'],
                 ['chase', 'zd1238_4', 'partyroles.partykey']],
                'select ** from chase.zd1238_4',
                """
+-----------------------------------------------+---------+---------+-----------------+
|                      name                     |   type  | comment |    attributes   |
+-----------------------------------------------+---------+---------+-----------------+
|                subscriptionkey                |  string |         |                 |
|              partyroles__partykey             |  string |         | attr_test_db.a1 |
|             partyroles__tenantkey             |  string |         |                 |
|                partyroles__role               |  string |         |                 |
|            partyroles__partyrolekey           |  string |         |                 |
|            partyroles__createddate            |  string |         |                 |
|            partyroles__updateddate            |  string |         |                 |
|                   productkey                  |  string |         | attr_test_db.a1 |
|                 productversion                |   int   |         |                 |
|                  producttype                  |  string |         |                 |
|             parentsubscriptionkey             |  string |         |                 |
|              parentaccountnumber              |  string |         |                 |
|                 accountnumber                 |  string |         |                 |
|                    sortcode                   |  string |         |                 |
|                  productname                  |  string |         |                 |
|               requiredexternalid              |  string |         |                 |
|               currency__country               |  string |         |                 |
|             currency__currencycode            |  string |         |                 |
|                 periodiccycle                 |  string |         |                 |
|               subscriptionstatus              |  string |         |                 |
|                  createddate                  |  string |         |                 |
|                  updateddate                  |  string |         |                 |
|    feeconfigurations__applicationfrequency    |  string |         |                 |
|   feeconfigurations__chargeincludedindicator  | boolean |         |                 |
|        feeconfigurations__chargingcycle       |  string |         |                 |
|     feeconfigurations__decision__tablekey     |  string |         |                 |
|       feeconfigurations__decision__input      |  string |         |                 |
| feeconfigurations__event__eventidentification |  string |         |                 |
|      feeconfigurations__event__eventname      |  string |         |                 |
|          feeconfigurations__feeamount         |  string |         |                 |
|      feeconfigurations__feecap__capamount     |  string |         |                 |
|    feeconfigurations__feecap__capoccurrence   |  string |         |                 |
|    feeconfigurations__feecap__cappingperiod   |  string |         |                 |
|         feeconfigurations__feecategory        |  string |         |                 |
|      feeconfigurations__feeidentification     |  string |         |                 |
|           feeconfigurations__feename          |  string |         |                 |
|        feeconfigurations__feerate__rate       |  string |         |                 |
|   feeconfigurations__feerate__notionalvalue   |  string |         |                 |
|           feeconfigurations__feetype          |  string |         |                 |
|         feeconfigurations__maximumfee         |  string |         |                 |
|         feeconfigurations__minimumfee         |  string |         |                 |
|           feeconfigurations__taxrate          |  string |         |                 |
|    feeconfigurations__statementdescription    |  string |         |                 |
|   feeconfigurations__validityperiod__enddate  |  string |         |                 |
|  feeconfigurations__validityperiod__startdate |  string |         |                 |
|            kafka_message_timestamp            |  bigint |         |                 |
+-----------------------------------------------+---------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex', 'strarray_t', 'str_arr']],
                'select ** from rs_complex.strarray_t',
                """
+---------+--------+---------+-----------------+
|   name  |  type  | comment |    attributes   |
+---------+--------+---------+-----------------+
|    id   | bigint |         |                 |
| str_arr | string |         | attr_test_db.a1 |
+---------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_t', 'a1.f1']],
                'select ** from rs_complex.array_struct_t',
                """
+--------+--------+---------+-----------------+
|  name  |  type  | comment |    attributes   |
+--------+--------+---------+-----------------+
| a1__f1 | string |         | attr_test_db.a1 |
| a1__f2 | string |         |                 |
+--------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_t', 'a1.f1'],
                 ['rs_complex', 'array_struct_t', 'a1.f2']],
                'select ** from rs_complex.array_struct_t',
                """
+--------+--------+---------+-----------------+
|  name  |  type  | comment |    attributes   |
+--------+--------+---------+-----------------+
| a1__f1 | string |         | attr_test_db.a1 |
| a1__f2 | string |         | attr_test_db.a1 |
+--------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_array', 'a1.a2'],
                 ['rs_complex', 'array_struct_array', 'a1.f1'],
                 ['rs_complex', 'array_struct_array', 'a1.f2']],
                'select ** from rs_complex.array_struct_array',
                """
+--------+--------+---------+-----------------+
|  name  |  type  | comment |    attributes   |
+--------+--------+---------+-----------------+
| a1__f1 | string |         | attr_test_db.a1 |
| a1__f2 | string |         | attr_test_db.a1 |
| a1__a2 | string |         | attr_test_db.a1 |
+--------+--------+---------+-----------------+""".strip())

# FIXME: map is not supported.
#            self._validate(conn, db, 'a1',
#                [['rs_complex_parquet', 'spark_gzip', 'int32'],
#                 ['rs_complex_parquet', 'spark_gzip', 'str_arr'],
#                 ['rs_complex_parquet', 'spark_gzip', 'int_arr']],
#                'select ** from rs_complex_parquet.spark_gzip',
#                """
#+---------+--------+---------+-----------------+
#|   name  |  type  | comment |    attributes   |
#+---------+--------+---------+-----------------+
#|  int32  |  int   |         | attr_test_db.a1 |
#| str_arr | string |         | attr_test_db.a1 |
#| int_arr |  int   |         | attr_test_db.a1 |
#+---------+--------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'zd1211', 'accountnumber'],
                 ['chase', 'zd1211', 'productdetails.subproducts']],
                'select ** from chase.zd1211',
"""
+---------------------------------------------------------------------------------------------------------+---------+---------+-----------------+
|                                                   name                                                  |   type  | comment |    attributes   |
+---------------------------------------------------------------------------------------------------------+---------+---------+-----------------+
|                                             subscriptionkey                                             |  string |         |                 |
|                                           partyroles__partykey                                          |  string |         |                 |
|                                          partyroles__tenantkey                                          |  string |         |                 |
|                                             partyroles__role                                            |  string |         |                 |
|                                         partyroles__partyrolekey                                        |  string |         |                 |
|                                         partyroles__createddate                                         |  string |         |                 |
|                                         partyroles__updateddate                                         |  string |         |                 |
|                                               productname                                               |  string |         |                 |
|                                              effectivedate                                              |  string |         |                 |
|                                                productkey                                               |  string |         |                 |
|                                              productversion                                             |   int   |         |                 |
|                                          parentsubscriptionkey                                          |  string |         |                 |
|                                           parentaccountnumber                                           |  string |         |                 |
|                                              accountnumber                                              |  string |         | attr_test_db.a1 |
|                                                 sortcode                                                |  string |         |                 |
|                                            subscriptionstatus                                           |  string |         |                 |
|                                               createddate                                               |  string |         |                 |
|                                               updateddate                                               |  string |         |                 |
|                                          linkedsubscriptionkey                                          |  string |         |                 |
|                                      productdetails__effectivedate                                      |  string |         |                 |
|                                        productdetails__productkey                                       |  string |         |                 |
|                                        productdetails__tenantkey                                        |  string |         |                 |
|                                     productdetails__productcategory                                     |  string |         |                 |
|                                       productdetails__productname                                       |  string |         |                 |
|                                       productdetails__producttype                                       |  string |         |                 |
|                                    productdetails__productdescription                                   |  string |         |                 |
|                                      productdetails__productsegment                                     |  string |         |                 |
|                                       productdetails__createddate                                       |  string |         |                 |
|                                        productdetails__createdby                                        |  string |         |                 |
|                                       productdetails__updateddate                                       |  string |         |                 |
|                                        productdetails__updatedby                                        |  string |         |                 |
|                                      productdetails__publisheddate                                      |  string |         |                 |
|                                       productdetails__publishedby                                       |  string |         |                 |
|                                        productdetails__closeddate                                       |  string |         |                 |
|                                         productdetails__closedby                                        |  string |         |                 |
|                                          productdetails__status                                         |  string |         |                 |
|                                       productdetails__majorversion                                      |   int   |         |                 |
|                                           productdetails__tags                                          |  string |         |                 |
|                                    productdetails__linkedproduct__id                                    |  string |         |                 |
|                                       productdetails__subproducts                                       |  string |         | attr_test_db.a1 |
|                                    productdetails__requiredexternalid                                   |  string |         |                 |
|                        productdetails__limits__transactionlimits__transactionname                       |  string |         |                 |
|                          productdetails__limits__transactionlimits__description                         |  string |         |                 |
|                         productdetails__limits__transactionlimits__minimumamount                        |  string |         |                 |
|                         productdetails__limits__transactionlimits__maximumamount                        |  string |         |                 |
|                          productdetails__limits__transactionlimits__resetperiod                         |  string |         |                 |
|                             productdetails__limits__schemelimits__schemename                            |  string |         |                 |
|                            productdetails__limits__schemelimits__description                            |  string |         |                 |
|                           productdetails__limits__schemelimits__minimumamount                           |  string |         |                 |
|                           productdetails__limits__schemelimits__maximumamount                           |  string |         |                 |
|                            productdetails__limits__schemelimits__resetperiod                            |  string |         |                 |
|                        productdetails__limits__accountbalancelimits__balancetype                        |  string |         |                 |
|                        productdetails__limits__accountbalancelimits__description                        |  string |         |                 |
|                       productdetails__limits__accountbalancelimits__minimumamount                       |  string |         |                 |
|                       productdetails__limits__accountbalancelimits__maximumamount                       |  string |         |                 |
|                            productdetails__limits__productlimits__productkey                            |  string |         |                 |
|                            productdetails__limits__productlimits__productname                           |  string |         |                 |
|                            productdetails__limits__productlimits__producttype                           |  string |         |                 |
|                            productdetails__limits__productlimits__description                           |  string |         |                 |
|                           productdetails__limits__productlimits__maximumnumber                          |   int   |         |                 |
|                         productdetails__limits__fundinglimits__fundingmechanism                         |  string |         |                 |
|                            productdetails__limits__fundinglimits__description                           |  string |         |                 |
|                           productdetails__limits__fundinglimits__minimumamount                          |  string |         |                 |
|                           productdetails__limits__fundinglimits__maximumamount                          |  string |         |                 |
|                           productdetails__limits__fundinglimits__defaultamount                          |  string |         |                 |
|                                 productdetails__cards__cardstatusdefault                                |  string |         |                 |
|                                       productdetails__cards__type                                       |  string |         |                 |
|                                      productdetails__cards__scheme                                      |  string |         |                 |
|                        productdetails__cards__channeldefaultsettings__contactless                       | boolean |         |                 |
|                          productdetails__cards__channeldefaultsettings__chippin                         | boolean |         |                 |
|                            productdetails__cards__channeldefaultsettings__atm                           | boolean |         |                 |
|                            productdetails__cards__channeldefaultsettings__cnp                           | boolean |         |                 |
|                         productdetails__cards__channeldefaultsettings__magstripe                        | boolean |         |                 |
|                       productdetails__cards__channeldefaultsettings__international                      | boolean |         |                 |
|                          productdetails__cards__channeldefaultsettings__online                          | boolean |         |                 |
|                              productdetails__termsandconditions__identifier                             |  string |         |                 |
|                                 productdetails__termsandconditions__name                                |  string |         |                 |
|                             productdetails__termsandconditions__description                             |  string |         |                 |
|                               productdetails__termsandconditions__version                               |  string |         |                 |
|                             productdetails__termsandconditions__createddate                             |  string |         |                 |
|                              productdetails__termsandconditions__createdby                              |  string |         |                 |
|                             productdetails__termsandconditions__updateddate                             |  string |         |                 |
|                              productdetails__termsandconditions__updatedby                              |  string |         |                 |
|                            productdetails__termsandconditions__publisheddate                            |  string |         |                 |
|                                productdetails__termsandconditions__status                               |  string |         |                 |
|                              productdetails__termsandconditions__files__url                             |  string |         |                 |
|                            productdetails__termsandconditions__files__format                            |  string |         |                 |
|                        productdetails__internaldocumentation__salesaccesschannels                       |  string |         |                 |
|                       productdetails__internaldocumentation__servingaccesschannels                      |  string |         |                 |
|                           productdetails__internaldocumentation__mobilewallet                           |  string |         |                 |
|                            productdetails__internaldocumentation__producturl                            |  string |         |                 |
|                          productdetails__internaldocumentation__fraudriskrating                         |  string |         |                 |
|                        productdetails__internaldocumentation__fincrimeriskrating                        |  string |         |                 |
|                          productdetails__subscriptioncreationrule__lockedstatus                         | boolean |         |                 |
|                   productdetails__subscriptioncreationrule__requiredsignatoriesnumber                   |   int   |         |                 |
|                   productdetails__subscriptioncreationrule__defaultsubscriptionstatus                   |  string |         |                 |
|                                  productdetails__currency__currencycode                                 |  string |         |                 |
|                                    productdetails__currency__country                                    |  string |         |                 |
|                                      productdetails__teams__teamkey                                     |  string |         |                 |
|                                       productdetails__teams__write                                      | boolean |         |                 |
|                                  productdetails__customattributes__name                                 |  string |         |                 |
|                                 productdetails__customattributes__value                                 |  string |         |                 |
|                                  productdetails__documents__identifier                                  |  string |         |                 |
|                                     productdetails__documents__name                                     |  string |         |                 |
|                                  productdetails__documents__description                                 |  string |         |                 |
|                                    productdetails__documents__version                                   |  string |         |                 |
|                                  productdetails__documents__createddate                                 |  string |         |                 |
|                                   productdetails__documents__createdby                                  |  string |         |                 |
|                                  productdetails__documents__updateddate                                 |  string |         |                 |
|                                   productdetails__documents__updatedby                                  |  string |         |                 |
|                                 productdetails__documents__publisheddate                                |  string |         |                 |
|                                    productdetails__documents__status                                    |  string |         |                 |
|                                  productdetails__documents__files__url                                  |  string |         |                 |
|                                 productdetails__documents__files__format                                |  string |         |                 |
|                                 productdetails__feescharges__feecategory                                |  string |         |                 |
|                                   productdetails__feescharges__feetype                                  |  string |         |                 |
|                               productdetails__feescharges__feedescription                               |  string |         |                 |
|                             productdetails__feescharges__feetransactioncode                             |  string |         |                 |
|                               productdetails__feescharges__transactioncode                              |  string |         |                 |
|                                   productdetails__feescharges__taxrate                                  |  string |         |                 |
|                            productdetails__feescharges__statementdescription                            |  string |         |                 |
|                                   productdetails__feescharges__feename                                  |  string |         |                 |
|                                  productdetails__feescharges__feeamount                                 |  string |         |                 |
|                           productdetails__feescharges__taxstatementdescription                          |  string |         |                 |
|                            productdetails__feescharges__calculationfrequency                            |  string |         |                 |
|                            productdetails__feescharges__applicationfrequency                            |  string |         |                 |
|                                productdetails__feescharges__feerate__rate                               |  string |         |                 |
|                           productdetails__feescharges__feerate__notionalvalue                           |  string |         |                 |
|                          productdetails__feescharges__feerate__maximumfeeamount                         |  string |         |                 |
|                          productdetails__feescharges__feerate__minimumfeeamount                         |  string |         |                 |
|                          productdetails__feescharges__validityperiod__startdate                         |  string |         |                 |
|                           productdetails__feescharges__validityperiod__enddate                          |  string |         |                 |
|                           productdetails__feescharges__validityperiod__period                           |  string |         |                 |
|                        productdetails__feescharges__validityperiod__periodamount                        |  string |         |                 |
|                            productdetails__feescharges__feecap__cappingperiod                           |  string |         |                 |
|                            productdetails__feescharges__feecap__feecapamount                            |  string |         |                 |
|                          productdetails__feescharges__feecap__feecapoccurrence                          |  string |         |                 |
|                       productdetails__feescharges__feerules__inputparameters__name                      |  string |         |                 |
|                      productdetails__feescharges__feerules__inputparameters__value                      |  string |         |                 |
|                     productdetails__feescharges__feerules__inputparameters__operator                    |  string |         |                 |
|                      productdetails__feescharges__feerules__outputparameters__name                      |  string |         |                 |
|                      productdetails__feescharges__feerules__outputparameters__value                     |  string |         |                 |
|                           productdetails__feescharges__notificationapplication                          |   int   |         |                 |
|                            productdetails__creditinterest__fixedvariabletype                            |  string |         |                 |
|                               productdetails__creditinterest__includefees                               | boolean |         |                 |
|                              productdetails__creditinterest__roundingmethod                             |  string |         |                 |
|                                 productdetails__creditinterest__daycount                                |  string |         |                 |
|                               productdetails__creditinterest__interestrate                              |  string |         |                 |
|                            productdetails__creditinterest__tierbandcalcmethod                           |  string |         |                 |
|                           productdetails__creditinterest__applicationfrequency                          |  string |         |                 |
|                           productdetails__creditinterest__compoundingfrequency                          |  string |         |                 |
|                           productdetails__creditinterest__calculationfrequency                          |  string |         |                 |
|                             productdetails__creditinterest__balancecriteria                             |  string |         |                 |
|                       productdetails__creditinterest__interesttierband__startrange                      |  string |         |                 |
|                        productdetails__creditinterest__interesttierband__endrange                       |  string |         |                 |
|                      productdetails__creditinterest__interesttierband__tierbandrate                     |  string |         |                 |
|                         productdetails__creditinterest__interestrateindex__index                        |  string |         |                 |
|                         productdetails__creditinterest__interestrateindex__term                         |  string |         |                 |
|                      productdetails__creditinterest__interestrateindex__identifier                      |  string |         |                 |
|                          productdetails__creditinterest__interestrateindex__url                         |  string |         |                 |
|                             productdetails__overdraft__applicationfrequency                             |  string |         |                 |
|                                productdetails__overdraft__balancecriteria                               |  string |         |                 |
|                             productdetails__overdraft__calculationfrequency                             |  string |         |                 |
|                             productdetails__overdraft__compoundingfrequency                             |  string |         |                 |
|                                   productdetails__overdraft__daycount                                   |  string |         |                 |
|                                 productdetails__overdraft__interestrate                                 |  string |         |                 |
|                           productdetails__overdraft__overdrafttierband__buffer                          |  string |         |                 |
|                          productdetails__overdraft__overdrafttierband__endrange                         |  string |         |                 |
|                        productdetails__overdraft__overdrafttierband__interestrate                       |  string |         |                 |
|         productdetails__overdraft__overdrafttierband__overdraftfeescharges__applicationfrequency        |  string |         |                 |
|         productdetails__overdraft__overdrafttierband__overdraftfeescharges__calculationfrequency        |  string |         |                 |
|              productdetails__overdraft__overdrafttierband__overdraftfeescharges__feeamount              |  string |         |                 |
|        productdetails__overdraft__overdrafttierband__overdraftfeescharges__feecap__cappingperiod        |  string |         |                 |
|         productdetails__overdraft__overdrafttierband__overdraftfeescharges__feecap__feecapamount        |  string |         |                 |
|       productdetails__overdraft__overdrafttierband__overdraftfeescharges__feecap__feecapoccurrence      |  string |         |                 |
|             productdetails__overdraft__overdrafttierband__overdraftfeescharges__feecategory             |  string |         |                 |
|            productdetails__overdraft__overdrafttierband__overdraftfeescharges__feedescription           |  string |         |                 |
|   productdetails__overdraft__overdrafttierband__overdraftfeescharges__feerules__inputparameters__name   |  string |         |                 |
|   productdetails__overdraft__overdrafttierband__overdraftfeescharges__feerules__inputparameters__value  |  string |         |                 |
| productdetails__overdraft__overdrafttierband__overdraftfeescharges__feerules__inputparameters__operator |  string |         |                 |
|   productdetails__overdraft__overdrafttierband__overdraftfeescharges__feerules__outputparameters__name  |  string |         |                 |
|  productdetails__overdraft__overdrafttierband__overdraftfeescharges__feerules__outputparameters__value  |  string |         |                 |
|          productdetails__overdraft__overdrafttierband__overdraftfeescharges__feetransactioncode         |  string |         |                 |
|         productdetails__overdraft__overdrafttierband__overdraftfeescharges__statementdescription        |  string |         |                 |
|               productdetails__overdraft__overdrafttierband__overdraftfeescharges__taxrate               |  string |         |                 |
|      productdetails__overdraft__overdrafttierband__overdraftfeescharges__validityperiod__startdate      |  string |         |                 |
|       productdetails__overdraft__overdrafttierband__overdraftfeescharges__validityperiod__enddate       |  string |         |                 |
|        productdetails__overdraft__overdrafttierband__overdraftfeescharges__validityperiod__period       |  string |         |                 |
|     productdetails__overdraft__overdrafttierband__overdraftfeescharges__validityperiod__periodamount    |  string |         |                 |
|       productdetails__overdraft__overdrafttierband__overdraftfeescharges__notificationapplication       |   int   |         |                 |
|                         productdetails__overdraft__overdrafttierband__startrange                        |  string |         |                 |
|                          productdetails__overdraft__overdrafttierband__tiername                         |  string |         |                 |
|                     productdetails__overdraft__overdrafttierband__tierstatusdefault                     |  string |         |                 |
|                                productdetails__overdraft__roundingmethod                                |  string |         |                 |
|                        productdetails__overdraft__termsandconditions__identifier                        |  string |         |                 |
|                           productdetails__overdraft__termsandconditions__name                           |  string |         |                 |
|                        productdetails__overdraft__termsandconditions__description                       |  string |         |                 |
|                          productdetails__overdraft__termsandconditions__version                         |  string |         |                 |
|                        productdetails__overdraft__termsandconditions__createddate                       |  string |         |                 |
|                         productdetails__overdraft__termsandconditions__createdby                        |  string |         |                 |
|                        productdetails__overdraft__termsandconditions__updateddate                       |  string |         |                 |
|                         productdetails__overdraft__termsandconditions__updatedby                        |  string |         |                 |
|                       productdetails__overdraft__termsandconditions__publisheddate                      |  string |         |                 |
|                          productdetails__overdraft__termsandconditions__status                          |  string |         |                 |
|                        productdetails__overdraft__termsandconditions__files__url                        |  string |         |                 |
|                       productdetails__overdraft__termsandconditions__files__format                      |  string |         |                 |
|                              productdetails__overdraft__tierbandcalcmethod                              |  string |         |                 |
|                            productdetails__overdraft__notificationapplication                           |   int   |         |                 |
|                         productdetails__eligibility__ageeligibility__maximumage                         |   int   |         |                 |
|                         productdetails__eligibility__ageeligibility__minimumage                         |   int   |         |                 |
|                productdetails__eligibility__creditcheckeligibility__maximumpersonalincome               |  string |         |                 |
|                    productdetails__eligibility__creditcheckeligibility__maximumscore                    |  string |         |                 |
|                productdetails__eligibility__creditcheckeligibility__minimumpersonalincome               |  string |         |                 |
|                    productdetails__eligibility__creditcheckeligibility__minimumscore                    |  string |         |                 |
|                    productdetails__eligibility__creditcheckeligibility__scoringmodel                    |  string |         |                 |
|                   productdetails__eligibility__creditcheckeligibility__scoringprovider                  |  string |         |                 |
|                   productdetails__eligibility__creditcheckeligibility__scoringsegment                   |  string |         |                 |
|                     productdetails__eligibility__creditcheckeligibility__scoringtype                    |  string |         |                 |
|                           productdetails__eligibility__ideligibility__idproof                           |  string |         |                 |
|                            productdetails__eligibility__ideligibility__idtype                           |  string |         |                 |
|                             productdetails__eligibility__ideligibility__url                             |  string |         |                 |
|                   productdetails__eligibility__industryeligibility__customindustryname                  |  string |         |                 |
|                        productdetails__eligibility__industryeligibility__siccode                        |  string |         |                 |
|                 productdetails__eligibility__legalstructureeligibility__countryincluded                 |  string |         |                 |
|                  productdetails__eligibility__legalstructureeligibility__legalstructure                 |  string |         |                 |
|                  productdetails__eligibility__legalstructureeligibility__stateincluded                  |  string |         |                 |
|                        productdetails__eligibility__officereligibility__maxamount                       |  string |         |                 |
|                        productdetails__eligibility__officereligibility__minamount                       |  string |         |                 |
|                       productdetails__eligibility__officereligibility__officertype                      |  string |         |                 |
|                          productdetails__eligibility__othereligibility__amount                          |  string |         |                 |
|                        productdetails__eligibility__othereligibility__description                       |  string |         |                 |
|                         productdetails__eligibility__othereligibility__indicator                        | boolean |         |                 |
|                           productdetails__eligibility__othereligibility__name                           |  string |         |                 |
|                          productdetails__eligibility__othereligibility__period                          |  string |         |                 |
|                           productdetails__eligibility__othereligibility__type                           |  string |         |                 |
|                 productdetails__eligibility__professioneligibility__customprofessionname                |  string |         |                 |
|                       productdetails__eligibility__professioneligibility__soccode                       |  string |         |                 |
|                    productdetails__eligibility__residencyeligibility__countryincluded                   |  string |         |                 |
|                     productdetails__eligibility__residencyeligibility__minimumperiod                    |  string |         |                 |
|                  productdetails__eligibility__residencyeligibility__minimumperiodamount                 |  string |         |                 |
|                    productdetails__eligibility__residencyeligibility__residencestatus                   |  string |         |                 |
|                     productdetails__eligibility__residencyeligibility__residencytype                    |  string |         |                 |
|                     productdetails__eligibility__residencyeligibility__stateincluded                    |  string |         |                 |
|                      productdetails__eligibility__tradinghistoryeligibility__amount                     |  string |         |                 |
|                   productdetails__eligibility__tradinghistoryeligibility__description                   |  string |         |                 |
|                    productdetails__eligibility__tradinghistoryeligibility__indicator                    | boolean |         |                 |
|                    productdetails__eligibility__tradinghistoryeligibility__minmaxtype                   |  string |         |                 |
|                      productdetails__eligibility__tradinghistoryeligibility__period                     |  string |         |                 |
|                   productdetails__eligibility__tradinghistoryeligibility__tradingtype                   |  string |         |                 |
|                                 productdetails__statement__statementtype                                |  string |         |                 |
|                                productdetails__statement__statementperiod                               |  string |         |                 |
|                             productdetails__statement__statementdescription                             |  string |         |                 |
|                                   productdetails__statement__startday                                   |   int   |         |                 |
|                                  productdetails__statement__startmonth                                  |   int   |         |                 |
|                                productdetails__statements__statementtype                                |  string |         |                 |
|                               productdetails__statements__statementperiod                               |  string |         |                 |
|                             productdetails__statements__statementdescription                            |  string |         |                 |
|                                   productdetails__statements__startday                                  |   int   |         |                 |
|                                  productdetails__statements__startmonth                                 |   int   |         |                 |
|                                         kafka_message_timestamp                                         |  bigint |         |                 |
+---------------------------------------------------------------------------------------------------------+---------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['chase', 'party', 'document.imagetype']],
                'select ** from chase.party',
"""
+----------------------------+-----------+---------+-----------------+
|            name            |    type   | comment |    attributes   |
+----------------------------+-----------+---------+-----------------+
|          partykey          |   string  |         |                 |
|         tenantkey          |   string  |         |                 |
|         givenname          |   string  |         |                 |
|          lastname          |   string  |         |                 |
|         middlename         |   string  |         |                 |
|       preferredname        |   string  |         |                 |
|        mobilenumber        |   string  |         |                 |
|           email            |   string  |         |                 |
|   address__addressline1    |   string  |         |                 |
|   address__addressline2    |   string  |         |                 |
|   address__addressline3    |   string  |         |                 |
|   address__addressline4    |   string  |         |                 |
|   address__addressline5    |   string  |         |                 |
|     address__postcode      |   string  |         |                 |
|       address__city        |   string  |         |                 |
|      address__country      |   string  |         |                 |
|       address__state       |   string  |         |                 |
|    address__addresstype    |   string  |         |                 |
|      address__status       |   string  |         |                 |
|    address__createddate    |   string  |         |                 |
|    address__updateddate    |   string  |         |                 |
|         birthdate          |    int    |         |                 |
|           status           |   string  |         |                 |
|     devices__deviceid      |   string  |         |                 |
|     devices__pushtoken     |   string  |         |                 |
|    devices__devicetype     |   string  |         |                 |
|    devices__createddate    |   string  |         |                 |
|    devices__updateddate    |   string  |         |                 |
|  ecis__externalidentifier  |   string  |         |                 |
|       ecis__provider       |   string  |         |                 |
|     ecis__createddate      |   string  |         |                 |
|     ecis__updateddate      |   string  |         |                 |
|        document__id        |   string  |         |                 |
|     document__partykey     |   string  |         |                 |
|    document__imagetype     |   string  |         | attr_test_db.a1 |
|  document__documentnumber  |   string  |         |                 |
|  document__issuingcountry  |   string  |         |                 |
|   document__dateofexpiry   |   string  |         |                 |
|   document__dateofbirth    |   string  |         |                 |
|     document__surname      |   string  |         |                 |
|    document__firstname     |   string  |         |                 |
|   document__placeofbirth   |   string  |         |                 |
|   document__createddate    |   string  |         |                 |
|   document__updateddate    |   string  |         |                 |
|        createddate         |   string  |         |                 |
|        updateddate         |   string  |         |                 |
|   citizenship__partykey    |   string  |         |                 |
| citizenship__nationalities |   string  |         |                 |
|  citizenship__createddate  |   string  |         |                 |
|  citizenship__updateddate  |   string  |         |                 |
|  kafka_message_timestamp   | timestamp |         |                 |
+----------------------------+-----------+---------+-----------------+""".strip())

            self._validate(conn, db, 'a1',
                [['rs_complex', 'array_struct_array', 'a1.f1'],
                 ['rs_complex', 'array_struct_array', 'a1.a2']],
                'select ** from rs_complex.array_struct_array',
"""
+--------+--------+---------+-----------------+
|  name  |  type  | comment |    attributes   |
+--------+--------+---------+-----------------+
| a1__f1 | string |         | attr_test_db.a1 |
| a1__f2 | string |         |                 |
| a1__a2 | string |         | attr_test_db.a1 |
+--------+--------+---------+-----------------+""".strip())

# TODO: map support
#            self._validate(conn, db, 'a1',
#                [['functional', 'allcomplextypes', 'id'],
#                 ['functional', 'allcomplextypes', 'nested_struct_col.f1']],
#                'select ** from functional.allcomplextypes',
#"""
#+---------------------------+----------------------------+---------+-----------------+
#|            name           |            type            | comment |    attributes   |
#+---------------------------+----------------------------+---------+-----------------+
#|             id            |            int             |         | attr_test_db.a1 |
#|       int_array_col       |         array<int>         |         |                 |
#|      array_array_col      |     array<array<int>>      |         |                 |
#|       map_array_col       |   array<map<string,int>>   |         |                 |
#|      struct_array_col     |       array<struct<        |         |                 |
#|                           |          f1:bigint,        |         |                 |
#|                           |          f2:string         |         |                 |
#|                           |             >>             |         |                 |
#|        int_map_col        |      map<string,int>       |         |                 |
#|       array_map_col       |   map<string,array<int>>   |         |                 |
#|       struct_map_col      |     map<string,struct<     |         |                 |
#|                           |          f1:bigint,        |         |                 |
#|                           |          f2:string         |         |                 |
#|                           |             >>             |         |                 |
#|       int_struct_col      |          struct<           |         |                 |
#|                           |           f1:int,          |         |                 |
#|                           |            f2:int          |         |                 |
#|                           |             >              |         |                 |
#|     complex_struct_col    |          struct<           |         |                 |
#|                           |           f1:int,          |         |                 |
#|                           |        f2:array<int>,      |         |                 |
#|                           |      f3:map<string,int>    |         |                 |
#|                           |             >              |         |                 |
#|     nested_struct_col     |          struct<           |         |                 |
#|                           |           f1:int,          |         | attr_test_db.a1 |
#|                           |          f2:struct<        |         |                 |
#|                           |          f11:bigint,       |         |                 |
#|                           |          f12:struct<       |         |                 |
#|                           |            f21:bigint      |         |                 |
#|                           |               >            |         |                 |
#|                           |              >             |         |                 |
#|                           |             >              |         |                 |
#| complex_nested_struct_col |          struct<           |         |                 |
#|                           |           f1:int,          |         |                 |
#|                           |       f2:array<struct<     |         |                 |
#|                           |          f11:bigint,       |         |                 |
#|                           |     f12:map<string,struct< |         |                 |
#|                           |            f21:bigint      |         |                 |
#|                           |               >>           |         |                 |
#|                           |              >>            |         |                 |
#|                           |             >              |         |                 |
#|            item           |            int             |         |                 |
#|            year           |            int             |         |                 |
#|           month           |            int             |         |                 |
#+---------------------------+----------------------------+---------+-----------------+""".strip())

if __name__ == "__main__":
    unittest.main()
