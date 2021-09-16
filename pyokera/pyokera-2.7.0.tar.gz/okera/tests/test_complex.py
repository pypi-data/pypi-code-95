# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests for auth in PyOkera
#
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=no-else-return
# pylint: disable=too-many-lines


import datetime
import json
import os
import warnings

import pytest
import numpy

import requests

from okera._thrift_api import TRecordServiceException
from okera.tests import pycerebro_test_common as common

API_URL = "http://%s:%s" % \
    (os.environ['ODAS_TEST_HOST'], os.environ['ODAS_TEST_PORT_REST_SERVER'])

def get_scan_as_json(conn, dataset):
    data = conn.scan_as_json(
        dataset, strings_as_utf8=True,
        max_records=10, max_client_process_count=1)
    return data

def get_scan_as_pandas(conn, dataset):
    def convert_types(datum):
        if isinstance(datum, datetime.datetime):
            return datum.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        elif isinstance(datum, numpy.int64):
            return int(datum)
        elif isinstance(datum, dict):
            for key, value in datum.items():
                datum[key] = convert_types(value)
            return datum
        elif isinstance(datum, list):
            return [convert_types(child) for child in datum]

        return datum

    data = conn.scan_as_pandas(
        dataset, strings_as_utf8=True,
        max_records=10, max_client_process_count=1)
    data = data.replace({numpy.nan: None})
    data = data.to_dict('records')
    return convert_types(data)

def get_scan_from_rest(dataset):
    headers = {'content-type': 'application/json'}
    query = {'query': 'SELECT * FROM %s' % dataset}
    response = requests.post(
        API_URL + '/api/scan?records=10',
        json=query, headers=headers)
    result = json.loads(response.text)
    return result

def format(data):
    return json.dumps(data, sort_keys=True, indent=1)

@pytest.mark.parametrize("dataset", [
    'rs_complex.array_struct_array',
    'rs_complex.array_struct_t',
    'rs_complex.array_t',
    'rs_complex.avrotbl',
    'rs_complex.bytes_type',
    'rs_complex.bytes_type_file',
    'rs_complex.enum_type',
    'rs_complex.enum_type_default',
    'rs_complex.map_t',
    'rs_complex.market_decide_single_avro',
    'rs_complex.market_v20_single',
    'rs_complex.market_v30_single',
    'rs_complex.multiple_structs_nested',
    'rs_complex.strarray_t',
    'rs_complex.strarray_t_view',
    'rs_complex.struct_array_struct',
    'rs_complex.struct_nested',
    'rs_complex.struct_nested_s1',
    'rs_complex.struct_nested_s1_f1',
    'rs_complex.struct_nested_s1_s2',
    'rs_complex.struct_nested_view',
    'rs_complex.struct_t',
    'rs_complex.struct_t2',
    'rs_complex.struct_t3',
    'rs_complex.struct_t_id',
    'rs_complex.struct_t_s1',
    'rs_complex.struct_t_view',
    'rs_complex.struct_t_view2',
    'rs_complex.user_phone_numbers',
    'rs_complex.user_phone_numbers_map',
    'rs_complex.users',
    'rs_complex.view_over_multiple_structs',
    'rs_complex_parquet.array_struct_array',
    'rs_complex_parquet.array_struct_map_t',
    'rs_complex_parquet.array_struct_t',
    'rs_complex_parquet.array_struct_t2',
    'rs_complex_parquet.array_t',
    'rs_complex_parquet.bytes_type',
    'rs_complex_parquet.enum_type',
    'rs_complex_parquet.map_array',
    'rs_complex_parquet.map_array_t2',
    'rs_complex_parquet.map_struct_array_t',
    'rs_complex_parquet.map_struct_array_t_view',
    'rs_complex_parquet.map_struct_t',
    'rs_complex_parquet.map_struct_t_view',
    'rs_complex_parquet.map_t',
    'rs_complex_parquet.strarray_t',
    'rs_complex_parquet.struct_array_struct',
    'rs_complex_parquet.struct_nested',
    'rs_complex_parquet.struct_nested_s1',
    'rs_complex_parquet.struct_nested_s1_f1',
    'rs_complex_parquet.struct_nested_s1_s2',
    'rs_complex_parquet.struct_nested_view',
    'rs_complex_parquet.struct_t',
    'rs_complex_parquet.struct_t2',
    'rs_complex_parquet.struct_t3',
    'rs_complex_parquet.struct_t_id',
    'rs_complex_parquet.struct_t_s1',
    'rs_complex_parquet.struct_t_view',
    'rs_complex_parquet.struct_t_view2',
    # # The ones below don't work because the /scan API returns the wrong value
    # # for decimals
    # 'rs_complex_parquet.spark_all_mixed_compression',
    # 'rs_complex_parquet.spark_gzip',
    # 'rs_complex_parquet.spark_snappy',
    # 'rs_complex_parquet.spark_snappy_part',
    # 'rs_complex_parquet.spark_uncompressed',
    # 'rs_complex_parquet.spark_uncompressed_legacy_format',
    'customer.zd277_complex',
    'rs_json_format.complex_c1_case_sensitive',
    'rs_json_format.complex_c1_usecase',
    'rs_json_format.complex_nike_usecase',
    # NOT WORKING array of arrays is not allowed, scan error
    # 'rs_json_format.json_array_arrays',
    'rs_json_format.json_array_struct',
    'rs_json_format.json_arrays_test',
    # # These tables don't work because Pandas and JSON don't serialize to the
    # # exact same types (e.g. float vs int), even though the overall data is correct)
    # 'rs_json_format.json_inferred',
    # 'rs_json_format.json_primitives',
    # 'rs_json_format.json_primitives_inferred',
    'rs_json_format.json_struct',
    'rs_json_format.json_struct_array',
    'rs_json_format.json_struct_nested',
    'rs_json_format.primitives_with_array',
])

def test_basic(dataset):
    print("Testing: " + dataset)
    warnings.filterwarnings("ignore", message="numpy.dtype size changed")
    ctx = common.get_test_context()
    with common.get_planner(ctx) as conn:
        json_data = get_scan_as_json(conn, dataset)
        pandas_data = get_scan_as_pandas(conn, dataset)
        rest_data = get_scan_from_rest(dataset)
        assert format(json_data) == format(pandas_data)
        assert format(json_data) == format(rest_data)

def test_pandas_empty_result():
    warnings.filterwarnings("ignore", message="numpy.dtype size changed")
    ctx = common.get_test_context()
    with common.get_planner(ctx) as conn:
        pandas_data = conn.scan_as_pandas('select s1 from rs_complex.struct_t where 1=0')
        columns = list(pandas_data.columns)
        assert columns == ['s1']

        pandas_data = conn.scan_as_pandas(
            'select a1 from rs_complex.array_struct_array where 1=0')
        columns = list(pandas_data.columns)
        assert columns == ['a1']

        pandas_data = conn.scan_as_pandas(
            'select s1, s1.a1 as x from rs_complex.struct_array_struct where 1=0')
        columns = list(pandas_data.columns)
        assert columns == ['s1', 'x']

        pandas_data = conn.scan_as_pandas(
            'select * from rs_complex_parquet.map_struct_array_t where 1=0')
        columns = list(pandas_data.columns)
        assert columns == ['id', 'str_arr', 'struct_map']

