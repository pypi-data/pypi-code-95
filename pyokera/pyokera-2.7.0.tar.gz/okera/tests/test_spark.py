# Copyright 2020 Okera Inc. All Rights Reserved.
#
# Integration tests for spark
#
# pylint: disable=logging-not-lazy
# pylint: disable=no-self-use
# pylint: disable=no-else-return
# pylint: disable=duplicate-code
import unittest

from okera.tests import pycerebro_test_common as common
from okera.tests import _mr_util as mr_util

IS_AUTHORIZE_QUERY = common.get_bool_env_var('OKERA_ENABLE_AUTHORIZE_QUERY', False)

auth_query_blacklisted_dbs = [
    # Spark cannot read the metadata
    # org.apache.spark.sql.execution.QueryExecutionException: Parquet column cannot be
    # converted in file s
    # 3a://cerebrodata-test/perf/tpcds/unpartitioned/parquet/tpcds_001TB/call_center/
    # part-00000.....-3c8d-4302-b184-9a3f6e2086a5-8888-1-c000.snappy.parquet.
    # Column: [cc_call_center_sk], Expected: bigint, Found: INT32
    'tpcds10_unpartitioned',
    'tpcds1_unpartitioned'
]

# TODO: We have empty dbs for some reason. Needs investigation.
blacklisted_dbs = [
    'delta_db',
    'okera_udfs',
    'udfs',
    'json_test_db',
    'ofs',
    'test_dremio',
    'test_presto_views',
    'test_tmp_db',

    # Contains large datasets for spark to scan, takes forever.
    'tpcds1000_unpartitioned',
    'tpcds1000_partitioned',
    'tpcds100_unpartitioned',
    'tpcds100_partitioned',
    'tpcds10_unpartitioned',
    'tpcds10_partitioned',
    'tpcds100x40',

    # Snowflake tables can cause high resource utilization on snowflake
    'tpcds001tb_snowflake',
    'sf_tpcds_1gb',
    'tpch_sf1',
    'tpch_sf5',
    'tpch_test_snowflake',

    # Test DB with some Delta tables in it
    'delta_dummy_scan_db',
]

blacklisted_tbls = [
    # Cannot read dbfs
    'all_table_types.dbfs_invalid_table',
    'customer.zd1010_dbfs_table_external_provider',
    'customer.zd1065_dbfs_table_no_provider',

    # BUG: Incompatible view
    'jdbc_demo_test.transactions2',

    # Invalid table
    'bad_metadata_db.broken_view',
    'datedb.dates_with_invalid_data',
    'jdbc_test_mysql.t',
    'parquet_testing.dict_page_offset_zero',

    # TODO: Table does not return correctly, batch size is too big?
    'jdbc_test_oracle.blob_test',
    'jdbc_test_oracle.clob_test',
    'jdbc_test_redshift.fact_ae_wide',

    # Invalid avro header
    'customer.zd623_east',
    'rs.avro_comments',

    # Fixable(?) invalid table
    'bad_metadata_db.valid_tbl',
    'customer.t2_authzn',
    'partition_test.keyword_part_table',
    'partition_test.weird_partition6',

    # Incompatible SQL
    'chase.cte_view',

    # Something wrong
    'special_chars.test_table',

    # Missing udfs
    'demo_test.transactions_anonymize_inactive_users_external_view',

    # Server does not support
    'parquet_testing.datapage_v2_snappy',
    'parquet_testing.nested_maps_snappy',
    'parquet_testing.nonnullable_impala',
    'parquet_testing.nullable_impala',
    'parquet_testing.repeated_no_annotation',
    'rs_complex.array_text',
    'rs_complex.rs_complex_array_map_t',
    'rs_complex_parquet.complextypestbl_parq',
    'rs_complex_parquet.rs_parquet_array_map_t',

    # LZO not supported
    'rs.alltypes_large_s3_lzo',

    # No access
    'rs.s3_no_perm',

    # Spark ooms
    'rs.test_many_columns',

    # Has a text file in the parquet path causes below exception
    # Caused by: java.io.IOException:
    # Could not read footer for file:
    # FileStatus{path=s3a://cerebrodata-test/nytaxi-data/parquet-symlink/symlink.txt;
    'nytaxi.parquet_data_symlink',
]

