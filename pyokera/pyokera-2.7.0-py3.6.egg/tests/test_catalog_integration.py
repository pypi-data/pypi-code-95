#import unittest
import os
import sys
from okera.tests import pycerebro_test_common as common
sys.path.append(os.path.join(os.environ.get("OKERA_HOME"), "integration", "catalog"))
# pylint: disable=wrong-import-position
import catalog_okera
import okera_catalog
from test_catalog import mock_catalog_cls

PORT = int(os.environ['ODAS_TEST_PORT_PLANNER_THRIFT'])
HOST = os.environ['ODAS_TEST_HOST']
TOKEN = "root"
LOG_DIR = os.path.join(os.environ.get("OKERA_HOME"), "logs")

# Config dictionary for all sync tests
CONFIGS = {
    'log_directory': LOG_DIR,
    'okera_host': HOST,
    'okera_port': PORT,
    'okera_token': TOKEN,
    'catalog_objects': {
        'databases': [],
        'tables': []},
    'logging_level': "debug",
    'mapped_catalog_attributes':
    [{'name': "Catalog Classification",
      'okera_namespace': "catalog_classification"},
     {'name': "Catalog Tag",
      'okera_namespace': "catalog_tag"}],
    'sync_descriptions': True
}

# Test database name
TEST_DB = "mock_db"
TEST_DB2 = "mock_db2"

# Test table names
TRANSACTIONS_TABLE = "transactions"
TRANSACTIONS2_TABLE = "transactions2"
USERS_TABLE = "users"
USERS2_TABLE = "users2"

# DDL statements to reset Okera test environment
DB_DDL = "CREATE DATABASE IF NOT EXISTS %s;"

TRANSACTIONS_DDL = """
CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
    ordernumber INT,
    quantityordered INT,
    priceeach INT,
    orderlinenumber INT,
    sales INT,
    orderdate STRING,
    status STRING,
    qtr_id INT,
    month_id INT,
    year_id INT,
    productline STRING,
    msrp INT,
    productcode STRING,
    customername STRING,
    phone STRING,
    address STRING,
    postalcode STRING,
    country STRING,
    territory STRING,
    ipaddress STRING,
    contactname STRING,
    dealsize STRING, rep STRING
)
LOCATION 's3a://cerebrodata-test/empty';"""

USERS_DDL = """
CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
    uid STRING,
    dob STRING,
    gender STRING,
    ccn STRING
)
LOCATION 's3a://cerebrodata-test/empty';"""

DROP_DDL = "DROP DATABASE IF EXISTS %s CASCADE;"

# Add description table property to table DDL
def add_description(ddl, description):
    ddl = ddl[:-1]
    desc_ddl = " TBLPROPERTIES ('comment'='%s');"
    return ddl + desc_ddl % description

# Gets objects from Okera with tags and descriptions
# Returns list with dict for each asset, example:
# [{'name': 'example_table', 'description': 'foobar'},
#   {'name': 'col1', 'Security Classification': 'Restricted'}, ...]
def get_okera_table(db, table_name, conn):
    table = conn.list_datasets(db=db, name=table_name)[0]

    return parse_okera_object(table)

def get_okera_database(db, conn):
    objects = [{"name": db, "description": None}]

    db_tables = conn.list_datasets(db=db)

    for table in db_tables:
        objects = objects + parse_okera_object(table)

    return objects

def parse_okera_object(okera_object):
    objects = []

    full_name = '.'.join([okera_object.db[0], okera_object.name])
    tbl = {"name": full_name, "description": okera_object.description}

    if okera_object.attribute_values:
        for tbl_tag in okera_object.attribute_values:
            tbl[tbl_tag.attribute.attribute_namespace] = tbl_tag.attribute.key

    objects.append(tbl)

    for column in okera_object.schema.cols:
        col = {"name": '.'.join([full_name, column.name])}
        if column.attribute_values:
            for col_tag in column.attribute_values:
                col[col_tag.attribute.attribute_namespace] = col_tag.attribute.key

        col["description"] = column.comment
        if column.comment is None:
            col["description"] = None

        objects.append(col)

    return objects

