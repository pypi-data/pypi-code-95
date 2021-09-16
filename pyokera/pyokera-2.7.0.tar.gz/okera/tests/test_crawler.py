# Copyright 2019 Okera Inc. All Rights Reserved.
#
# Some integration tests against the crawler

# pylint: disable=broad-except,line-too-long,too-many-public-methods
import os
import time
import unittest
from collections import namedtuple
import pytest
from okera import _thrift_api
from okera.tests import pycerebro_test_common as common

TEST_USER = "testcrawleruser"
TEST_USER2 = "testcrawleruser2"
TEST_ROLE = "test_crawler_role"
TEST_ROLE2 = "test_crawler_role2"

CRAWLER_STATUS_KEY = 'okera.crawler.status'
CRAWLER_DATA_FILE_PATH_KEY = 'okera.crawler.data_file_path'

"""
This function determines which cloud providers are currently
supported in the running test cluster.  It is not properly wired
to detect platform support, so this needs to be tweaked manually.

To run this test suite with Azure support, start cdas with:
    start-cdas -load-test-data-minimal -autotagger -azure
To run this with AWS support, start cdas with:
    start-cdas -load-test-data-minimal -autotagger

Execute the UTs with:
    cd $OKERA_HOME/client/pycerebro
    export CRAWLER_TEST_MODES="S3,ADLS,ABFS,AUTOTAGGER"
    pytest okera/tests/test_crawler.py
"""
# TODO: We need cleanup handling here. We should attempt to delete previous crawlers
# before starting the next one. Related ticket: DAS-3831

MAX_WAIT_SEC = 60 if os.environ.get('CONTAINERIZED', 'false') == 'true' else 25

CRAWLER_TEST_MODES = os.environ.get('CRAWLER_TEST_MODES', 'S3')

FIELDS = ['provider', 'name', 'root_path', 'found_tables', 'timeout']
CrawlerTest = namedtuple("CrawlerTest", FIELDS)
Privilege = namedtuple("Privilege", ['level', 'can_select', 'can_drop', 'can_alter'])

PRIV_ALL = Privilege('ALL', True, True, True)
PRIV_SHOW = Privilege('SHOW', False, False, False)
PRIV_SELECT = Privilege('SELECT', True, False, False)
PRIV_DROP = Privilege('DROP', False, True, False)
PRIV_ALTER = Privilege('ALTER', False, False, True)