def test_json_nonutf8():
    warnings.filterwarnings("ignore", message="numpy.dtype size changed")
    ctx = common.get_test_context()
    with common.get_planner(ctx) as conn:
        data = conn.scan_as_json(
            'select * from rs.encoding',
            strings_as_utf8=False)
        assert data == [{'uid': b'ABC123', 'message': b'\xe8 bene'}]

def test_null_map():
    warnings.filterwarnings("ignore", message="numpy.dtype size changed")
    ctx = common.get_test_context()
    with common.get_planner(ctx) as conn:
        json_data = get_scan_as_json(conn, 'fastparquet.map_array_parq')
        pandas_data = get_scan_as_pandas(conn, 'fastparquet.map_array_parq')
        assert format(json_data) == format(pandas_data)

def assert_scan_output(qry, expected, is_scan=True, as_utf8=False, limit=None):
    warnings.filterwarnings("ignore", message="numpy.dtype size changed")
    ctx = common.get_test_context()
    qry = qry.rstrip()
    with common.get_planner(ctx) as conn:
        print("Running query: %s" % qry)
        if is_scan:
            data = conn.scan_as_json(qry, strings_as_utf8=as_utf8, max_records=limit)
        else:
            data = conn.execute_ddl(qry)
        print("data is: ")
        print(data)
        #print(json.dumps(data, indent=2))
        print("expected is: ")
        print(expected)
        #print(json.dumps(expected, indent=2))
        assert data == expected

def assert_query(sql, expected, skip_inline_view=False, skip_count=False,
                 skip_catalog_view=False):
    assert_scan_output(sql, expected, as_utf8=True)
    if not skip_inline_view:
        wrapper_view = "SELECT * FROM (%s) do_not_use_name" % sql
        assert_scan_output(wrapper_view, expected, as_utf8=True)
    if not skip_count:
        count_view = "SELECT count(*) as cnt FROM (%s) do_not_use_name" % sql
        assert_scan_output(count_view, [{'cnt': len(expected)}], as_utf8=True)
    if not skip_catalog_view:
        with common.get_planner(common.get_test_context()) as conn:
            with common.TmpView(conn, sql) as view:
                assert_scan_output('SELECT * FROM %s' % view.name(),
                                   expected, as_utf8=True)
                count_view = 'SELECT count(*) as cnt FROM %s' % view.name()
                assert_scan_output(count_view, [{'cnt': len(expected)}], as_utf8=True)

def assert_scan_exception(qry, expected, is_scan=True):
    warnings.filterwarnings("ignore", message="numpy.dtype size changed")
    ctx = common.get_test_context()
    with common.get_planner(ctx) as conn:
        try:
            if is_scan:
                result = conn.scan_as_json(qry, strings_as_utf8=False)
            else:
                result = conn.execute_ddl(qry)
            assert result
        except TRecordServiceException as ex:
            assert expected in str(ex.detail)