# Gets objects from the mock catalog with tags and descriptions
# Returns list with dict for each asset, example:
# [{'name': 'example_table', 'description': 'foobar'},
#   {'name': 'col1', 'Security Classification': 'Restricted'}, ...]
def get_catalog_table(mock_catalog, table_name):
    catalog_object = mock_catalog.get_table('.'.join([TEST_DB, table_name]))
    catalog_objects = [parse_catalog_object(catalog_object)]
    if catalog_object.children:
        for child in catalog_object.children:
            catalog_objects.append(parse_catalog_object(child))

    return catalog_objects

def parse_catalog_object(catalog_object):
    obj = {"name": catalog_object.name.full_name,
           "description": catalog_object.attributes['description']}

    if catalog_object.attributes['tags']:
        for tag in catalog_object.attributes['tags']:
            obj[tag.namespace] = tag.key

    return obj

# Sync mock catalog table attributes to Okera
#
# Current test attributes:
# - `transactions`: Catalog Classification = "restricted",
#                   Description = "Mock dataset sync test."
# - `transactions.phone`: Catalog Tag = "phone", PII = "phone_number"
# - `transactions.address`: Description = "Home address", PII = "address"
# - `transactions.sales`: Description = "Number of sales"
# - `users`: Description = "Mock dataset sync test.",
#            Catalog Classification = "restricted"
# - `users.ccn`: Catalog Classification = "confidential"
# - `users.dob`: Description = "Date of birth"
#
# Reset Okera test environment,
# create database `mock_db` in Okera
# create dataset `transactions` and `users` in Okera,
# sync attributes from mock catalog to Okera
def test_table_okera():
    ctx = common.get_test_context()
    ctx.enable_token_auth(token_str=TOKEN)

    with common.get_planner(ctx, host=HOST, port=PORT) as conn:
        mock_catalog = mock_catalog_cls.MockCatalog(CONFIGS)
        # Clean up Okera environment by deleting database
        conn.execute_ddl(DROP_DDL % TEST_DB)
        # Create new database and `transactions` dataset in Okera
        conn.execute_ddl(DB_DDL % TEST_DB)
        users_ddl = add_description(
            USERS_DDL % (TEST_DB, USERS_TABLE), "Mock catalog sync dataset description.")
        conn.execute_ddl(users_ddl)
        conn.execute_ddl(TRANSACTIONS_DDL % (TEST_DB, TRANSACTIONS_TABLE))

        # Set sync objects in config dictionary
        CONFIGS['catalog_objects']['tables'] = [
            '.'.join([TEST_DB, USERS_TABLE]), '.'.join([TEST_DB, TRANSACTIONS_TABLE])]

        # Run catalog to Okera sync
        catalog_okera.run_sync("mock", CONFIGS)

        # Get users tables
        catalog_users = get_catalog_table(mock_catalog, USERS_TABLE)
        okera_users = get_okera_table(TEST_DB, USERS_TABLE, conn)

        # Get transactions tables
        catalog_transactions = get_catalog_table(mock_catalog, TRANSACTIONS_TABLE)
        okera_transactions = get_okera_table(TEST_DB, TRANSACTIONS_TABLE, conn)

        # Compare list of dicts from Okera and mock catalog to ensure sync was successful
        # The table and each of its columns have a dict that contains the assets name
        # and any attributes it has, example:
        # catalog_objects = [
        #   {'name': 'example_table', 'description': 'foobar'},
        #   {'name': 'col1', 'security Classification': 'restricted'},
        #   {'name': 'col2'}]
        # okera_objects = [
        #   {'name': 'example_table', 'description': 'foobar'},
        #   {'name': 'col1', 'security classification': 'restricted'},
        #   {'name': 'col2'}]
        for obj in catalog_users:
            assert obj in okera_users

        for obj in catalog_transactions:
            assert obj in okera_transactions