@pytest.mark.skip(reason="Currently broken and fix being tracked by DAS-5760")
class CrawlerIntegrationTest(unittest.TestCase):
    def _wait_for_crawler(self, conn, crawler_db, dataset=None, max_sec=MAX_WAIT_SEC):
        """ Waits for the crawler to find dataset for this crawler
            If dataset is None, then just wait for the crawler to report COMPLETED.
        """
        sleep_time = 1
        if max_sec > 60:
            sleep_time = 3
        if max_sec > 120:
            sleep_time = 5

        elapsed_sec = 0
        datasets = None
        while elapsed_sec < max_sec:
            time.sleep(sleep_time)
            elapsed_sec += sleep_time
            if dataset:
                datasets = conn.list_dataset_names(crawler_db)
                if (crawler_db + '.' + dataset) in datasets:
                    return datasets
            else:
                params = conn.execute_ddl('DESCRIBE DATABASE %s' % crawler_db)
                for p in params:
                    if p[0] == CRAWLER_STATUS_KEY and p[1] == 'COMPLETED':
                        return conn.list_dataset_names(crawler_db)
        if not datasets:
            datasets = conn.list_dataset_names(crawler_db)
        print("Found datasets: " + str(datasets))
        self.fail('Crawler did not find dataset in time.')

    def create_crawler_and_verify(self, user, crawler, root_path, found_tables, max_sec=25):
        crawler_db = '_okera_crawler_' + crawler
        ctx = common.get_test_context()

        with common.get_planner(ctx) as conn:
            # Always drop the crawler as admin
            ctx.disable_auth()
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)

            if user is not None:
                ctx.enable_token_auth(token_str=user)

            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, root_path))
            for table in found_tables:
                print("Waiting on table: %s" % table)
                self._wait_for_crawler(conn, crawler_db, table, max_sec)

    def run_crawler_test(self, user=None, config=None):
        if not config:
            return
        if config.provider in CRAWLER_TEST_MODES:
            self.create_crawler_and_verify(user,
                                           config.name,
                                           config.root_path,
                                           config.found_tables,
                                           config.timeout)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_basic(self):
        tests = [
            CrawlerTest(provider='S3',
                        name='integration_test',
                        root_path='s3://cerebrodata-test/tpch-nation-integration-test/',
                        found_tables=['tpch_nation_integration_test'],
                        timeout=25),
            CrawlerTest(provider='ADLS',
                        name='integration_test',
                        root_path='adl://okeratestdata.azuredatalakestore.net/cerebrodata-test/tpch-nation-integration-test/',
                        found_tables=['tpch_nation_integration_test'],
                        timeout=25),
            CrawlerTest(provider='ABFS',
                        name='integration_test',
                        root_path='abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/tpch-nation-integration-test/',
                        found_tables=['tpch_nation_integration_test'],
                        timeout=25)
                ]
        for test in tests:
            self.run_crawler_test(test)

    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_not_slow_5k(self):
        # This table has 5K partitions, make sure it finishes reasonably quickly
        tests = [
            CrawlerTest(provider='S3',
                        name='integration_test',
                        root_path='s3://cerebrodata-test/part_flat_5000_data_100/',
                        found_tables=['part_flat_5000_data_100'],
                        timeout=10)
                ]
        for test in tests:
            self.run_crawler_test(test)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_flat(self):
        tests = [
            CrawlerTest(provider='S3',
                        name='integration_test',
                        root_path='s3://cerebrodata-test/crawler_flat_structure/',
                        found_tables=['atp_csv', 'topbabynamesbystate_csv'],
                        timeout=25),
            CrawlerTest(provider='ADLS',
                        name='integration_test',
                        root_path='adl://okeratestdata.azuredatalakestore.net/cerebrodata-test/crawler_flat_structure/',
                        found_tables=['atp_csv', 'topbabynamesbystate_csv'],
                        timeout=25),
            CrawlerTest(provider='ABFS',
                        name='integration_test',
                        root_path='abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/crawler_flat_structure/',
                        found_tables=['atp_csv', 'topbabynamesbystate_csv'],
                        timeout=25)
                ]
        for test in tests:
            if test.provider not in CRAWLER_TEST_MODES:
                continue
            crawler_db = '_okera_crawler_' + test.name
            ctx = common.get_test_context()
            with common.get_planner(ctx) as conn:
                conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
                conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (test.name, test.root_path))

                # This should only find one dataset since flat structures is not the default
                self._wait_for_crawler(conn, crawler_db, None)
                datasets = conn.list_dataset_names(crawler_db)
                self.assertEqual(len(datasets), 1)
                conn.execute_ddl('DROP TABLE %s.%s' % (crawler_db, 'crawler_flat_structure'))

                # Configure this crawler to accept flat structures
                conn.execute_ddl("ALTER DATABASE %s SET DBPROPERTIES('%s'='%s')" %\
                    (crawler_db, 'okera.crawler.single_file_datasets', 'true'))
                conn.execute_ddl("ALTER DATABASE %s SET DBPROPERTIES('%s'='%s')" %\
                    (crawler_db, CRAWLER_STATUS_KEY, ''))

                # Crawler should have been retriggered, wait for it, it should now find
                # both datasets
                for table in test.found_tables:
                    self._wait_for_crawler(conn, crawler_db, table)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_empty(self):
        crawler = 'test_empty'
        crawler_db = '_okera_crawler_' + crawler
        if 'S3' in CRAWLER_TEST_MODES:
            location = 's3://cerebrodata-test/empty/'
        elif 'ADLS' in CRAWLER_TEST_MODES:
            location = ('adl://okeratestdata.azuredatalakestore.net/' +
                        'cerebrodata-test/empty_folder/')
        elif 'ABFS' in CRAWLER_TEST_MODES:
            location = ('abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/' +
                        'empty_folder/')
        else:
            self.fail('Test received invalid testType: ' + CRAWLER_TEST_MODES)
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None)

        if contents:
            self.fail('Directory was not empty, location : ' + location)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_hidden_file(self):
        crawler = 'test_hidden_file'
        crawler_db = '_okera_crawler_' + crawler
        if 'S3' in CRAWLER_TEST_MODES:
            location = 's3://cerebrodata-test/hidden_files_only/'
        elif 'ADLS' in CRAWLER_TEST_MODES:
            location = ('adl://okeratestdata.azuredatalakestore.net/' +
                        'cerebrodata-test/hidden_file/')
        elif 'ABFS' in CRAWLER_TEST_MODES:
            location = ('abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/' +
                        'hidden_files_only/')
        else:
            self.fail('Test received invalid testType: ' + CRAWLER_TEST_MODES)
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None)

        if contents:
            self.fail('Directory was not empty or hidden file found, location : '
                      + location)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_bad_path_good_scheme(self):
        caught = None
        crawler = 'test_bad_path_good_scheme'
        crawler_db = '_okera_crawler_' + crawler
        bucket = 'thispathdoesnotexistcerebro'
        if 'S3' in CRAWLER_TEST_MODES:
            location = ('s3://%s/' % bucket)
        elif 'ADLS' in CRAWLER_TEST_MODES:
            location = ('adl://%s.azuredatalakestore.net/'% bucket)
        elif 'ABFS' in CRAWLER_TEST_MODES:
            location = 'abfs://%s@okeratestdata.dfs.core.windows.net/' % bucket
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            try:
                conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
                conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            except Exception as e:
                if "is not accessible" not in str(e) and "does not exist" not in str(e):
                    self.fail("Exception did not match expected. Ex encountered: "
                              + str(e))
                else:
                    caught = True
            if(not caught):
                self.fail("No exception raised, expected TRecordServiceException")

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_null_path(self):
        crawler = 'test_null_path'
        caught = None
        crawler_db = '_okera_crawler' + crawler
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            try:
                conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, None))
            except Exception as e:
                if "Source path not valid" not in str(e):
                    self.fail("Exception did not match expected. Ex encountered: "
                              + str(e))
                else:
                    caught = True

            if not caught:
                self.fail("No exception raised, expected TRecordServiceException")

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_bad_scheme(self):
        caught = None
        crawler = 'test_bad_scheme'
        crawler_db = '_okera_crawler' + crawler
        location = 'foo://bucket/path'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            try:
                conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            except Exception as e:
                if "Crawlers are not supported for this storage system" not in str(e):
                    self.fail("Exception did not match expected. Ex encountered: "
                              + str(e))
                else:
                    caught = True
            if not caught:
                self.fail("No exception raised, expected TRecordServiceException")

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_no_scheme(self):
        caught = None
        crawler = 'test_no_scheme'
        crawler_db = '_okera_crawler' + crawler
        location = 'bucket/path'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            try:
                conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            except Exception as e:
                if "Please verify the URL is correct:" not in str(e):
                    self.fail("Exception did not match expected. Ex encountered: "
                              + str(e))
                else:
                    caught = True
            if not caught:
                self.fail("No exception raised, expected TRecordServiceException")

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_crawl_partitioned(self):
        crawler = 'test_crawl_partitioned'
        crawler_db = '_okera_crawler_' + crawler
        if 'S3' in CRAWLER_TEST_MODES:
            location = 's3://cerebrodata-test/partitions-test2/'
        elif 'ADLS' in CRAWLER_TEST_MODES:
            location = ('adl://okeratestdata.azuredatalakestore.net/' +
                        'cerebrodata-test/partitions-test/')
        elif 'ABFS' in CRAWLER_TEST_MODES:
            location = ('abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/' +
                        'partitions-test2/')
        else:
            self.fail('Test received invalid testType: ' + CRAWLER_TEST_MODES)
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None, 30)

        if len(contents) != 2:
            self.fail("Did not find 2 datasets at location: " + location)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_crawl_already_registered(self, testType=None):
        crawler = 'test_crawl_already_registered'
        crawler_db = '_okera_crawler_' + crawler
        if 'S3' in CRAWLER_TEST_MODES:
            location = 's3://cerebrodata-test/tpch_nation/'
        elif 'ADLS' in CRAWLER_TEST_MODES:
            location = ('adl://okeratestdata.azuredatalakestore.net/'
                        'cerebrodata-test/tpch_nation/')
        elif 'ABFS' in CRAWLER_TEST_MODES:
            location = ('abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/' +
                        'tpch_nation/')
        else:
            self.fail('Test received invalid testType: ' + testType)
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            if 'S3' in CRAWLER_TEST_MODES:
                conn.execute_ddl("CREATE EXTERNAL TABLE IF NOT EXISTS"
                                 "`default`.`tpch_nation_s3`(s smallint"
                                 ", n string, t smallint, d string) LOCATION '%s'"
                                 % location)
            elif 'ADLS' in CRAWLER_TEST_MODES:
                conn.execute_ddl("CREATE EXTERNAL TABLE IF NOT EXISTS"
                                 "`default`.`tpch_nation_adls`(s smallint"
                                 ", n string, t smallint, d string) LOCATION '%s'"
                                 % location)
            elif 'ABFS' in CRAWLER_TEST_MODES:
                conn.execute_ddl("CREATE EXTERNAL TABLE IF NOT EXISTS"
                                 "`default`.`tpch_nation_abfs`(s smallint"
                                 ", n string, t smallint, d string) LOCATION '%s'"
                                 % location)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None)

        if contents:
            print(str(contents))
            self.fail("Found unregistered dataset when should have found none: " +
                      location)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_crawl_duplicate_paths(self):
        crawler1 = 'test_crawl_duplicate_paths_1'
        crawler1_db = '_okera_crawler_' + crawler1
        crawler2 = 'test_crawl_duplicate_paths_2'
        crawler2_db = '_okera_crawler_' + crawler2
        if 'S3' in CRAWLER_TEST_MODES:
            location = 's3://cerebrodata-test/alltypes-parquet/'
        elif 'ADLS' in CRAWLER_TEST_MODES:
            location = ('adl://okeratestdata.azuredatalakestore.net/'
                        'cerebrodata-test/alltypes-parquet/')
        elif 'ABFS' in CRAWLER_TEST_MODES:
            location = ('abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/' +
                        'alltypes-parquet/')
        else:
            self.fail('Test received invalid testType: ' + CRAWLER_TEST_MODES)
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler1_db)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler2_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler1, location))
            contents1 = self._wait_for_crawler(conn, crawler1_db, None)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler2, location))
            contents2 = self._wait_for_crawler(conn, crawler2_db, None)

            contents1 = [ds.split(".")[1] for ds in contents1]
            contents2 = [ds.split(".")[1] for ds in contents2]

        self.assertEqual(contents1, contents2)

    @staticmethod
    def __get_columns(dataset):
        cols = []
        partition_cols = []
        for c in dataset.schema.cols:
            if c.hidden:
                continue
            if c.is_partitioning_col:
                partition_cols.append(c.name)
            else:
                cols.append(c.name)
        return cols, partition_cols

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_data_partition_col_dup(self):
        # This dataset has the same column name in the partition path and data file.
        # We want to ignore the column in the data file.
        crawler = 'data_partition_col_dup_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebro-test-itay/lake4/partitioned2/'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Default crawler allows duplicates
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, 'partitioned2')
            dataset = conn.list_datasets(crawler_db, name='partitioned2')
            cols, partition_cols = self.__get_columns(dataset[0])
            self.assertTrue('str2' in cols)
            self.assertTrue('str2' in partition_cols)
            show = conn.execute_ddl(
                'show create table %s.%s' % (crawler_db, 'partitioned2'))[0][0]
            self.assertEqual(2, show.count('str2 STRING'), msg=show)

            # Configure this crawler to ignore duplicates
            conn.execute_ddl("DROP TABLE %s.%s" % (crawler_db, 'partitioned2'))
            conn.execute_ddl("ALTER DATABASE %s SET DBPROPERTIES('%s'='%s')" %\
                (crawler_db, 'okera.allow.partition_cols_in_data', 'true'))
            conn.execute_ddl("ALTER DATABASE %s SET DBPROPERTIES('%s'='%s')" %\
                (crawler_db, CRAWLER_STATUS_KEY, ''))
            self._wait_for_crawler(conn, crawler_db, 'partitioned2')
            dataset = conn.list_datasets(crawler_db, name='partitioned2')
            cols, partition_cols = self.__get_columns(dataset[0])

            # str2 should not be in cols now, only in partition cols
            self.assertTrue('str2' not in cols)
            self.assertTrue('str2' in partition_cols)
            show = conn.execute_ddl(
                'show create table %s.%s' % (crawler_db, 'partitioned2'))[0][0]
            self.assertEqual(1, show.count('str2 STRING'), msg=show)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_crawler_no_suffix(self):
        # Crawl a directory where the datasets don't have file suffixes and make
        # sure we can find them another way.
        crawler = 'no_suffix_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://okera-ui/autotagger/no-postfix'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db)

            dataset = conn.list_datasets(crawler_db, name='csv')[0]
            self.assertEqual("TEXT", dataset.table_format)
            dataset = conn.list_datasets(crawler_db, name='parquet')[0]
            self.assertEqual("PARQUET", dataset.table_format)
            dataset = conn.list_datasets(crawler_db, name='avro')[0]
            self.assertEqual("AVRO", dataset.table_format)
            dataset = conn.list_datasets(crawler_db, name='json')[0]
            self.assertEqual("JSON", dataset.table_format)

    # DAS-5753: Find out why this is causing failures in subsequent crawler tests
    @unittest.skipIf(True, "Skipping disabled test")
    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_crawler_opencsv(self):
        # Crawl a directory where the datasets don't have file suffixes and make
        # sure we can find them another way.
        crawler = 'nfl_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://okera-cust-success/nflstatistics/'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, 'basic_stats', max_sec=30)
            dataset = conn.list_datasets(crawler_db, name='basic_stats')[0]
            self.assertEqual(",", dataset.serde_metadata['separatorChar'])

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_crawler_tsv(self):
        # Crawl a directory where the datasets don't have file suffixes and make
        # sure we can find them another way.
        crawler = 'tsv_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebro-test-kevin/dea_pain_pills/'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db)

            dataset = conn.list_datasets(crawler_db, name='dea_pain_pills')[0]
            self.assertEqual("TEXT", dataset.table_format)
            self.assertEqual(42, len(dataset.schema.cols))

    # DAS-5753: fix and re-enable this test
    @unittest.skipIf(True, "Skipping disabled test.")
    @unittest.skipIf(common.TEST_LEVEL != "ci" and
                     common.TEST_LEVEL != "all", "Only running at CI/ALL level.")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_root_crawler(self):
        # Crawl the root test bucket, this can take a while.
        crawler = 'root_crawler_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebrodata-test/'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            # This takes ~330s on an ec2 dev box
            self._wait_for_crawler(conn, crawler_db, 'zookeeper', max_sec=600)
            datasets = conn.list_dataset_names(crawler_db)
            self.assertTrue(len(datasets) > 250, msg=str(datasets))

    @unittest.skipIf(common.TEST_LEVEL != "ci" and
                     common.TEST_LEVEL != "all", "Only running at CI/ALL level.")
    @unittest.skipIf(('ABFS' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_root_crawler_abfs(self):
        # Crawl the root test bucket, this can take a while.
        crawler = 'abfs_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 'abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, max_sec=600)
            datasets = conn.list_dataset_names(crawler_db)
            self.assertTrue(len(datasets) > 250, msg=str(datasets))

    @unittest.skipIf(common.TEST_LEVEL != "ci" and
                     common.TEST_LEVEL != "all", "Only running at CI/ALL level.")
    @unittest.skipIf(('ADLS' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_root_crawler_adls(self):
        # Crawl the root test bucket, this can take a while.
        crawler = 'adls_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 'adl://okeratestdata.azuredatalakestore.net/cerebrodata-test/'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, max_sec=600)
            datasets = conn.list_dataset_names(crawler_db)
            self.assertTrue(len(datasets) > 250, msg=str(datasets))


    # DAS-5753: fix and re-enable this test
    @unittest.skipIf(True, "Skipping disabled test.")
    @unittest.skipIf(common.TEST_LEVEL != "ci" and
                     common.TEST_LEVEL != "all", "Only running at CI/ALL level.")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_ui_crawler(self):
        # Crawl the ui test bucket, this can take a while.
        crawler = 'ui_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://okera-ui/'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, max_sec=300)
            datasets = conn.list_dataset_names(crawler_db)
            self.assertTrue(len(datasets) > 80)


    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    @unittest.skipIf(True, "Skipping as the backend broke this test - it cannot pass")
    def test_okera_lite(self):
        # This crawler is special and registers the tables in another DB based on
        # the path.
        crawler = 'okera_lite'
        result_db = 'okera_lite_default'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebrodata-test/tpch-nation/'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % result_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, None)
            contents = conn.list_dataset_names(result_db)
            self.assertTrue('okera_lite_default.tpch_nation' in contents,
                            msg=str(contents))

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_das_3489(self):
        crawler = 'das_3489_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebrodata-test/put-test2/'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, max_sec=300)
            dataset = conn.list_datasets(crawler_db, name='put_test2')[0]
            self.assertEqual("TEXT", dataset.table_format)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_empty_json(self):
        # This is an empty json file. We should not register it
        crawler = 'json_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebro-datasets/empty-json/empty.json'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, max_sec=10)
            self.assertEqual(len(conn.list_datasets(crawler_db)), 0)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_text_boolean(self):
        # Test case for a cedilla delimited file
        crawler = 'text_boolean_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://okera-demo/consent-management/whitelist'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, max_sec=10)
            dataset = conn.list_datasets(crawler_db, name='whitelist')[0]
            self.assertEqual(3, len(dataset.schema.cols))
            self.assertEqual(
                _thrift_api.TTypeId.STRING,
                dataset.schema.cols[0].type.type_id)
            self.assertEqual(
                _thrift_api.TTypeId.BOOLEAN,
                dataset.schema.cols[1].type.type_id)
            self.assertEqual(
                _thrift_api.TTypeId.BOOLEAN,
                dataset.schema.cols[2].type.type_id)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_cedilla_delimiter(self):
        # Test case for a cedilla delimited file
        crawler = 'cedilla_delimiter_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebro-datasets/cedilla_sample/'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, max_sec=10)
            dataset = conn.list_datasets(crawler_db, name='cedilla_sample')[0]
            self.assertEqual(2, len(dataset.schema.cols))

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    def test_comments(self):
        crawler = 'comments_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebrodata-test/crawler-schema-comments/'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db)

            # This should have comments from the data file
            whitelist = conn.list_datasets(crawler_db, name='avro_whitelist')[0]
            self.assertTrue('This dataset stores' in whitelist.description,
                            msg=str(whitelist))
            whitelist_col = whitelist.schema.cols[1]
            self.assertTrue('Indicates if the user' in whitelist_col.comment,
                            msg=str(whitelist_col))

            # This should have default comments
            default_comments = conn.list_datasets(crawler_db, name='avro_no_comments')[0]
            self.assertTrue('Discovered by Okera crawler' in default_comments.description,
                            msg=str(default_comments))
            default_comments_col = default_comments.schema.cols[1]
            self.assertTrue(default_comments_col.comment is None)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    @unittest.skipIf(('S3' not in CRAWLER_TEST_MODES),
                     "Skipping UT because platform not set in CRAWLER_TEST_MODES")
    @unittest.skipIf(('AUTOTAGGER' not in CRAWLER_TEST_MODES),
                     "Skipping UT because Autotagger not set in CRAWLER_TEST_MODES")
    def test_autotagger(self):
        crawler = 'autotagger_test'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://okera-datalake/gdpr-avro/transactions/'
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            # Run it a few times to make sure dropping table and assigning existing
            # tags works.
            for _ in range(3):
                conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
                conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
                self._wait_for_crawler(conn, crawler_db)

                # This should have comments from the data file
                transactions = conn.list_datasets(crawler_db, name='transactions')[0]
                self.assertTrue('This dataset stores' in transactions.description,
                                msg=str(transactions))

                # This column should be tagged
                ccn = transactions.schema.cols[5]
                self.assertTrue(ccn.attribute_values is not None)
                self.assertEqual('credit_card_number',
                                 ccn.attribute_values[0].attribute.key)
                self.assertTrue('credit card number' in ccn.comment,
                                msg=str(ccn))

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_crawl_ordering(self):
        crawler = 'test_crawl_ordering'
        crawler_db = '_okera_crawler_' + crawler
        if 'S3' in CRAWLER_TEST_MODES:
            location = 's3://cerebrodata-test/partitioned_flat_50000/'
        elif 'ADLS' in CRAWLER_TEST_MODES:
            location = ('adl://okeratestdata.azuredatalakestore.net/' +
                        'cerebrodata-test/partitioned_flat_50000/')
        elif 'ABFS' in CRAWLER_TEST_MODES:
            location = ('abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/' +
                        'partitioned_flat_50000/')
        else:
            self.fail('Test received invalid testType: ' + CRAWLER_TEST_MODES)
        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None, 30)

            self.assertEqual(
                contents,
                ['_okera_crawler_test_crawl_ordering.partitioned_flat_50000'])
            dataset = conn.list_datasets(crawler_db, name='partitioned_flat_50000')[0]
            datafile_path = dataset.metadata[CRAWLER_DATA_FILE_PATH_KEY]
            self.assertEqual(
                datafile_path,
                's3a://cerebrodata-test/partitioned_flat_50000/part=9999/data_0.csv')

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_crawl_dup_names(self):
        crawler = 'test_crawl_dup_names'
        crawler_db = '_okera_crawler_' + crawler
        base_loc = "cerebrodata-test/crawler_dupe_names/"
        if 'S3' in CRAWLER_TEST_MODES:
            location = "s3://" + base_loc
        elif 'ADLS' in CRAWLER_TEST_MODES:
            location = "adl://okeratestdata.azuredatalakestore.net/" + base_loc
        elif 'ABFS' in CRAWLER_TEST_MODES:
            location = ("abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/" +
                        base_loc)
        else:
            self.fail("Test received invalid testType: " + CRAWLER_TEST_MODES)

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None, 30)

            self.assertIn('_okera_crawler_test_crawl_dup_names.transactions_1', contents)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_das_4807(self):
        # This test verifies that we are picking up the latest file in the folder which
        # contains data with quotes, which should produce a different result in the
        # crawled table. This may not be robust as this is a "real" dataset that gets
        # data added to it. If this because they problem, we should create a directory
        # with 2 test files, the older with no quotes and the newer with quotes.
        crawler = 'test_crawl_health'
        crawler_db = '_okera_crawler_' + crawler
        location = 's3://cerebro-test-kevin/covid_19_daily'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            contents = self._wait_for_crawler(conn, crawler_db, None, 30)
            self.assertIn('_okera_crawler_test_crawl_health.covid_19_daily', contents)
            dataset = conn.list_datasets(crawler_db, name='covid_19_daily')[0]
            self.assertEqual(
                "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe", dataset.serialization_lib)

    @unittest.skipIf(common.TEST_LEVEL in ["smoke", "dev"], "Skipping at unit test level")
    def test_col_name_too_long(self):
        crawler = 'test_crawl_long_col_name'
        crawler_db = '_okera_crawler_' + crawler
        if 'S3' in CRAWLER_TEST_MODES:
            location = 's3://cerebrodata-test/long-col-names/'
        elif 'ADLS' in CRAWLER_TEST_MODES:
            location = ('adl://okeratestdata.azuredatalakestore.net/'
                        'cerebrodata-test/long-col-names/')
        elif 'ABFS' in CRAWLER_TEST_MODES:
            location = ('abfs://cerebrodata-test@okeratestdata.dfs.core.windows.net/' +
                        'long-col-names/')
        else:
            self.fail('Test received invalid testType: ' + CRAWLER_TEST_MODES)

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, max_sec=10)
            self.assertEqual(len(conn.list_datasets(crawler_db)), 0)

    def test_skip_crawl_when_column_name_contain_invalid_chars(self):
        crawler = 'test_crawl_col_name_with_dot'
        crawler_db = '_okera_crawler_' + crawler
        # this bucket contains two datasets, one of which contains
        # column names with 'dot' in it.
        location = 's3://cerebro-customers/chase/zd1475'

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:
            conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % crawler_db)
            conn.execute_ddl("CREATE CRAWLER %s SOURCE '%s'" % (crawler, location))
            self._wait_for_crawler(conn, crawler_db, max_sec=10)
            # only one dataset should be found by the crawler
            # and call should succeed
            self.assertEqual(len(conn.list_datasets(crawler_db)), 1)

    def test_crawler_privileges(self):
        s3_uri = 's3://cerebrodata-test/tpch-nation-integration-test/'
        crawler_name = 'integration_test'
        table_name = 'tpch_nation_integration_test'
        as_owner_role = "_okera_internal_role_%s" % (TEST_USER)

        ctx = common.get_test_context()
        with common.get_planner(ctx) as conn:

            for priv in [PRIV_ALL, PRIV_SHOW, PRIV_SELECT, PRIV_DROP, PRIV_ALTER]:
                ctx.disable_auth()
                setup_ddls = [
                    # Setup create role
                    "DROP ROLE IF EXISTS %s" % (TEST_ROLE),
                    "CREATE ROLE %s" % (TEST_ROLE),
                    "GRANT ROLE %s TO GROUP %s" % (TEST_ROLE, TEST_USER),

                    # Setup use role
                    "DROP ROLE IF EXISTS %s" % (TEST_ROLE2),
                    "CREATE ROLE %s" % (TEST_ROLE2),
                    "GRANT ROLE %s TO GROUP %s" % (TEST_ROLE2, TEST_USER2),

                    # Cleanup the special per-user role to start from a clean slate
                    "DROP ROLE IF EXISTS %s" % (as_owner_role),

                    # Grant create_crawler_as_owner on the catalog and access to the
                    # URI
                    "GRANT CREATE_CRAWLER_AS_OWNER ON CATALOG TO ROLE %s" % (TEST_ROLE),
                    "GRANT ALL ON URI '%s' TO ROLE %s" % (s3_uri, TEST_ROLE),
                ]

                for ddl in setup_ddls:
                    conn.execute_ddl(ddl)

                tests = [
                    CrawlerTest(provider='S3',
                                name=crawler_name,
                                root_path=s3_uri,
                                found_tables=[table_name],
                                timeout=25),
                ]
                for test in tests:
                    self.run_crawler_test(TEST_USER, test)

                user2_ddls = [
                    # Setup use role
                    "DROP ROLE IF EXISTS %s" % (TEST_ROLE2),
                    "CREATE ROLE %s" % (TEST_ROLE2),
                    "GRANT ROLE %s TO GROUP %s" % (TEST_ROLE2, TEST_USER2),

                    # Grant create_crawler_as_owner on the catalog and access to the
                    # URI
                    "GRANT %s ON CRAWLER %s TO ROLE %s" % (priv.level, crawler_name, TEST_ROLE2),
                ]
                for ddl in user2_ddls:
                    conn.execute_ddl(ddl)

                # Switch to second user who has access to just this crawler
                ctx.enable_token_auth(token_str=TEST_USER2)

                print("Running crawler privilege tests with privilege: %s" % priv.level)

                # Ensure we can "wait" for the crawler
                crawler_db = '_okera_crawler_' + crawler_name
                self._wait_for_crawler(conn, crawler_db, table_name, 25)

                # Ensure we can read the data or not
                query = "SELECT * FROM %s.%s WHERE n_name='ALGERIA'" % (crawler_db, table_name)
                if priv.can_select:
                    res = conn.scan_as_json(query)

                    assert len(res) == 1
                    assert res[0]['n_nationkey'] == 0
                else:
                    with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                        conn.scan_as_json(query)
                    self.assertTrue("'testcrawleruser2' does not have privileges to execute 'SELECT'" in str(ex_ctx.exception))

                ddl = "ALTER DATABASE %s SET dbproperties('okera.crawler.status'='')" % crawler_db
                if priv.can_alter:
                    conn.execute_ddl(ddl)
                else:
                    with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                        conn.execute_ddl(ddl)
                    self.assertTrue("'testcrawleruser2' does not have privileges to execute 'ALTER'" in str(ex_ctx.exception))

                ddl = "DROP DATABASE %s CASCADE" % crawler_db
                if priv.can_drop:
                    conn.execute_ddl(ddl)
                else:
                    with self.assertRaises(_thrift_api.TRecordServiceException) as ex_ctx:
                        conn.execute_ddl(ddl)
                    self.assertTrue("'testcrawleruser2' does not have privileges to execute 'DROP'" in str(ex_ctx.exception))


if __name__ == "__main__":
    unittest.main()