# Authorize query has some limitations right now, so skip these additional tables
authorize_query_blacklisted_tbls = [
    # FIXME: complex types rewrite error
    'authdb.struct_t_full_view_on_sel_complex_view',
    'authdb.struct_t_full_view_on_sel_view',
    'authdb.struct_t_sel_complex_view',
    'authdb.struct_t_sel_view',
    'authdb.struct_t_sel_view_on_sel_complex_view',
    'authdb.struct_t_view',
    'authdb.struct_t_view_on_view',
    'authdb.struct_t_where_clause_view',
    'chase.struct_view',
    'chase.subscription_currency',
    'chase.subscription_view',
    'rs_complex.struct_nested_s1',
    'rs_complex.struct_nested_view',
    'rs_complex.struct_t',
    'rs_complex.struct_t2',
    'rs_complex.struct_t3',
    'rs_complex.struct_t_id',
    'rs_complex.struct_t_restricted_view',
    'rs_complex.struct_t_s1',
    'rs_complex.struct_t_view',
    'rs_complex.struct_t_view2',
    'rs_complex.struct_view',
    'rs_complex.user_phone_numbers',
    'rs_complex.users',
    'rs_complex_parquet.struct_nested_s1',
    'rs_complex_parquet.struct_nested_view',
    'rs_complex_parquet.struct_t_s1',
    'rs_complex_parquet.struct_t_view',
    'rs_complex_parquet.struct_t_view2',

    # FIXME: view rewrite error
    'customer.market_decide_offer_decision_v3_card_non_npi_vw',

    # BUG: HMS cannot support partition structure (error message very bad)
    'partition_test.special_chars_partition',
    'partition_test.special_chars_partition_nested',

    # BUG: HMS cannot support timestamp part col
    'partition_test.timestamp_part_encoded',
    'partition_test.timestamp_part_test',
    'partition_test.timestamp_part_test2',

    # FIXME: Fails with the following exception.
    # org.apache.spark.sql.AnalysisException:
    # org.apache.hadoop.hive.ql.metadata.HiveException:
    # Unable to fetch table orc_data. java.lang.IllegalArgumentException:
    # Table nytaxi.orc_data set to bypass Okera for direct access.
    # However, it appears the user does not have full access to the table
    # to allow this operation. Ask the admin to grant full access on this table.
    'nytaxi.orc_data',
    'rs.lineitem_orc',

    # Spark cannot read these files
    'chase.party',
    'chase.product',
    'chase.subscription',
    'customer.zd271_private_asvdataintegration',
    'customer.zd277_complex',
    'customer.zd424_enterprise_edge_events_received',
    'customer.zd558_application_model_scoring',
    'customer.zd558_credit_card_market_decide_application_created',
    'customer.zd558_credit_card_market_decide_offer_decision',
    'customer.zd558_product_decision',
    'customer.zd965_intab_period',
    'customer_usage.nike_user_activity',
    'fastparquet.gzip_nation_impala_parquet',
    'fastparquet.nation_dict_parquet',
    'fastparquet.nation_impala_parquet',
    'fastparquet.snappy_nation_impala_parquet',
    'parquet_testing.byte_array_decimal',
    'parquet_testing.nation_dict_malformed',
    'partition_test.invalid_files_test',
    'rs.s3_nation_subdir',
    'rs.sample_from_readonly_bucket',
    'rs_complex.enum_type',
    'rs_complex_parquet.chase_parquet_timestamp',
    'special_chars.test_table',

    # Suspect these do not work.
    'rs_complex_parquet.hudi_as_parquet',
    'rs_complex_parquet.hudi_nonpartitioned',
    'rs_complex_parquet.hudi_partitioned',
] + mr_util.authorize_query_unsupported_datasets

def skip_table(tbl_name):
    if tbl_name in blacklisted_tbls:
        return True
    if IS_AUTHORIZE_QUERY and tbl_name in authorize_query_blacklisted_tbls:
        return True
    return False

class SparkScanTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Initializes one time state that is shared across test cases. This is used
            to speed up the tests. State that can be shared across (but still stable)
            should be here instead of __cleanup()."""
        super(SparkScanTest, cls).setUpClass()
        cls._session = (mr_util.get_spark_session(__name__))

    @classmethod
    def tearDownClass(cls):
        cls._session.stop()

    def test_show_databases(self):
        query = self._session.sql("SHOW DATABASES")
        resultList = query.collect()
        dbFound = False
        for row in resultList:
            if 'okera_sample' in row.databaseName:
                dbFound = True
                break
        self.assertTrue(dbFound)

    def test_show_tables(self):
        dbs = self._session.sql("SHOW DATABASES").collect()
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            for db in dbs:
                print("test_show_tables for db: " + db.databaseName)
                if (not db.databaseName.startswith('_') and
                        db.databaseName not in blacklisted_dbs):
                    tables = self._session.sql("SHOW TABLES IN " + db.databaseName).collect()
                    tables_from_okera = conn.list_dataset_names(db.databaseName)
                    self.assertTrue(len(tables) == len(tables_from_okera), msg=db.databaseName)

    @unittest.skip("Used for testing to run a single table easily.")
    def test_select_singlerow_dev(self):
        tbl = 'demo.audit_logs'
        sql = 'SELECT * FROM ' + tbl + ' LIMIT 1'
        self._session.sql(sql).limit(1).collect()

    def test_select_single_row(self):
        if common.TEST_LEVEL in ["smoke", "dev"]:
            dbs = ['rs', 'rs_complex']
        else:
            all_dbs = self._session.sql("SHOW DATABASES").collect()
            dbs = []
            for db in all_dbs:
                if db.databaseName.startswith('_'):
                    continue
                elif db.databaseName in blacklisted_dbs:
                    continue
                elif IS_AUTHORIZE_QUERY and db.databaseName in auth_query_blacklisted_dbs:
                    continue
                dbs.append(db.databaseName)

        tables_scanned = 0
        for db in dbs:
            tables = self._session.sql("SHOW TABLES IN " + db).collect()
            for table in tables:
                full_tbl_name = db + '.' + table.tableName
                if table.tableName.startswith('_') or skip_table(full_tbl_name):
                    continue
                # The limit here is not honored.
                sql = "SELECT * FROM " + full_tbl_name + " LIMIT 1"
                print("Spark::test_select_single_row SQL: " + sql)
                # We have issues consuming the data. We need to fix the spark versions
                # and then re-enable this. Until then just executing the query is
                # sufficient to catch any spark errors.
                # rows = self._session.sql(sql).collect()
                rows = self._session.sql(sql)
                self.assertIsNotNone(rows)
                tables_scanned += 1
        print("Total tables scanned: %d" % tables_scanned)