# Sync mock catalog database attributes to Okera
#
# Current test attributes:
# same as test_table_okera()
#
# Reset Okera test environment,
# create database `mock_db` in Okera
# create dataset `transactions` and `users` in Okera,
# sync attributes from mock catalog to Okera
def test_database_okera():
    ctx = common.get_test_context()
    ctx.enable_token_auth(token_str=TOKEN)

    with common.get_planner(ctx, host=HOST, port=PORT) as conn:
        mock_catalog = mock_catalog_cls.MockCatalog(CONFIGS)
        # Clean up Okera environment by deleting database
        conn.execute_ddl(DROP_DDL % TEST_DB)
        # Create new database and `transactions` dataset in Okera
        conn.execute_ddl(DB_DDL % TEST_DB)
        users_ddl = add_description(
            USERS_DDL % (TEST_DB, USERS_TABLE), "Mock catalog sync dataset description.")
        conn.execute_ddl(users_ddl)
        conn.execute_ddl(TRANSACTIONS_DDL % (TEST_DB, TRANSACTIONS_TABLE))

        # Set sync objects in config dictionary
        CONFIGS['catalog_objects']['databases'].append(TEST_DB)
        CONFIGS['catalog_objects']['tables'] = []

        # Run catalog to Okera sync
        catalog_okera.run_sync("mock", CONFIGS)

        catalog_object = mock_catalog.get_database(TEST_DB)
        catalog_objects = [parse_catalog_object(catalog_object)]
        if catalog_object.children:
            for table in catalog_object.children:
                catalog_objects.append(parse_catalog_object(table))
                if table.children:
                    for column in table.children:
                        catalog_objects.append(parse_catalog_object(column))

        okera_objects = get_okera_database(TEST_DB, conn)

        for obj in catalog_objects:
            assert obj in okera_objects

# Sync mock catalog table attributes to Okera without description
#
# Current test attributes:
# same as test_table_okera() but without descriptions
#
# Reset Okera test environment,
# create database `mock_db` in Okera
# create dataset `users` in Okera,
# sync attributes from mock catalog to Okera
def test_disable_description():
    ctx = common.get_test_context()
    ctx.enable_token_auth(token_str=TOKEN)

    with common.get_planner(ctx, host=HOST, port=PORT) as conn:
        mock_catalog = mock_catalog_cls.MockCatalog(CONFIGS)
        # Clean up Okera environment by deleting database
        conn.execute_ddl(DROP_DDL % TEST_DB)
        # Create new database and `transactions` dataset in Okera
        conn.execute_ddl(DB_DDL % TEST_DB)
        conn.execute_ddl(USERS_DDL % (TEST_DB, USERS_TABLE))

        # Disable description sync in config dictionary
        CONFIGS['sync_descriptions'] = False

        # Set sync objects in config dictionary
        CONFIGS['catalog_objects']['tables'] = ['.'.join([TEST_DB, USERS_TABLE])]

        # Run catalog to Okera sync
        catalog_okera.run_sync("mock", CONFIGS)

        # Get users tables
        catalog_users = get_catalog_table(mock_catalog, USERS_TABLE)
        okera_users = get_okera_table(TEST_DB, USERS_TABLE, conn)

        # Check if Okera descriptions are none
        for obj in okera_users:
            assert obj["description"] is None

        # Check if the objects and their other attributes were synced correctly
        for obj in catalog_users:
            assert any("name" in obj for obj in okera_users)
            for attr in CONFIGS['mapped_catalog_attributes']:
                if obj.get(attr['okera_namespace']):
                    assert any(attr['okera_namespace'] in obj for obj in okera_users)

