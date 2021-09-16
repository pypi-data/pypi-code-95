# Copyright 2020 Okera Inc. All Rights Reserved.
import os

from boto3 import Session
from pyspark.sql import SparkSession

OKERA_HOME = os.environ["OKERA_HOME"]
OKERA_JAVA_VERSION = os.environ["OKERA_JAVA_VERSION"]

# Planner vars
ODAS_TEST_HOST = os.environ["ODAS_TEST_HOST"]
PLANNER_THRIFT_URL = ODAS_TEST_HOST + ":" + os.environ['ODAS_TEST_PORT_PLANNER_THRIFT']

# Hive thrift URL
HIVE_THRIFT_URL = 'thrift://' + ODAS_TEST_HOST + ":" + \
    os.environ['ODAS_TEST_PORT_HIVE_THRIFT']
# Spark master URL
SPARK_MASTER_URL = 'spark://' + ODAS_TEST_HOST + ":" + \
    os.environ['ODAS_TEST_PORT_SPARK_MASTER']

# This is needed for authenticating to ODAS planner.
DEFAULT_SPARK_USER = 'okera'
os.environ["HADOOP_USER_NAME"] = DEFAULT_SPARK_USER

# This is needed for HMS discovery. Note, the spark job is still submitted to the
# spark cluster.
SPARK_JAR_NAME = OKERA_HOME + '/rsc/java/spark2/target/recordservice-spark-2.0-' + \
    OKERA_JAVA_VERSION + '.jar'
HIVE_JAR_NAME = OKERA_HOME + '/rsc/java/hive/target/recordservice-hive-' + \
    OKERA_JAVA_VERSION + '.jar'
HIVE_UDF_NAME = OKERA_HOME + '/tools/hive-udf/target/okera-hive-udfs-0.1.1.jar'

# Additional jars needed to read from S3, this is not included by spark by default.
ADDITIONAL_JARS = OKERA_HOME + '/thirdparty/spark/hadoop-aws-2.7.3.jar'
ADDITIONAL_JARS += ',' + OKERA_HOME + '/thirdparty/spark/aws-java-sdk-1.7.4.jar'
ADDITIONAL_JARS += ',' + OKERA_HOME + '/thirdparty/spark/snappy-java-1.1.7.3.jar'

os.environ["PYSPARK_SUBMIT_ARGS"] = '--jars ' + SPARK_JAR_NAME + ',' + HIVE_JAR_NAME + \
    ',' + HIVE_UDF_NAME + ',' + ADDITIONAL_JARS + ' pyspark-shell'

def get_spark_session(app_name):
    credentials = Session().get_credentials()

    return (SparkSession.builder.appName(app_name)
            .master(SPARK_MASTER_URL)
            .config("spark.recordservice.user", DEFAULT_SPARK_USER)
            .config("hive.metastore.uris", HIVE_THRIFT_URL)
            .enableHiveSupport()
            .config("spark.recordservice.planner.hostports",
                    PLANNER_THRIFT_URL)
            .config("fs.s3a.access.key", credentials.access_key)
            .config("fs.s3a.secret.key", credentials.secret_key)
            .config("spark.cores.max", "2")
            .config("spark.executor.memory", "2048M")
            .getOrCreate())

authorize_query_unsupported_datasets = [
    # Complex types view syntax issues
    'authdb.struct_t_join_clause_view',
    'chase.feescharges_view',
    'chase.second_level',
    'chase.subscription_party_view',
    'rs_complex.pn_view',
    'zd1179large.store_sales_pk_view',

    # Unknown, need to explore
    'demo_test.transactions_active_users',
    'demo_test.transactions_anonymize_inactive_users',
    'nytaxi.unionallview',
    'rs_complex.market_decide_single_avro',

    # Join hint is causing issues, should not be output in query rewrite
    'rs.nation_join_cache',
    'rs.nation_join_cache_and_size_hint',
    'rs.nation_join_size_hint',

    # Skipping as these joins take a long time
    'tpch_sf1.lineitem_orders',
    'tpch_sf1.lineitem_orders_medium',
    'tpch_sf5.lineitem_orders',
    'tpch_sf5.lineitem_orders_medium',
    'tpch_sf5.lineitem_orders_small',

    # Hive/Spark doesn't like the avro schemas
    'chase.zd1211',
    'chase.zd1211_1',
    'chase.zd1211_join_view',
    'chase.zd1211_view',
    'chase.zd1238',
    'chase.zd1238_1',
    'chase.zd1238_2',
    'chase.zd1238_3',
    'chase.zd1238_4',
    'chase.zd1238_5',
    'chase.zd1238_6',
    'chase.zd1238_7',
    'chase.zd1238_8',
    'chase.zd1238_9',
    'customer.account_alternate1_phone_number_updated_from_file',
    'rs_complex.avrotbl',
    'rs_complex.bytes_type_file',
    'rs_complex.global_dtc_daily_store_stock_on_hand_snapshot',
    'rs_complex.non_null_union',
    'rs_complex.rs_complex_array_map_t',
    'rs_complex.zd1216',
    'rs_complex.zd1216_with_subscriptionlimit',

    # TODO: complex views
    'rs_complex.struct_nested_s1_s2',
    'rs_complex_parquet.struct_nested_s1_s2',
]
