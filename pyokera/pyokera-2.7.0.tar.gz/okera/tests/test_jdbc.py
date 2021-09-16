# Copyright 2020 Okera Inc. All Rights Reserved.
#
# pylint: disable=global-statement
# pylint: disable=no-self-use
# pylint: disable=no-else-return

import unittest
import io
import json
import os
import warnings
import PIL.Image as Image
import PyPDF2

from okera.tests import pycerebro_test_common as common

DEFAULT_PRESTO_PORT = int(os.environ['ODAS_TEST_PORT_PRESTO_COORD_HTTPS'])

## The all types check here will need to be verified against the JDBC data source,
## maybe by running query in DBeaver.
class JdbcScanTest(unittest.TestCase):

    def format(self, data):
        return json.dumps(data, sort_keys=True, indent=1)

    def assert_output(self, qry, expected, is_scan=True):
        warnings.filterwarnings("ignore", message="numpy.dtype size changed")
        ctx = common.get_test_context(dialect='presto')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            if is_scan:
                result = conn.scan_as_json(qry, strings_as_utf8=False)
            else:
                result = conn.execute_ddl(qry)
            print("Actual and expected: ")
            print(format(result))
            print(expected)
            print("Done printing.....")
            assert result == expected

    def test_dremio_basic(self):
        CXN = 'test_dremio_connection'
        DB = 'test_dremio'
        CONFIG = 's3://cerebrodata-dev/jdbc/dremio.properties'
        ctx = common.get_test_context()

        create_connection = [
            """
                CREATE DATACONNECTION %s CXNPROPERTIES
                (
                'connection_type'='JDBC',
                'jdbc_driver'='dremio',
                'user_key'='awssm://dremio_internal_akshay',
                'password_key'='awssm://dremio_internal_akshay_password',
                'host'='dremio.internal.okera.rocks',
                'port'='31010',
                'connection_properties'='{"driver.jar.path":"s3://okera-jdbc-test/drivers/dremio-jdbc-driver-12.0.0.jar", "fetchSize": "64"}'
                )
            """ % CXN,

            # Using connection pool
            """
                CREATE DATACONNECTION %s CXNPROPERTIES
                (
                'connection_type'='JDBC',
                'jdbc_driver'='dremio',
                'user_key'='awssm://dremio_internal_akshay',
                'password_key'='awssm://dremio_internal_akshay_password',
                'host'='dremio.internal.okera.rocks',
                'port'='31010',
                'connection_properties'='{"driver.jar.path":"s3://okera-jdbc-test/drivers/dremio-jdbc-driver-12.0.0.jar", "fetchSize": "64", "supports.connection-pool"="true"}'
                )
            """ % CXN,

            # TODO: add following variants:
            # 1. Using newer driver
            # 2. Using built in driver (with and without pooling)
        ]

        with common.get_planner(ctx) as conn:
            # The 'test' db exists in this dremio cluster but is empty
            for create in create_connection:
                conn.execute_ddl('DROP DATABASE IF EXISTS %s CASCADE' % DB)
                conn.execute_ddl('DROP DATACONNECTION IF EXISTS %s' % CXN)
                conn.execute_ddl(create)
                conn.execute_ddl("""CREATE DATABASE %s DBPROPERTIES(
                    'okera.connection.name' = '%s',
                    'jdbc.schema.name'='okera.okera-demo',
                    'okera.autotagger.skip'='true')""" % (DB, CXN))
                conn.execute_ddl('ALTER DATABASE %s LOAD DEFINITIONS()' % DB)
                datasets = conn.list_dataset_names(DB)
                self.assertTrue(('%s.hospital_discharge_sampled' % DB) in datasets,
                                msg=str(datasets))
                result = conn.scan_as_json(
                    'select facility_name from %s.hospital_discharge_sampled limit 1' %\
                    DB)
                print(result)
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]['facility_name'], 'Oneida Healthcare Center')

                conn.scan_as_json('%s.hospital_discharge_sampled limit 250' % DB)

    def test_jdbc_blob_img_file_download(self):
        qry = "select * from jdbc_test_oracle.blob_test where id = 1"
        warnings.filterwarnings("ignore", message="numpy.dtype size changed")
        ctx = common.get_test_context(dialect='okera')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            result = conn.scan_as_pandas(qry)
        data = result.to_dict('records')

        # if underlying "blob_data" column is null, it is returned as float.
        # For non null values, data should be returned as bytes. That's why below assert
        self.assertTrue(isinstance(data[0]['blob_data'], bytes), \
            "The value of 'blob_data' column is not returned as bytes!! ")

        # Cleanup if file exists.
        tmp_image_file = '/tmp/test_jdbc_blob_img_file_download.png'
        if os.path.exists(tmp_image_file):
            os.remove(tmp_image_file)

        # Download image and save as png. We know the original one was png format.
        image = Image.open(io.BytesIO(data[0]['blob_data']))
        image.save(tmp_image_file)

        # Open and verify the image.
        if os.path.exists(tmp_image_file):
            image = Image.open(tmp_image_file)
            # Assert the image size.
            assert image.size[0] == 1000
            assert image.size[1] == 562
            image.verify()
        else:
            # no file is downloaded. underlying jdbc source might have 'blob_data' as NULL
            self.assertTrue(1 == 2, "No image file availalbe!! Please investigate.")

    def test_jdbc_blob_pdf_file_download(self):
        qry = "select * from jdbc_test_oracle.blob_test where id = 2"
        warnings.filterwarnings("ignore", message="numpy.dtype size changed")
        ctx = common.get_test_context(dialect='okera')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            result = conn.scan_as_pandas(qry)
        data = result.to_dict('records')

        # if underlying "blob_data" column is null, it is returned as float.
        # For non null values, data should be returned as bytes. That's why below assert
        self.assertTrue(isinstance(data[0]['blob_data'], bytes), \
            "The value of 'blob_data' column is not returned as bytes!! ")

        # Cleanup if file exists.
        tmp_pdf_file = '/tmp/test_jdbc_blob_pdf_file_download.pdf'
        if os.path.exists(tmp_pdf_file):
            os.remove(tmp_pdf_file)

        # Read the pdf contents which is stored as blob
        pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(data[0]['blob_data']), strict=False)
        assert pdf_reader.numPages == 2

        # Write pdf contents into the blank file "test_jdbc_blob_pdf_file_download.pdf"
        pdf_writer = PyPDF2.PdfFileWriter()
        for page_num in range(pdf_reader.numPages):
            page_obj = pdf_reader.getPage(page_num)
            pdf_writer.addPage(page_obj)
        pdf_output_file = open(tmp_pdf_file, 'wb')
        pdf_writer.write(pdf_output_file)
        pdf_output_file.close()

        # Assert the no. of pages in the newly written file
        pdf_reader = PyPDF2.PdfFileReader(tmp_pdf_file)
        assert pdf_reader.numPages == 2

    def test_jdbc_clob_txt_file_download(self):
        qry = "select * from jdbc_test_oracle.clob_test where id = 1"
        warnings.filterwarnings("ignore", message="numpy.dtype size changed")
        ctx = common.get_test_context(dialect='okera')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx, presto_port=DEFAULT_PRESTO_PORT) as conn:
            result = conn.scan_as_pandas(qry)
        data = result.to_dict('records')

        # if underlying "clob_data" column is null, it is returned as float.
        # For non null values, data should be returned as bytes. That's why below assert
        self.assertTrue(isinstance(data[0]['clob_data'], bytes), \
            "The value of 'clob_data' column is not returned as bytes!! ")

        # Cleanup if file exists.
        tmp_txt_file = '/tmp/test_jdbc_clob_txt_file_download.txt'
        file_size = 0
        if os.path.exists(tmp_txt_file):
            os.remove(tmp_txt_file)

        # Open the blank file, write the data and verify the file size
        with open(tmp_txt_file, 'wb') as file_handle:
            file_handle.write(bytes(data[0]['clob_data']))
            file_handle.close()
            file_size = os.path.getsize(tmp_txt_file)

        # Assert the file size (in bytes)
        assert file_size == 6121

    def test_jdbc_all_types(self):
        self.assert_output(
            'select * from jdbc_test_mysql.all_types_v2',
            [{'date': None, 'decimal': None, 'float': None, 'mediumint': None,
              'blob': None, 'tinyblob': None, 'bigint': None,
              'mediumtext': None, 'datetime': None, 'time': None,
              'longtext': None, 'mediumblob': None, 'smallint': None, 'enum': None,
              'varchar': None, 'tinytext': None, 'timestamp': None, 'binary': None,
              'longblob': None, 'int': None, 'set': None, 'tinyint': None, 'bool': None,
              'varbinary': None, 'text': None, 'char': None, 'double': None},
             {'date': '1990-01-01', 'decimal': '8.23', 'float': 7.099999904632568,
              'mediumint': 3, 'blob': 'blob', 'tinyblob': 'tinyblob', 'bigint': 5,
              'mediumtext': 'mediumtext', 'datetime': '2020-10-01 18:19:03.000',
              'time': '1970-01-01 00:20:20.000', 'longtext': 'longtext',
              'mediumblob': 'mediumblob', 'smallint': 2, 'enum': '1', 'varchar':
              'test', 'tinytext': 'tinytext', 'timestamp': '2017-06-01 18:19:03.000',
              'binary': 'binary\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
              'longblob': 'longblob', 'int': 4, 'set': '1,2  ', 'tinyint': 1,
              'bool': True, 'varbinary': 'varbinary', 'text': 'hello',
              'char': 'char      ', 'double': 6.0}])

        self.assert_output(
            'select * from jdbc_test_psql.all_types',
            [{'bigint': None, 'bigserial': 1, 'money': None, 'numeric': None,
              'text': None, 'timestamp': None, 'real': None, 'serial': 1, 'bool': None,
              'int': None, 'double': None, 'time': None, 'smallint': None, 'bit': None,
              'varchar': None, 'decimal': None, 'char': None},
             {'bigint': 3, 'bigserial': 2, 'money': 10.0, 'numeric': '7.10',
              'text': 'hello', 'timestamp': '2017-06-01 18:19:03.000', 'real': 2.13000011,
              'serial': 2, 'bool': True, 'int': 2, 'double': 6.0,
              'time': '1970-01-01 18:19:03.000', 'smallint': 1,
              'bit': 1010101010, 'varchar': 'test', 'decimal': '8.23',
              'char': 'char      '}])

        self.assert_output(
            'select * from jdbc_test_redshift.all_types',
            [{'int': None, 'decimal': None, 'text': None, 'smallint': None,
              'numeric': None, 'real': None, 'char': None, 'double': None, 'bool': None,
              'varchar': None, 'timestamp': None, 'bigint': None},
             {'int': 2, 'decimal': '8.23', 'text': 'hello', 'smallint': 1,
              'numeric': '7.10', 'real': 10.0, 'char': 'char      ',
              'double': 6.0, 'bool': True, 'varchar': 'test',
              'timestamp': '2017-06-01 18:19:03.000', 'bigint': 3}])

        self.assert_output(
            'select * from jdbc_test_oracle.all_types',
            [{'int_col': 4, 'date_col': '2017-06-01 00:00:00.000',
              'timestamp_col': '2017-06-01 18:19:03.000', 'smallint_col': 3,
              'dec_col': '4000000.45', 'number_col': '1.000000', 'numeric_col': 2,
              'bigint_col': '100000000000', 'decimal_col': '3000.45',
              'char_col': 'char      ', 'float_col': 3.4000000953674316,
              'varchar_col': 'varchar2', 'nvarchar_col': 'nvarchar2'},
             {'int_col': None, 'date_col': None, 'timestamp_col': None,
              'smallint_col': None, 'dec_col': None, 'number_col': None,
              'numeric_col': None, 'bigint_col': None, 'decimal_col': None,
              'char_col': None, 'float_col': None, 'varchar_col': None,
              'nvarchar_col': None}])

        ## TODO for snowflake, athena and sqlserver

    def check_jdbc_source_by_schema(self, **kwargs):
        '''
            A common test method to create a jdbc_data_source by schema and iterate
            through the tables and verify the query is successful.
        '''
        # Eventually, we can just call test_authorization on this.
        select_queries = [
            'select * from {}',
            'select count(*) from {}'
            ]
        ctx = common.get_test_context(dialect='okera')
        ctx.enable_token_auth(token_str='root')
        with common.get_planner(ctx) as conn:
            db_name = kwargs['db_name']
            schema_name = kwargs['schema_name']
            creds_file = kwargs['credentials_file']
            # Cleanup existing DB
            conn.execute_ddl("DROP DATABASE IF EXISTS {} CASCADE".format(db_name))
            # Create the test database with credentials file.
            conn.execute_ddl('''
                CREATE DATABASE IF NOT EXISTS {} DBPROPERTIES
                ('credentials.file' = '{}',
                 'jdbc.schema.name'='{}')'''.format(db_name, creds_file, schema_name))
            # Prepare datasets
            conn.execute_ddl("ALTER DATABASE {} LOAD DEFINITIONS()".format(db_name))

            res = conn.execute_ddl("SHOW TABLES IN {} ".format(db_name))
            print(res)
            print(len(res))
            self.assertEqual(len(res), kwargs['expected_table_count'])
            if kwargs['skip_scan']:
                return
            for table in res:
                if table[0] in kwargs['ignore_tables_list']:
                    continue
                for query in select_queries:
                    result = conn.scan_as_pandas(query.format(db_name + "." + table[0]))
                    # dummy statement
                    print(len(result))

    @unittest.skip("SAP HANA instance can be costly to maintain, skip tests for normal.")
    def test_saphana_jdbc_source(self):
        '''
            This test is run on-demand due to maintenance cost of SAP HANA instances.
            If needed to test, a standard SAP HANA Express Edition 2.0 can be spun up
            and we check for some schemas in the pre-loaded SAP HANA instances.
        '''
        # These schemas have some interesting tables/views.
        # SAP HANA has some special views like CALC VIEW, HIERARCHY VIEW etc which are
        # based on stored procedures. No JDBC tools support it (like DBeaver etc), we
        # skip those views for scanning. The customer has a choice to include them
        # by setting `table.types` property in the credentials file.
        # See 's3://cerebro-datasets/jdbc_demo/jdbc_saphana_all_table_types.conf'.
        # The HANA_XS_BASE and _SI_BIC schema is full of such special views.
        # Those two schemas also have very special characters which are good test cases.
        # The _SYS_STATISTICS is a big schema and good stress test for metadata operation.
        saphana_schemas_to_verify = [
            ('_SYS_BI', 57, False, ['get_bwauths4hana_tabletype_valtab']),
            ('HANA_XS_BASE', 23, True, []),
            ('_SYS_BIC', 10, True, []),
            ('_SYS_STATISTICS', 388, False,
             ['tt_mail_collector', 'tt_statistics_alert_thresholds',
              'tt_statistics_used_values'])]
        cred_file = 's3://cerebro-datasets/jdbc_demo/jdbc_saphana_all_table_types.conf'
        for schema in saphana_schemas_to_verify:
            (s_name, count, skip, ignore_tables) = schema
            self.check_jdbc_source_by_schema(
                db_name='jdbc_saphana_test', credentials_file=cred_file,
                schema_name=s_name, expected_table_count=count, skip_scan=skip,
                ignore_tables_list=ignore_tables)