# Sync Okera table to mock catalog
#
# Current test attributes:
# - `users`: Description = "Mock catalog sync dataset description.")
#
# Reset Okera test environment,
# create database `mock_db` in Okera
# create dataset `transactions` and `users` in Okera,
# sync tables from Okera to mock catalog
def test_okera_table():
    ctx = common.get_test_context()
    ctx.enable_token_auth(token_str=TOKEN)

    with common.get_planner(ctx, host=HOST, port=PORT) as conn:
        mock_catalog = mock_catalog_cls.MockCatalog(CONFIGS)
        # Clean up Okera environment by deleting database
        conn.execute_ddl(DROP_DDL % TEST_DB)
        # Create new database and `transactions` dataset in Okera
        conn.execute_ddl(DB_DDL % TEST_DB)
        users_ddl = add_description(
            USERS_DDL % (TEST_DB, USERS2_TABLE), "Mock catalog sync dataset description.")
        conn.execute_ddl(users_ddl)
        conn.execute_ddl(TRANSACTIONS_DDL % (TEST_DB, TRANSACTIONS2_TABLE))

        # Set sync objects in config dictionary
        CONFIGS['catalog_objects']['databases'] = []
        CONFIGS['catalog_objects']['tables'] = [
            '.'.join([TEST_DB, USERS2_TABLE]), '.'.join([TEST_DB, TRANSACTIONS2_TABLE])]


        # Run catalog to Okera sync
        okera_catalog.run_sync("mock", CONFIGS)

        # Get transactions tables
        catalog_transactions = get_catalog_table(mock_catalog, TRANSACTIONS2_TABLE)
        okera_transactions = get_okera_table(TEST_DB, TRANSACTIONS2_TABLE, conn)

        # Get users tables
        catalog_users = get_catalog_table(mock_catalog, USERS2_TABLE)
        okera_users = get_okera_table(TEST_DB, USERS2_TABLE, conn)

        for obj in catalog_transactions:
            assert obj in okera_transactions

        for obj in catalog_users:
            assert obj in okera_users

# Sync Okera database to mock catalog
#
# Current test attributes:
# - `users`: Description = "Mock catalog sync dataset description.")
#
# Reset Okera test environment,
# create database `mock_db` in Okera
# create dataset `transactions` and `users` in Okera,
# sync database with tables from Okera to mock catalog
def test_okera_database():
    ctx = common.get_test_context()
    ctx.enable_token_auth(token_str=TOKEN)

    with common.get_planner(ctx, host=HOST, port=PORT) as conn:
        mock_catalog = mock_catalog_cls.MockCatalog(CONFIGS)
        # Clean up Okera environment by deleting database
        conn.execute_ddl(DROP_DDL % TEST_DB2)
        # Create new database and `transactions` dataset in Okera
        conn.execute_ddl(DB_DDL % TEST_DB2)
        users_ddl = add_description(
            USERS_DDL % (TEST_DB2, USERS_TABLE), "Mock catalog sync dataset description.")
        conn.execute_ddl(users_ddl)
        conn.execute_ddl(TRANSACTIONS_DDL % (TEST_DB2, TRANSACTIONS_TABLE))

        # Set sync objects in config dictionary
        CONFIGS['catalog_objects']['databases'].append(TEST_DB2)
        CONFIGS['catalog_objects']['tables'] = []

        # Run catalog to Okera sync
        okera_catalog.run_sync("mock", CONFIGS)

        catalog_object = mock_catalog.get_database(TEST_DB2)
        catalog_objects = [parse_catalog_object(catalog_object)]
        if catalog_object.children:
            for table in catalog_object.children:
                catalog_objects.append(parse_catalog_object(table))
                if table.children:
                    for column in table.children:
                        catalog_objects.append(parse_catalog_object(column))

        okera_objects = get_okera_database(TEST_DB2, conn)

        for obj in catalog_objects:
            assert obj in okera_objects