# pylint: disable=bad-continuation
def test_unnest():
    assert_query('''
        select id, str_arr.item
        from rs_complex.strarray_t, rs_complex.strarray_t.str_arr
        ''',
        [{'id': 456, 'item': 'a'}, {'id': 456, 'item': 'b'},
         {'id': 457, 'item': 'cde'}, {'id': 457, 'item': ''},
         {'id': 458, 'item': 'fg'},
         {'id': 458, 'item': 'ijlk'}])

    assert_query('''
        select id, str_arr.item item
        from rs_complex.strarray_t, rs_complex.strarray_t.str_arr where id = 456
        ''',
        [{'id': 456, 'item': 'a'}, {'id': 456, 'item': 'b'}])

    # TODO(bug): Illegal reference to non-materialized tuple
    assert_query('''
        select a1.item, mask(a1.item.f1)
        from rs_complex.array_struct_t, rs_complex.array_struct_t.a1
        ''',
        [{'item': {'f2': 'c', 'f1': 'ab'}, 'mask(a1': {'item': {'f1)': 'XX'}}},
         {'item': {'f2': '', 'f1': 'def'}, 'mask(a1': {'item': {'f1)': 'XXX'}}},
         {'item': {'f2': 'ij', 'f1': 'g'}, 'mask(a1': {'item': {'f1)': 'X'}}}],
        skip_inline_view=True,
        skip_catalog_view=True)

    # TODO(usability): Error creating view: Invalid column/field name: item.f2
    assert_query('''
        select
            a1.item.f1 as raw_f1,
            concat(a1.item.f1, '_f1') as concat_f1,
            a1.item.f2,
            concat(a1.item.f2, '_f2') as concat_f2
        from rs_complex.array_struct_t, rs_complex.array_struct_t.a1
        ''',
        [{'raw_f1': 'ab', 'item': {'f2': 'c'},
          'concat_f1': 'ab_f1', 'concat_f2': 'c_f2'},
         {'raw_f1': 'def', 'item': {'f2': ''},
          'concat_f1': 'def_f1', 'concat_f2': '_f2'},
         {'raw_f1': 'g', 'item': {'f2': 'ij'},
          'concat_f1': 'g_f1', 'concat_f2': 'ij_f2'}],
        skip_catalog_view=True)

    # TODO(usability): Error creating view: Invalid column/field name: item.f2
    assert_query('''
        select a1.item.f2, mask(a1.item.f1)
        from rs_complex.array_struct_t, rs_complex.array_struct_t.a1
        ''',
        [{'item': {'f2': 'c'}, 'mask(a1': {'item': {'f1)': 'XX'}}},
         {'item': {'f2': ''}, 'mask(a1': {'item': {'f1)': 'XXX'}}},
         {'item': {'f2': 'ij'}, 'mask(a1': {'item': {'f1)': 'X'}}}],
        skip_catalog_view=True)

    assert_query('''
        select id, str_arr.item
        from rs_complex.strarray_t, rs_complex.strarray_t.str_arr
        where str_arr.item = 'cde'
        ''',
        [{'id': 457, 'item': 'cde'}])

    assert_scan_exception('''
        select tokenize(partyroles.item.partykey) as tokenized_key
        from chase.zd1238_4.partyroles
        ''',
        "AnalysisException: Correlated table 'chase.zd1238_4' must " \
        "be specified before the collection reference " \
        "'chase.zd1238_4.partyroles' in the from clause")

    # TODO: Make execddl return the raw output for explain plan, then enable this.
    # assert_scan_output(
    #     'EXPLAIN SELECT subscription_key_tokenized FROM chase.subscription_party_view',
    #     '00:SCAN HDFS [chase.zd1238_4] '\
    #     '    partitions=1/1 files=1 size=54.05KB '\
    #     '    predicates: !empty(chase.zd1238_4.partyroles)',
    #     False
    # )

    assert_query('''
        select a1.* from rs_complex.array_struct_t, rs_complex.array_struct_t.a1
        ''',
        [{'f2': 'c', 'f1': 'ab'},
         {'f2': '', 'f1': 'def'},
         {'f2': 'ij', 'f1': 'g'}])

    # TODO(bug): (inline and catalog view): Illegal reference to non-materialized tuple
    assert_query('''
        select a1.item.* from rs_complex.array_struct_t, rs_complex.array_struct_t.a1
        ''',
        [{'item': {'f2': 'c', 'f1': 'ab'}},
         {'item': {'f2': '', 'f1': 'def'}},
         {'item': {'f2': 'ij', 'f1': 'g'}}],
        skip_inline_view=True,
        skip_catalog_view=True)

    assert_query('''
        select a1, mask(a1.item.f1) as masked
        from rs_complex.array_struct_t, rs_complex.array_struct_t.a1
        ''',
        [{'a1': [{'f1': 'ab', 'f2': 'c'}], 'masked': 'XX'},
         {'a1': [{'f1': 'def', 'f2': ''}], 'masked': 'XXX'},
         {'a1': [{'f1': 'g', 'f2': 'ij'}], 'masked': 'X'}])

    assert_query('''
        select a1.* from rs_complex.array_struct_t, rs_complex.array_struct_t.a1
        ''',
        [{'f1': 'ab', 'f2': 'c'},
         {'f1': 'def', 'f2': ''},
         {'f1': 'g', 'f2': 'ij'}])

    # TODO(usability): Error creating view: Invalid column/field name: item.f2
    assert_query('''
        select a1.item.a2
        from rs_complex.array_struct_array, rs_complex.array_struct_array.a1
        ''',
        [{'item': {'a2': ['jk']}},
         {'item': {'a2': ['l']}},
         {'item': {'a2': ['']}}],
        skip_catalog_view=True)

    # TODO(bug): (inline and catalog view): Illegal reference to non-materialized tuple
    assert_query('''
        select a1.item
        from rs_complex.array_struct_array, rs_complex.array_struct_array.a1
        ''',
        [{'item': {'f1': 'ab', 'f2': 'c', 'a2': ['jk']}},
         {'item': {'f1': 'def', 'f2': '', 'a2': ['l']}},
         {'item': {'f1': 'g', 'f2': 'ij', 'a2': ['']}}],
        skip_inline_view=True,
        skip_catalog_view=True)

    assert_query('''
        select a1.item.f2 as f2, mask(a1.item.f1) as masked
        from rs_complex.array_struct_t, rs_complex.array_struct_t.a1
        ''',
        [{'f2': 'c', 'masked': 'XX'},
         {'f2': '', 'masked': 'XXX'},
         {'f2': 'ij', 'masked': 'X'}])

    assert_query('''
        select a1.item.f2 as f2, mask(a1.item.f1) as masked
        from rs_complex.array_struct_t, rs_complex.array_struct_t.a1
        where a1.item.f2 = 'c'
        ''',
        [{'f2': 'c', 'masked': 'XX'}])

    # TODO(bug): (inline and catalog view): Illegal reference to non-materialized tuple
    assert_query('''
        select a.s1 from rs_complex.struct_array_struct a, a.s1.a1
        ''',
        [{'s1': {'a1': [{'f1': 'ab', 'f2': 'c', 'a2': ['jk']},
                        {'f1': 'def', 'f2': '', 'a2': ['l']}]}},
         {'s1': {'a1': [{'f1': 'ab', 'f2': 'c', 'a2': ['jk']},
                        {'f1': 'def', 'f2': '', 'a2': ['l']}]}},
         {'s1': {'a1': [{'f1': 'g', 'f2': 'ij', 'a2': ['']}]}}],
        skip_inline_view=True,
        skip_catalog_view=True)

    # TODO(bug): (inline and catalog view): Illegal reference to non-materialized tuple
    assert_query('''
        select a.s1 from rs_complex.struct_array_struct a, a.s1.a1
        where a1.item.f1 = 'ab'
        ''',
        [{'s1': {'a1': [{'f1': 'ab', 'f2': 'c', 'a2': ['jk']},
                        {'f1': 'def', 'f2': '', 'a2': ['l']}]}}],
        skip_inline_view=True,
        skip_catalog_view=True)

    # FIXME(bug): Inline/catalog view returning empty
    assert_query('''
        select a.s1, a1.* from rs_complex.struct_array_struct a, a.s1.a1
        ''',
        [{'s1': {'a1': [{'f2': 'c', 'a2': ['jk'], 'f1': 'ab'},
                        {'f2': '', 'a2': ['l'], 'f1': 'def'}]},
          'f2': 'c', 'a2': ['jk'], 'f1': 'ab'},
         {'s1': {'a1': [{'f2': 'c', 'a2': ['jk'], 'f1': 'ab'},
                        {'f2': '', 'a2': ['l'], 'f1': 'def'}]},
          'f2': '', 'a2': ['l'], 'f1': 'def'},
         {'s1': {'a1': [{'f2': 'ij', 'a2': [''], 'f1': 'g'}]},
          'f2': 'ij', 'a2': [''], 'f1': 'g'}],
        skip_inline_view=True,
        skip_catalog_view=True)

    # FIXME(bug): Inline/catalog view returning empty
    assert_query('''
        select a.s1, a1.*
        from rs_complex.struct_array_struct a, a.s1.a1
        where a1.item.f1 = 'ab'
        ''',
        [{'f2': 'c', 'f1': 'ab', 'a2': ['jk'],
          's1': {'a1': [{'f2': 'c', 'f1': 'ab', 'a2': ['jk']},
                        {'f2': '', 'f1': 'def', 'a2': ['l']}]}}],
        skip_inline_view=True,
        skip_catalog_view=True)

    ## Test on many Array types in same table.
    assert_query('''
        select int32, int_arr, str_arr from rs_complex_parquet.spark_snappy
        ''',
        [{'int_arr': [1, 2], 'int32': 1, 'str_arr': ['t1', 't2']},
         {'int_arr': [3, 4], 'int32': 2, 'str_arr': ['t3', 't4']}])

    assert_query('''
        select int32, str_arr.item, int_arr
        from rs_complex_parquet.spark_gzip, rs_complex_parquet.spark_gzip.str_arr
        ''',
        [{'item': 't1', 'int_arr': [1, 2], 'int32': 1},
         {'item': 't2', 'int_arr': [1, 2], 'int32': 1},
         {'item': 't3', 'int_arr': [3, 4], 'int32': 2},
         {'item': 't4', 'int_arr': [3, 4], 'int32': 2}])

    assert_query('''
        select int32,
            int_arr.item as i,
            str_arr.item as s,
            mask(str_arr.item) as str_masked
        from
            rs_complex_parquet.spark_snappy,
            rs_complex_parquet.spark_snappy.str_arr,
            rs_complex_parquet.spark_snappy.int_arr
        ''',
        [{'i': 1, 's': 't1', 'str_masked': 'XX', 'int32': 1},
         {'i': 2, 's': 't1', 'str_masked': 'XX', 'int32': 1},
         {'i': 1, 's': 't2', 'str_masked': 'XX', 'int32': 1},
         {'i': 2, 's': 't2', 'str_masked': 'XX', 'int32': 1},
         {'i': 3, 's': 't3', 'str_masked': 'XX', 'int32': 2},
         {'i': 4, 's': 't3', 'str_masked': 'XX', 'int32': 2},
         {'i': 3, 's': 't4', 'str_masked': 'XX', 'int32': 2},
         {'i': 4, 's': 't4', 'str_masked': 'XX', 'int32': 2}])

    assert_query('''
        select
            int32,
            inner_str_arr.item as srt_arr_str,
            mask(inner_str_arr.item) as masked_srt_arr_str,
            mask(struct_arr.item.inner_str) masked_struct_str
        from
            rs_complex_parquet.spark_snappy,
            rs_complex_parquet.spark_snappy.struct_t.inner_str_arr,
            rs_complex_parquet.spark_snappy.struct_arr
        ''',
        [{'masked_srt_arr_str': 'XXX', 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'srt_arr_str': 'In1'},
         {'masked_srt_arr_str': 'XXX', 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'srt_arr_str': 'In1'},
         {'masked_srt_arr_str': 'XXX', 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'srt_arr_str': 'In2'},
         {'masked_srt_arr_str': 'XXX', 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'srt_arr_str': 'In2'},
         {'masked_srt_arr_str': 'XXX', 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'srt_arr_str': 'In7'},
         {'masked_srt_arr_str': 'XXX', 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'srt_arr_str': 'In7'},
         {'masked_srt_arr_str': 'XXX', 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'srt_arr_str': 'In8'},
         {'masked_srt_arr_str': 'XXX', 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'srt_arr_str': 'In8'}])

    ## One test with array of int, string and struct<string>.
    ## we may not write many such tests as its too verbose output but this should
    ## be good coverage for flattened output.
    assert_query('''
        select
            int32,
            int_arr.item as flat_int,
            mask(str_arr.item) as masked_str,
            struct_arr.item.inner_str as raw_struct_str,
            mask(struct_arr.item.inner_str) masked_struct_str
        from
            rs_complex_parquet.spark_snappy,
            rs_complex_parquet.spark_snappy.str_arr,
            rs_complex_parquet.spark_snappy.int_arr,
            rs_complex_parquet.spark_snappy.struct_arr
        ''',
        [{'masked_str': 'XX', 'flat_int': 1, 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr2'},
         {'masked_str': 'XX', 'flat_int': 1, 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr3'},
         {'masked_str': 'XX', 'flat_int': 2, 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr2'},
         {'masked_str': 'XX', 'flat_int': 2, 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr3'},
         {'masked_str': 'XX', 'flat_int': 1, 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr2'},
         {'masked_str': 'XX', 'flat_int': 1, 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr3'},
         {'masked_str': 'XX', 'flat_int': 2, 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr2'},
         {'masked_str': 'XX', 'flat_int': 2, 'int32': 1,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr3'},
         {'masked_str': 'XX', 'flat_int': 3, 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr5'},
         {'masked_str': 'XX', 'flat_int': 3, 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr6'},
         {'masked_str': 'XX', 'flat_int': 4, 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr5'},
         {'masked_str': 'XX', 'flat_int': 4, 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr6'},
         {'masked_str': 'XX', 'flat_int': 3, 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr5'},
         {'masked_str': 'XX', 'flat_int': 3, 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr6'},
         {'masked_str': 'XX', 'flat_int': 4, 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr5'},
         {'masked_str': 'XX', 'flat_int': 4, 'int32': 2,
          'masked_struct_str': 'XXXXXXXXX', 'raw_struct_str': 'InnerStr6'}])

    assert_query('''
        select id, str_arr.item item
        from rs_complex.strarray_t, rs_complex.strarray_t.str_arr where id = 456
        ''',
        [{'item': 'a', 'id': 456}, {'item': 'b', 'id': 456}])

    assert_scan_exception('''
        select id, str_arr.item item
        from rs_complex.strarray_t.str_arr, rs_complex.strarray_t where id = 456
        ''',
        "Correlated table 'rs_complex.strarray_t' must be specified before " \
        "the collection reference 'rs_complex.strarray_t.str_arr' in the from clause ")

    assert_query('''
        select int32, int_arr.item
        from rs_complex_parquet.spark_gzip, rs_complex_parquet.spark_gzip.int_arr
        ''',
        [{'int32': 1, 'item': 1}, {'int32': 1, 'item': 2},
         {'int32': 2, 'item': 3}, {'int32': 2, 'item': 4}]
    )

    assert_query('''
        select int32, int_arr.item
        from rs_complex_parquet.spark_gzip, rs_complex_parquet.spark_gzip.int_arr
        ''',
        [{'int32': 1, 'item': 1}, {'int32': 1, 'item': 2},
         {'int32': 2, 'item': 3}, {'int32': 2, 'item': 4}]
    )

    assert_query('''
        select * from rs_complex.pn_view
        ''',
        [{'uid': 123, 'item': '111-222-3333'}, {'uid': 123, 'item': '444-555-6666'},
         {'uid': 234, 'item': '222-333-4444'}, {'uid': 234, 'item': '555-666-7777'},
         {'uid': 345, 'item': '111-222-5555'}]
    )

    assert_query('''
        select count(*) as unnest_view_count from rs_complex.pn_view
        ''',
        [{'unnest_view_count': 5}]
    )

    assert_query('''
        select count(*) as unnest_view_count from rs_complex.pn_view
        where uid = 234
        ''',
        [{'unnest_view_count': 2}]
    )

    ## Some GROUP BY/HAVING tests
    assert_query('''
        select count(item) as item_count, uid from rs_complex.pn_view
        GROUP BY uid HAVING count(item) > 1
        ''',
        [{'item_count': 2, 'uid': 123}, {'item_count': 2, 'uid': 234}]
    )
    assert_query('''
        select count(item) as item_count, uid from rs_complex.pn_view
        GROUP BY uid HAVING count(item) >= 1'''
        ,
        [{'item_count': 1, 'uid': 345}, {'item_count': 2, 'uid': 123},
         {'item_count': 2, 'uid': 234}]
    )
    assert_query('''
        select count(item) as item_count, uid from rs_complex.pn_view
        GROUP BY uid HAVING count(item) = 1
        ''',
        [{'item_count': 1, 'uid': 345}]
    )

def test_array_of_arrays():
    assert_scan_output(
        'select * from rs_json_format.json_array_arrays',
        [{'arr_outer': [[1, 2], [1200000, 345600]], 'arr_string': [b'a', b'b'],
          'str_val': b'abc', 'int_val': 1},
         {'arr_outer': [[3, 4], [1200000, 345600]], 'arr_string': [b'c', b'd'],
          'str_val': b'def', 'int_val': 4}])

    assert_scan_output(
        'select * from parquet_testing.nested_lists_snappy',
        [{'a': [[[b'a', b'b'], [b'c']], [None, [b'd']]], 'b': 1},
         {'a': [[[b'a', b'b'], [b'c', b'd']], [None, [b'e']]], 'b': 1},
         {'a': [[[b'a', b'b'], [b'c', b'd'], [b'e']], [None, [b'f']]], 'b': 1}])

    assert_scan_output(
        'select payload.shas from rs_json_format.gharch_test_data ' +
        'where id = \'1201654257\'',
        [
            {'payload':
                {'shas':[
                        [b'4d1085635d642ba60071341dd46d38216bff1313',
                        b'86d2a548fee49abc43bd1c251300d7089748195b@mitechie.com',
                        b'Garden it up',
                        b'Richard Harding'
                        ]
                    ]
                }
            }
        ]
    )

def test_full_unnest_with_long_column_names():
    ctx = common.get_test_context()
    with common.get_planner(ctx) as conn:
        plan = conn.plan('select ** from `rs_json_format`.`deeply_nested_json`')
        schema_cols = plan.schema.cols

        assert len(schema_cols) == 4
        assert schema_cols[0].name == 'ashort'
        assert schema_cols[1].name == 'a12__b12__c12__d12__e12__f12__g12__h12__i12__j12__k12__l1234567890__m1234567890__n1234567890__o1234567890__p1234567890__foo'
        assert schema_cols[2].name == 'a12__b12__c12__d12__e12__f12__g12__h12__i12__j12__k12__l12__m1234567890__n1234567890__o1234567890__p1234567890__baz__bar'
        assert schema_cols[3].name == 'a12__b12__c12__d12__e12__f12__g12__h12__i12__j12__k12__l12__m1234567890__n1234567890__array_o1234567890__p1234567890__baz__bar'


def test_full_unnest():
    def validate(t, expected):
        assert_scan_output('select ** from %s' % t, expected, as_utf8=True, limit=1)

    # Array types
    validate('rs_complex.array_t', [{'int_arr': 1, 'id': 456}])
    validate('rs_complex.array_struct_t', [{'a1__f2': 'c', 'a1__f1': 'ab'}])
    validate('rs_complex.strarray_t', [{'str_arr': 'a', 'id': 456}])
    validate('rs_complex.array_struct_array',
             [{'a1__a2': 'jk', 'a1__f1': 'ab', 'a1__f2': 'c'}])
    validate('rs_complex.struct_array_struct',
             [{'s1__a1__a2': 'jk', 'id': 100, 's1__a1__f2': 'c',
               's1__a1__f1': 'ab'}])
    validate('rs_complex.multiple_structs_nested',
             [{'struct1__array1__subfield11': 'namename22',
               'struct1__array1__subfield12': 'valuevalue22',
               'struct1__array2__subfield21': 'code5787878'}])
    validate('rs_complex.user_phone_numbers',
             [{'phone_numbers__uid': 123,
               'phone_numbers__numbers': '111-222-3333',
               'phone_numbers__user': 'john'}])
    validate('rs_complex.avrotbl',
             [{'messages__incident__escalation_policy__type':
                  'escalation_policy_reference',
               'messages__incident__service__acknowledgement_timeout': None,
               'messages__incident__escalation_policy__self': 'S2R6',
               'messages__incident__alert_counts__triggered': 1,
               'messages__incident__first_trigger_log_entry__self': 'BHVZH38',
               'messages__incident__assignments__assignee__html_url': '',
               'messages__incident__alert_counts__all': 1,
               'messages__incident__assignments__assignee__id': 'PJ7CR',
               'messages__incident__service__integrations__type':
                  'event_transformer_api_inbound_integration_reference',
               'messages__webhook__webhook_object__html_url': 'P7RAELC',
               'messages__incident__service__name': 'Card',
               'messages__incident__service__teams__type': 'team_reference',
               'messages__incident__service__escalation_policy__id': 'R6',
               'messages__incident__basic_alert_grouping': None,
               'messages__incident__service__summary': 'Card',
               'messages__incident__last_status_change_by__type': 'service_reference',
               'messages__log_entries__id': 'R3OWU2PBO5L90DLF76BS0LTTEV',
               'messages__incident__teams__html_url': '59ZN5',
               'messages__incident__pending_actions': None,
               'messages__incident__service__integrations__summary': 'Splunk',
               'messages__log_entries__service__self': 'P7RAELC',
               'messages__log_entries__channel__type': 'timeout',
               'messages__incident__last_status_change_by__id': 'ELC',
               'messages__incident__impacted_services__id': 'AELC',
               'messages__webhook__accounts_addon': None,
               'messages__incident__impacted_services__html_url': 'AELC',
               'messages__incident__teams__self': '59ZN5',
               'messages__incident__incident_key': None,
               'messages__webhook__outbound_integration__html_url': None,
               'messages__incident__service__alert_grouping_timeout': None,
               'messages__incident__escalation_policy__id': 'S2R6',
               'messages__incident__service__teams__self': 'P059ZN5',
               'messages__incident__service__incident_urgency_rule__type': 'constant',
               'messages__incident__service__support_hours': None,
               'messages__webhook__name': 'Data Pipeline Integration Queue',
               'messages__incident__first_trigger_log_entry__html_url': 'BHVZH38',
               'messages__log_entries__teams__summary': 'Card-TSYS-ApplePay',
               'messages__incident__acknowledgements': None,
               'messages__incident__teams__summary': 'Card',
               'messages__incident__service__integrations__id': 'SEA',
               'messages__log_entries__contexts': None,
               'messages__incident__service__alert_creation':
                  'create_alerts_and_incidents',
               'messages__id': 'f73f-11e8-af44-0a5ff7c88466',
               'messages__incident__service__response_play': None,
               'messages__incident__service__integrations__html_url': 'SEA',
               'messages__incident__service__metadata__conference_url': '',
               'messages__incident__first_trigger_log_entry__summary':
                  'Triggered through the API',
               'messages__incident__service__teams__html_url': 'P059ZN5',
               'messages__incident__service__id': 'ELC',
               'messages__incident__service__escalation_policy__summary': 'ApplePay',
               'messages__webhook__html_url': None,
               'messages__log_entries__teams__type': 'team_reference',
               'messages__incident__responder_requests': None,
               'messages__webhook__type': 'webhook',
               'messages__log_entries__teams__self': 'P059ZN5',
               'messages__incident__type': 'incident',
               'messages__incident__assignments__at': '2018-12-03T20:58:58Z',
               'messages__incident__service__escalation_policy__type':
                  'escalation_policy_reference',
               'messages__incident__last_status_change_by__summary': 'Card',
               'messages__log_entries__self': 'TTEV',
               'messages__incident__service__alert_grouping': None,
               'messages__log_entries__service__id': 'P7RAELC',
               'messages__incident__service__last_incident_timestamp':
                  '2018-12-03T16:08:55-05:00',
               'messages__incident__service__created_at': '2018-04-10T18:05:25-04:00',
               'messages__incident__service__metadata__conference_number': '',
               'messages__webhook__id': 'P9S8SCO',
               'messages__log_entries__agent__id': '7RAELC',
               'messages__incident__incident_number': 2317252,
               'messages__incident__assignments__assignee__self': '',
               'messages__incident__service__addons': None,
               'messages__log_entries__summary': 'Resolved by timeout',
               'messages__incident__service__status': 'critical',
               'messages__log_entries__service__type': 'service_reference',
               'messages__incident__service__teams__id': 'P059ZN5',
               'messages__incident__service__self': 'ELC',
               'messages__incident__subscriber_requests': None,
               'messages__incident__service__description': 'MANAGEMENT',
               'messages__log_entries__agent__summary': 'Card',
               'messages__webhook__webhook_object__id': 'P7RAELC',
               'messages__webhook__description': None,
               'messages__incident__created_at': '2018-12-03T20:58:58Z',
               'messages__incident__summary': 'TSYS',
               'messages__incident__first_trigger_log_entry__id': 'BHVZH38',
               'messages__log_entries__teams__id': 'P059ZN5',
               'messages__incident__service__type': 'service',
               'messages__incident__impacted_services__summary': 'Card',
               'messages__incident__last_status_change_by__html_url': 'ELC',
               'messages__log_entries__agent__type': 'service_reference',
               'messages__incident__alert_grouping': None,
               'messages__incident__impacted_services__type': 'service_reference',
               'messages__incident__resolve_reason': None,
               'messages__incident__self': 'BK744Y',
               'messages__incident__impacted_services__self': 'AELC',
               'messages__incident__html_url': '744Y',
               'messages__incident__urgency': 'low',
               'messages__log_entries__incident__summary': ' IDs',
               'messages__log_entries__type': 'resolve_log_entry',
               'messages__created_on': '2018-12-03T21:08:58Z',
               'messages__webhook__endpoint_url': '',
               'messages__incident__description': 'IDs',
               'messages__incident__service__integrations__self': 'SEA',
               'messages__log_entries__service__html_url': 'P7RAELC',
               'messages__log_entries__incident__self': 'PBK744Y',
               'messages__log_entries__incident__type': 'incident_reference',
               'messages__incident__service__html_url': 'ELC',
               'messages__webhook__outbound_integration__summary': 'Generic V2 Webhook',
               'messages__incident__priority': None,
               'messages__webhook__webhook_object__self': 'P7RAELC',
               'messages__webhook__webhook_object__summary': 'Card',
               'messages__incident__assignments__assignee__type': 'user_reference',
               'messages__log_entries__service__summary':
                  'Card-TSYS-ApplePay-ENVPRTSYSPLATFORMMANAGEMENT',
               'messages__log_entries__teams__html_url': 'P059ZN5',
               'messages__webhook__outbound_integration__id': 'PJFWPEP',
               'messages__log_entries__html_url': None,
               'messages__incident__last_status_change_by__self': 'ELC',
               'messages__incident__service__escalation_policy__self': 'R6',
               'messages__incident__id': '744Y',
               'messages__incident__escalation_policy__summary': 'ApplePay',
               'messages__incident__service__auto_resolve_timeout': 600,
               'messages__incident__is_mergeable': True,
               'messages__incident__service__incident_urgency_rule__urgency': 'low',
               'messages__webhook__summary': 'Data Pipeline Integration Queue',
               'messages__incident__last_status_change_at': '2018-12-03T21:08:58Z',
               'messages__incident__service__scheduled_actions': None,
               'messages__log_entries__incident__html_url': 'PBK744Y',
               'messages__webhook__self': 'P9S8SCO',
               'messages__log_entries__incident__id': 'PBK744Y',
               'messages__log_entries__created_at': '2018-12-03T21:08:58+00:00',
               'messages__incident__teams__id': '59ZN5',
               'messages__incident__escalation_policy__html_url': 'S2R6',
               'messages__log_entries__agent__html_url': '7RAELC',
               'messages__incident__alert_counts__resolved': 0,
               'messages__event': 'incident.resolve',
               'messages__incident__teams__type': 'team_reference',
               'messages__webhook__outbound_integration__self': 'PJFWPEP',
               'messages__incident__service__escalation_policy__html_url': 'R6',
               'messages__webhook__webhook_object__type': 'service_reference',
               'messages__incident__first_trigger_log_entry__type':
                  'trigger_log_entry_reference',
               'messages__incident__service__teams__summary': 'ApplePay',
               'messages__log_entries__agent__self': '7RAELC',
               'messages__webhook__outbound_integration__type':
                  'outbound_integration_reference',
               'messages__incident__assignments__assignee__summary': '',
               'messages__incident__external_references': None,
               'messages__incident__incidents_responders': None,
               'messages__incident__title': 'TSYS',
               'messages__incident__status': 'resolved'}])

    # Map types
    validate('rs_complex.map_t', [{'str_map__value': 'ab', 'id': 1, 'str_map__key': '1'}])
    validate('rs_complex.market_v20_single',
             [{'enterpriseeventenvelope__correlationid': None,
               'domainpayload__productid': '9998',
               'enterpriseeventenvelope__eventid': '83fe66b39ff3442b8a928f7299e43af6',
               'domainpayload__productdecisiontimestamp': '2018-04-03T15:12:17.194Z',
               'domainpayload__applicationid': '1522768336584',
               'domainpayload__externalkeys__key': 'cardCustomerRecognitionDecisionKey',
               'year': '2018',
               'domainpayload__decision': 'DECLINE',
               'domainpayload__turndownreasoncodes': None,
               'enterpriseeventenvelope__eventaction': 'Created',
               'enterpriseeventenvelope__eventprefix': '',
               'enterpriseeventenvelope__providerid': '40e840a6fce64ec78448baff73a14c04',
               'domainpayload__createdby': None,
               'enterpriseeventenvelope__eventdataquality__errorruleids': None,
               'enterpriseeventenvelope__domainpayloadversion': 'v1',
               'domainpayload__offercode': None,
               'enterpriseeventenvelope__eventqualifier': '',
               'domainpayload__concerntypes__value': None,
               'domainpayload__temporarycreditline': 0,
               'domainpayload__externalkeys__value': 'f4952756-0504-4b39-b178-b97f1dec2a6d',
               'domainpayload__creditline': 0,
               'domainpayload__productdecisionid': '83fe66b39ff3442b8a928f7299e43af6',
               'enterpriseeventenvelope__eventoccurrencetimestamp':
                  '2018-04-17T15:49:35.507',
               'domainpayload__concerntypes__key': None,
               'enterpriseeventenvelope__eventdataquality__executedrulesetid': '',
               'enterpriseeventenvelope__eventdataquality__failedruleids': None}])

    validate('rs_complex.market_v30_single',
             [{'domainpayload__temporarycreditline': 0,
               'enterpriseeventenvelope__eventdataquality__failedruleids':
                  '9566f8a1-97b2-42ef-94e8-2b8c38fb9d84',
               'domainpayload__createdby': None,
               'enterpriseeventenvelope__eventprefix': '',
               'enterpriseeventenvelope__providerid': '40e840a6fce64ec78448baff73a14c04',
               'domainpayload__decision': 'APPROVE',
               'year': '2018',
               'domainpayload__concerntypes__value': 'notRequired',
               'domainpayload__productdecisiontimestamp': '2018-11-02T02:00:31.973Z',
               'domainpayload__turndownreasoncodes': None,
               'domainpayload__externalkeys__value': '1f725222-30ab-4c1f-b39a-f1b60904046f',
               'domainpayload__creditline': 3000,
               'domainpayload__concerntypes__key': 'incomeVerification',
               'enterpriseeventenvelope__domainpayloadversion': 'v1',
               'enterpriseeventenvelope__eventid': '259bdeb898934724a5caf496a3a4ec9d',
               'enterpriseeventenvelope__eventdataquality__executedrulesetid':
                  '04ef8e1b-22ff-40de-8bdd-87bfc580e4b6',
               'domainpayload__offercode': '1280935',
               'domainpayload__productid': '3665',
               'domainpayload__applicationid': '10000057919105',
               'enterpriseeventenvelope__correlationid': None,
               'enterpriseeventenvelope__eventdataquality__errorruleids': None,
               'enterpriseeventenvelope__eventqualifier': '',
               'enterpriseeventenvelope__eventaction': 'Created',
               'enterpriseeventenvelope__eventoccurrencetimestamp':
                  '2018-11-02T02:00:31.977',
               'domainpayload__externalkeys__key': 'abilityToPayReferenceId',
               'domainpayload__productdecisionid': '259bdeb898934724a5caf496a3a4ec9d'}])
    validate('rs_complex.user_phone_numbers_map',
             [{'username': 'Alex', 'contact_numbers__value': '444-555-6666',
               'contact_numbers__key': 'work', 'uid': 1}])

    # Just flat or structs
    validate('rs_complex.bytes_type', [{'id': 1, 'v': 'abc'}])
    validate('rs_complex.bytes_type_file', [{'id': 1, 'v': 'abc'}])
    validate('rs_complex.enum_type', [{'id': 1, 'v': 'ENUM_1'}])
    validate('rs_complex.enum_type_default', [{'id': 1, 'v': 'ENUM_1'}])
    # This is non deterministic when selecting just 1 row
    #validate('rs_complex.market_decide_single_avro',
    #         [{'applicationid': '10000057919105', 'productid': '3665',
    #           'createdby': None, 'decision': 'APPROVE',
    #           'productdecisiontimestamp': '2018-11-02T02:00:31.973Z',
    #           'offercode': '1280935',
    #           'productdecisionid': '259bdeb898934724a5caf496a3a4ec9d', 'year': '2018'}])
    validate('rs_complex.struct_nested',
             [{'id': 123, 's1__f1': 'field1', 's1__s2__f3': '2', 's1__s2__f2': 2}])
    validate('rs_complex.struct_nested_s1',
             [{'s1__s2__f3': '2', 's1__f1': 'field1', 's1__s2__f2': 2}])
    validate('rs_complex.struct_nested_s1_f1', [{'f1': 'field1'}])
    validate('rs_complex.struct_nested_s1_s2', [{'s2__f2': 2, 's2__f3': '2'}])
    validate('rs_complex.struct_nested_view',
             [{'id': 123, 's1__s2__f2': 2, 's1__f1': 'field1', 's1__s2__f3': '2'}])
    validate('rs_complex.struct_t', [{'s1__f2': 1, 's1__f1': 'field1', 'id': 123}])
    validate('rs_complex.struct_t2',
             [{'id': 123, 's2__f1': 'field11', 's2__f2': 11,
               's1__f2': 1, 's1__f1': 'field1'}])
    validate('rs_complex.struct_t3',
             [{'s1__f1': 'field1', 's2__f2': 11,
               'id': 123, 's2__f1': 'field11', 's1__f2': 1}])
    validate('rs_complex.struct_t_id', [{'id': 123}])

    validate('rs_complex.struct_t_s1', [{'s1__f2': 1, 's1__f1': 'field1'}])
    validate('rs_complex.struct_t_view', [{'s1__f1': 'field1', 's1__f2': 1, 'id': 123}])
    validate('rs_complex.struct_t_view2', [{'id': 123, 's1__f2': 1, 's1__f1': 'field1'}])
    validate('rs_complex.users',
             [{'age': 25, 'uid': 100, 'address__city': 'san francisco',
               'user': 'alice', 'address__state': 'ca'}])

# Commented out ones are failing due to views, maps, or some other corner case.
# TODO: debug them
@pytest.mark.parametrize("unnest_dataset", [
    # View, not expected to work
    #'chase.cte_view',
    #'chase.redacted_ledger_balance_view',
    #'chase.subscription_party_view',

    # TODO: Something wrong with view.
    #'chase.subscription_view',
    #'rs_complex.strarray_t_view',
    #'rs_complex.view_over_multiple_structs',

    # TODO: Map
    #'rs_complex.map_t',
    #'rs_complex.market_v20_single',
    #'rs_complex.market_v30_single',
    #'rs_complex.user_phone_numbers_map',
    #'rs_complex_parquet.array_struct_map_t',
    #'rs_complex_parquet.map_array',
    #'rs_complex_parquet.map_array_t2',
    #'rs_complex_parquet.map_struct_array_t',
    #'rs_complex_parquet.map_struct_array_t_view',
    #'rs_complex_parquet.map_struct_t',
    #'rs_complex_parquet.map_struct_t_view',
    #'rs_complex_parquet.map_t',

    'chase.feescharges_view',
    'chase.ledger_balance',
    'chase.ledger_transaction',
    'chase.party',
    'chase.second_level',
    'chase.struct_t',
    'chase.struct_view',
    'chase.subscription',
    'chase.subscription_currency',

    # TODO: either hung or taking very long
    'chase.product',
    'chase.zd1211',
    'chase.zd1211_1',
    #'chase.zd1211_join_view',
    #'chase.zd1211_view',
    #'chase.zd1238',
    #'chase.zd1238_1',

    'chase.zd1238_2',
    'chase.zd1238_3',
    'chase.zd1238_4',
    'chase.zd1238_5',
    'chase.zd1238_6',
    'chase.zd1238_7',
    'chase.zd1238_8',
    'chase.zd1238_9',

    'rs_complex.array_struct_array',
    'rs_complex.array_struct_t',
    'rs_complex.array_t',
    'rs_complex.avrotbl',
    'rs_complex.bytes_type',
    'rs_complex.bytes_type_file',
    'rs_complex.enum_type',
    'rs_complex.enum_type_default',
    'rs_complex.market_decide_single_avro',
    'rs_complex.multiple_structs_nested',
    'rs_complex.strarray_t',
    'rs_complex.struct_array_struct',
    'rs_complex.struct_nested',
    'rs_complex.struct_nested_s1',
    'rs_complex.struct_nested_s1_f1',
    'rs_complex.struct_nested_s1_s2',
    'rs_complex.struct_nested_view',
    'rs_complex.struct_t',
    'rs_complex.struct_t2',
    'rs_complex.struct_t3',
    'rs_complex.struct_t_id',
    'rs_complex.struct_t_s1',
    'rs_complex.struct_t_view',
    'rs_complex.struct_t_view2',
    'rs_complex.user_phone_numbers',
    'rs_complex.users',
    'rs_complex_parquet.array_struct_array',
    'rs_complex_parquet.array_struct_t',
    'rs_complex_parquet.array_struct_t2',
    'rs_complex_parquet.array_t',
    'rs_complex_parquet.bytes_type',
    'rs_complex_parquet.enum_type',
    'rs_complex_parquet.strarray_t',
    'rs_complex_parquet.struct_array_struct',
    'rs_complex_parquet.struct_nested',
    'rs_complex_parquet.struct_nested_s1',
    'rs_complex_parquet.struct_nested_s1_f1',
    'rs_complex_parquet.struct_nested_s1_s2',
    'rs_complex_parquet.struct_nested_view',
    'rs_complex_parquet.struct_t',
    'rs_complex_parquet.struct_t2',
    'rs_complex_parquet.struct_t3',
    'rs_complex_parquet.struct_t_id',
    'rs_complex_parquet.struct_t_s1',
    'rs_complex_parquet.struct_t_view',
    'rs_complex_parquet.struct_t_view2',
    #'rs_complex_parquet.spark_all_mixed_compression',
    #'rs_complex_parquet.spark_gzip',
    #'rs_complex_parquet.spark_snappy',
    #'rs_complex_parquet.spark_snappy_part',
    #'rs_complex_parquet.spark_uncompressed',
    #'rs_complex_parquet.spark_uncompressed_legacy_format',
    'customer.zd277_complex',
    'rs_json_format.complex_c1_case_sensitive',
    'rs_json_format.complex_c1_usecase',
    'rs_json_format.complex_nike_usecase',
    'rs_json_format.json_array_struct',
    'rs_json_format.json_arrays_test',
    'rs_json_format.json_inferred',
    'rs_json_format.json_primitives',
    'rs_json_format.json_primitives_inferred',
    'rs_json_format.json_struct',
    'rs_json_format.json_struct_array',
    'rs_json_format.json_struct_nested',
    'rs_json_format.primitives_with_array',
])

def test_view_full_unnest(unnest_dataset):
    print("Testing: " + unnest_dataset)
    ctx = common.get_test_context()
    db = 'unnest_test_db'

    def contains(col, attrs):
        if col not in attrs:
            return False
        return '%s.a1' % db in attrs[col]

    with common.get_planner(ctx) as conn:
        conn.execute_ddl("drop attribute if exists %s.a1" % db)
        conn.execute_ddl("create attribute %s.a1" % db)

        parts = unnest_dataset.split('.')
        unnest_scan = get_scan_as_json(conn, 'select ** from %s' % unnest_dataset)

        # Run a few iterations
        for _ in range(0, 3):
            # Add an attribute to a random leaf col
            base_path, flattened = common.TestBase.get_random_leaf_column(
                conn, parts[0], parts[1])
            print("Assigning tag to %s --> %s " % (base_path, flattened))
            conn.assign_attribute(db, 'a1', parts[0], parts[1], base_path)
            attrs_by_col = common.TestBase.collect_column_attributes(
                conn.list_datasets(parts[0], name=parts[1])[0])
            print(conn.execute_ddl_table_output('describe %s' % unnest_dataset))
            assert contains(unnest_dataset + '.' + base_path, attrs_by_col)

            # Create a view and make sure the scans are the same
            conn.execute_ddl("CREATE DATABASE IF NOT EXISTS %s" % db)
            conn.execute_ddl("DROP VIEW IF EXISTS %s.v" % db)
            conn.execute_ddl("CREATE VIEW %s.v AS SELECT ** from %s" %
                             (db, unnest_dataset))
            view_scan = get_scan_as_json(conn, 'select * from %s.v' % db)
            assert format(unnest_scan) == format(view_scan)

            # Verify tag inheritance
            print(conn.execute_ddl_table_output('describe %s.v' % db))
            attrs_by_col = common.TestBase.collect_column_attributes(
                conn.list_datasets(db, name='v')[0])
            assert contains(db + '.v.' + flattened, attrs_by_col)

            # Unassign the tag from the base table, should also be removed from view
            conn.unassign_attribute(db, 'a1', parts[0], parts[1], base_path, cascade=True)
            attrs_by_col = common.TestBase.collect_column_attributes(
                conn.list_datasets(parts[0], name=parts[1])[0])
            print(attrs_by_col)
            assert not contains(unnest_dataset + '.' + base_path, attrs_by_col)

            attrs_by_col = common.TestBase.collect_column_attributes(
                conn.list_datasets(db, name='v')[0])
            print(attrs_by_col)
            assert not contains(db + '.v.' + flattened, attrs_by_col)

# pylint: disable=line-too-long
def test_complex_json_format():
    assert_scan_output(
        'select * from rs_json_format.gharch_test_data where id = \'1201654257\'',
        [{'actor':
            {'avatar_url':
            b'https://secure.gravatar.com/avatar/1641c0f988b844f44de596fcef3adc62?d=http://github.dev%2Fimages%2Fgravatars%2Fgravatar-user-420.png',
            'gravatar_id': b'1641c0f988b844f44de596fcef3adc62',
            'id': 75915,
            'url': b'https://api.github.dev/users/mitechie',
            'login': b'mitechie'},
            'id': b'1201654257',
            'public': True,
            'payload': {
                'actor': b'mitechie', 'size': 1,
                'head': b'4d1085635d642ba60071341dd46d38216bff1313', 'push_id': 27295992,
                'actor_gravatar': b'1641c0f988b844f44de596fcef3adc62',
                'ref': b'refs/heads/develop',
                'shas':
                    [[
                        b'4d1085635d642ba60071341dd46d38216bff1313',
                        b'86d2a548fee49abc43bd1c251300d7089748195b@mitechie.com',
                        b'Garden it up',
                        b'Richard Harding'
                    ]],
                'repo': b'mitechie/Bookie'
            },
            'type': b'PushEvent',
            'repo':
                {'id': 1176073,
                'url': b'https://api.github.dev/repos/mitechie/Bookie',
                'name': b'mitechie/Bookie'},
            'created_at': '2011-03-23 00:06:16.000'
        }]
    )
# pylint: enable=bad-continuation
# pylint: enable=line-too-long
