import json
import logging
import os
import sys
import unittest
from okera.tests import pycerebro_test_common as common
sys.path.append(os.path.join(os.environ.get("OKERA_HOME"), "integration", "collibra"))
# pylint: disable=wrong-import-position
from collibra_okera import collibra_okera
from okera_collibra import okera_collibra

PORT = int(os.environ['ODAS_TEST_PORT_PLANNER_THRIFT'])
HOST = os.environ['ODAS_TEST_HOST']
LOG_DIR = os.path.join(os.environ.get("OKERA_HOME"), "logs")
TOKEN = "root"
COLLIBRA_DGC = "https://okera.collibra.com:443"
COLLIBRA_USERNAME = "Admin"
COLLIBRA_PASSWORD = "Gac2Quencotdilo"

# Config dict for Collibra -> Okera
EXPORT_CONFIGS = {
    'log_directory':LOG_DIR,
    'okera_host': HOST,
    'okera_token': TOKEN,
    'collibra_dgc': COLLIBRA_DGC,
    'collibra_username': COLLIBRA_USERNAME,
    'collibra_password': COLLIBRA_PASSWORD,
    'collibra_assets': "",
    'mapped_collibra_attributes': [
        {'attribute_name': "Security Classification",
         'attribute_id': "00000000-0000-0000-0001-000500000031",
         'okera_namespace': "security_classification",
         'prioritize_column_attribute': False}
    ],
    'mapped_collibra_statuses': {
        'statuses': ["Accepted", "Under Review"],
        'okera_namespace': "collibra_status"
    },
    'full_name_prefixes': None
}

# Config dict for Okera -> Collibra
IMPORT_CONFIGS = {
    'log_directory': LOG_DIR,
    'okera_host': HOST,
    'okera_token': TOKEN,
    'collibra_dgc': COLLIBRA_DGC,
    'collibra_username': COLLIBRA_USERNAME,
    'collibra_password': COLLIBRA_PASSWORD,
    'collibra_assets': ""
}

# Collibra test community
COMMUNITY = "Okera Test"
COMMUNITY_ID = "16c061ce-c1a7-4730-86fd-fb5f485452bb"

# Collibra test domain
DOMAIN = "Integration Test"
DOMAIN_ID = "a1887114-104d-4e38-9d3b-393b2ac0b6fa"

# Test database name
TEST_DB = "test_collibra_integration"

# Test table names
TRANSACTIONS_TABLE = "transactions"
USERS_TABLE = "users"

# Collibra attribute IDs
ATTRIBUTE_IDS = [
    {'name': "Description", 'id': "00000000-0000-0000-0000-000000003114"},
    {'name': "Location", 'id': "00000000-0000-0000-0000-000000000203"},
    {'name': "Technical Data Type", 'id': "00000000-0000-0000-0000-000000000219"},
    {'name': "Security Classification", 'id': "00000000-0000-0000-0001-000500000031"}
]

# Collibra asset IDs
ASSET_IDS = [
    {'name': "Column", 'id': "00000000-0000-0000-0000-000000031008"},
    {'name': "Database", 'id': "00000000-0000-0000-0000-000000031006"},
    {'name': "Table", 'id': "00000000-0000-0000-0000-000000031007"}
]

# Collibra relation ID for Table -> Database
TBL_RELATION_ID = "00000000-0000-0000-0000-000000007045"
# Collibra relation ID for Column -> Table
COL_RELATION_ID = "00000000-0000-0000-0000-000000007042"

# Collibra status ID for test status 'Accepted'
ACCEPTED_STATUS_ID = "00000000-0000-0000-0000-000000005009"

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
LOCATION 's3a://cerebrodata-test/empty'
TBLPROPERTIES ('comment'='%s');
"""

USERS_DDL = """
CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
    uid STRING,
    dob STRING,
    gender STRING,
    ccn STRING
)
LOCATION 's3a://cerebrodata-test/empty'
TBLPROPERTIES ('comment'='%s');
"""

DROP_DDL = "DROP DATABASE IF EXISTS %s CASCADE;"

# List of columns of the two test datasets
TABLE1_COLS = ["ordernumber", "quantityordered", "priceeach", "orderlinenumber",
               "sales", "orderdate", "status", "qtr_id", "month_id",
               "year_id", "productline", "msrp", "productcode",
               "customername", "phone", "address", "postalcode",
               "country", "territory", "ipaddress", "contactname",
               "dealsize", "rep"]

TABLE2_COLS = ["uid", "dob", "gender", "ccn"]

# Turns assets into dict with the same structure as assets.yaml
def format_assets(tables):
    return {'communities': [
        {'name': COMMUNITY,
         'id': COMMUNITY_ID,
         'domains': [
             {'name': DOMAIN,
              'id': DOMAIN_ID,
              'databases': None,
              'tables': tables}]
         }]}

# Unsure about 'cerebro/logs'
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    format='%(levelname)s %(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename=os.path.join(LOG_DIR, "test_collibra_integration.log"),
    level=logging.DEBUG
)

# PyOkera context

# Escapes special characters and removes whitespace
def escape(string, remove_whitespace=False):
    if string:
        if remove_whitespace:
            return json.dumps(string.lower().replace(" ", "_"))[1:-1]
        return json.dumps(string.lower())[1:-1]
    return ""

# Gets resource IDs from ASSET_IDS and ATTRIBUTE_IDS
def get_resource_id(id_type, attr_name):
    for a in id_type:
        if a['name'] == attr_name:
            return a['id']
    return None

# Returns Collibra assets based on the search parameters
# Using nameMatchMode and typeId allows for a more refined search
def search_collibra_asset(name, type_id=None, match_mode="EXACT"):
    params = {
        'name': name,
        'nameMatchMode': match_mode,
        'domainId': DOMAIN_ID,
        'communityId': COMMUNITY_ID
    }

    if type_id:
        params.update({'typeId': type_id})

    asset = collibra_okera.collibra_request(params, "assets", "get", IMPORT_CONFIGS)

    return asset['results']

# Adds attributes to assets in Collibra for export and bidirectional test
def add_collibra_attribute(asset_id, attr_type, attr_value):
    attribute_params = {
        'assetId': asset_id,
        'typeId': get_resource_id(ATTRIBUTE_IDS, attr_type),
        'value': attr_value
        }

    collibra_okera.collibra_request(
        attribute_params, "attributes", "post", IMPORT_CONFIGS)


# Resets test environment in Collibra by deleting all assets in the given domain
def _cleanup_collibra(db):
    delete_ids = []
    assets = search_collibra_asset(name=db, match_mode="START")

    for a in assets:
        delete_ids.append(a['id'])

    collibra_okera.collibra_request(delete_ids, "assets/bulk", "delete", IMPORT_CONFIGS)

# Sets up a new Collibra test environment in the given domain
#
# A new test database and optionally a test table are created.
# If a table is created all the tables columns are created
# with relations to connect the table to the database and the
# columns to the table. Since the script leverages relations to
# find assets in Collibra, this ensures that the assets have the correct
# hierarchy.
#
# pylint: disable=too-many-locals
def _collibra_setup(db, table=None, status_id=None):
    assets = []

    def set_asset_params(name, display_name, type_id):
        return {
            'name': name,
            'displayName': display_name,
            'domainId': DOMAIN_ID,
            'typeId': type_id,
        }

    def set_relation_params(source_id, target_id, type_id):
        return {
            'sourceId': source_id,
            'targetId': target_id,
            'typeId': type_id
        }

    # Create test database
    database_params = set_asset_params(db, db, get_resource_id(ASSET_IDS, "Database"))
    db_id = collibra_okera.collibra_request(
        database_params, "assets", "post", IMPORT_CONFIGS)['id']

    # Create table with columns
    if table:
        tbl_full_name = '.'.join([db, table['name']])
        table_params = set_asset_params(
            tbl_full_name, table['name'], get_resource_id(ASSET_IDS, "Table"))
        if status_id:
            table_params.update({'statusId': status_id})

        tbl_id = collibra_okera.collibra_request(
            table_params, "assets", "post", IMPORT_CONFIGS)['id']
        assets = [{'name': tbl_full_name, 'id': tbl_id}]

        # Creates relation between table and database
        tbl_relation_params = set_relation_params(tbl_id, db_id, TBL_RELATION_ID)
        collibra_okera.collibra_request(
            tbl_relation_params, "relations", "post", IMPORT_CONFIGS)

        for col in table['columns']:
            col_full_name = '.'.join([tbl_full_name, col])
            col_params = set_asset_params(
                col_full_name, col, get_resource_id(ASSET_IDS, "Column"))
            col_id = collibra_okera.collibra_request(
                col_params, "assets", "post", IMPORT_CONFIGS)['id']
            assets.append({'name': col, 'id': col_id})

            # Creates relation bewteen column and table
            col_relation_params = set_relation_params(col_id, tbl_id, COL_RELATION_ID)
            collibra_okera.collibra_request(
                col_relation_params, "relations", "post", IMPORT_CONFIGS)

    if assets:
        return assets

# Gets assets from Okera with tags and descriptions
# Returns list with dict for each asset, example:
# [{'name': 'example_table', 'description': 'foobar'},
#   {'name': 'col1', 'Security Classification': 'Restricted'}, ...]
def get_okera_assets(db, table_name, conn):
    assets = []

    table = conn.list_datasets(db=db, name=table_name)[0]
    full_name = '.'.join([table.db[0], table.name])
    tbl = {"name": full_name, "description": table.description}
    if table.attribute_values:
        for tbl_tag in table.attribute_values:
            tbl[tbl_tag.attribute.attribute_namespace] = tbl_tag.attribute.key
    assets.append(tbl)

    for column in table.schema.cols:
        col = {"name": '.'.join([full_name, column.name])}
        if column.attribute_values:
            for col_tag in column.attribute_values:
                col[col_tag.attribute.attribute_namespace] = col_tag.attribute.key
        if column.comment:
            col["description"] = column.comment
        assets.append(col)

    return assets

# Gets assets and attributes from Collibra
# Returns list with dict for each asset, example:
# [{'name': 'example_table', 'description': 'foobar'},
#   {'name': 'col1', 'Security Classification': 'Restricted'}, ...]
def get_collibra_assets(full_tbl_name):
    assets = []
    attr_ids = []
    # Importing assets will automatically add the attributes Technical Data Type
    # and Location but we do not want to compare these because they are constants
    for attr in ATTRIBUTE_IDS:
        if attr['name'] not in ["Technical Data Type", "Location"]:
            attr_ids.append(attr['id'])

    table_params = {
        'name': full_tbl_name,
        'nameMatchMode': "EXACT",
        'domainId': DOMAIN_ID,
        'communityId': COMMUNITY_ID,
        'typeId': get_resource_id(ASSET_IDS, "Table")
    }

    tbl_data = collibra_okera.collibra_request(
        table_params, "assets", "get", IMPORT_CONFIGS)['results'][0]
    tbl_attributes = _get_collibra_attributes(tbl_data['id'], attr_ids)
    table = {'name': tbl_data['name']}
    for attr in tbl_attributes:
        table.update(attr)
    assets.append(table)

    column_params = {'relationTypeId': COL_RELATION_ID, 'targetId': tbl_data['id']}
    col_data = collibra_okera.collibra_request(
        column_params, 'relations', 'get', IMPORT_CONFIGS)
    for col in col_data['results']:
        col_attributes = _get_collibra_attributes(col['source']['id'], attr_ids)
        column = {'name': col['source']['name']}
        for attr in col_attributes:
            column.update(attr)
        assets.append(column)

    return assets

# Gets all attributes of asset by asset_id
def _get_collibra_attributes(asset_id, attr_ids):
    attributes = []
    attr_params = {
        'typeIds': attr_ids,
        'assetId': asset_id
    }

    data = collibra_okera.collibra_request(
        attr_params, "attributes", "get", IMPORT_CONFIGS)
    for d in data['results']:
        value = d['value'] if d['type']['name'] == "Description" else escape(
            d['value'], True)
        attributes.append({escape(d['type']['name'], True): value})

    return attributes

# Okera to Collibra tests
#
# Reset Collibra and Okera test environment,
# create datasets `transactions` and `users` in Okera,
# import `transactions` into domain and sync `users` description
# table1 = `transactions`, table2 = `users`
@unittest.skipIf(common.TEST_LEVEL != "all", "Skipping at unit test level")
def test_okera_collibra():
    ctx = common.get_test_context()
    ctx.enable_token_auth(token_str=TOKEN)

    tbl1_full_name = '.'.join([TEST_DB, TRANSACTIONS_TABLE])
    tbl2_full_name = '.'.join([TEST_DB, USERS_TABLE])

    table2 = {'name': USERS_TABLE, 'columns': TABLE2_COLS}

    table_desc = "Dataset to test Okera to Collibra sync."

    # Deletes all assets in the given domain
    _cleanup_collibra(TEST_DB)

    with common.get_planner(ctx, host=HOST, port=PORT) as conn:
        # Clean up Okera environment by deleting database
        conn.execute_ddl(DROP_DDL % TEST_DB)
        # Create new database and datasets `transactions` (TRANSACTIONS_TABLE)
        # and `users` (USERS_TABLE) in Okera
        conn.execute_ddl(DB_DDL % TEST_DB)
        conn.execute_ddl(TRANSACTIONS_DDL % (TEST_DB, TRANSACTIONS_TABLE, table_desc))
        conn.execute_ddl(USERS_DDL % (TEST_DB, USERS_TABLE, table_desc))

        # Setup Collibra environment by creating new test assets,
        # returns list of imported assets with asset ID
        _collibra_setup(TEST_DB, table2)

        # Run import script
        okera_collibra.run(IMPORT_CONFIGS, format_assets(
            [tbl1_full_name, tbl2_full_name]), PORT)

        # Collect asset information for `transactions`
        collibra_assets_table1 = get_collibra_assets(tbl1_full_name)
        okera_assets_table1 = get_okera_assets(TEST_DB, TRANSACTIONS_TABLE, conn)

        # Collect asset information for `users`
        collibra_assets_table2 = get_collibra_assets(tbl2_full_name)
        okera_assets_table2 = get_okera_assets(TEST_DB, USERS_TABLE, conn)

        # Compare list of dicts from Okera and Collibra to ensure sync was successful
        # The table and each of its columns have a dict that contains the assets name
        # and any attributes it has, example:
        # collibra_assets = [
        #   {'name': 'example_table', 'description': 'foobar'},
        #   {'name': 'col1', 'Security Classification': 'Restricted'},
        #   {'name': 'col2'}]
        # okera_assets = [
        #   {'name': 'example_table', 'description': 'foobar'},
        #   {'name': 'col1', 'security classification': 'restricted'},
        #   {'name': 'col2'}]

        # Comparing `transactions`
        for tbl1_asset in collibra_assets_table1:
            assert tbl1_asset in okera_assets_table1

        # Comparing `users`
        for tbl2_asset in collibra_assets_table2:
            assert tbl2_asset in okera_assets_table2

# Collibra to Okera test
#
# Current test attributes:
# - `transactions`: Security Classification = "Restricted", Status = "Under Review")
# - `transactions.address`: Security Classification = "Confidential"
# - `transactions.ipaddress`: Security Classification = "Highly Confidential"
# - `transactions.sales`: Description = "Number of sales"
#
# Reset Collibra and Okera test environment,
# create dataset `transactions` in Okera,
# create table `transactions` in Collibra,
# add test attributes to table in Collibra,
# sync attributes from Collibra to Okera
#
# pylint: disable=too-many-locals
@unittest.skipIf(common.TEST_LEVEL != "all", "Skipping at unit test level")
def test_collibra_okera():
    EXPORT_CONFIGS['mapped_collibra_attributes'][0]['prioritize_column_attribute'] = True

    ctx = common.get_test_context()
    ctx.enable_token_auth(token_str=TOKEN)

    tbl_full_name = '.'.join([TEST_DB, TRANSACTIONS_TABLE])

    table_desc = "Dataset to test Collibra to Okera sync."

    assets = {'name': TRANSACTIONS_TABLE, 'columns': TABLE1_COLS}

    # Deletes all assets in the given domain
    _cleanup_collibra(TEST_DB)

    with common.get_planner(ctx, host=HOST, port=PORT) as conn:
        # Clean up Okera environment by deleting database
        conn.execute_ddl(DROP_DDL % TEST_DB)
        # Create new database and `transactions` dataset in Okera
        conn.execute_ddl(DB_DDL % TEST_DB)
        conn.execute_ddl(TRANSACTIONS_DDL % (TEST_DB, TRANSACTIONS_TABLE, table_desc))

        # Setup Collibra environment by creating new test assets,
        # returns list of imported assets with asset ID
        export_assets = _collibra_setup(TEST_DB, assets, ACCEPTED_STATUS_ID)

        # Getting each asset ID from assets imported in _collibra_setup()
        # which is needed to add attributes
        tbl_id = [asset["id"]
                  for asset in export_assets if asset["name"] == tbl_full_name][0]
        col1_id = [asset["id"]
                   for asset in export_assets if asset["name"] == "ipaddress"][0]
        col2_id = [asset["id"]
                   for asset in export_assets if asset["name"] == "address"][0]
        col3_id = [asset["id"]
                   for asset in export_assets if asset["name"] == "sales"][0]

        # Adding test attributes for each asset
        add_collibra_attribute(tbl_id, "Description", table_desc)
        add_collibra_attribute(tbl_id, "Security Classification", "Restricted")
        add_collibra_attribute(
            col1_id, "Security Classification", "Confidential")
        add_collibra_attribute(
            col2_id, "Security Classification", "Highly Confidential")
        add_collibra_attribute(col3_id, "Description", "Number of sales")

        # Run export script
        collibra_okera.run(EXPORT_CONFIGS, format_assets([tbl_full_name]), PORT)

        # Collect asset information for `transactions`
        collibra_assets = get_collibra_assets(tbl_full_name)
        okera_assets = get_okera_assets(TEST_DB, TRANSACTIONS_TABLE, conn)

        # Get table status and append to attribute
        # Status is only returned when getting the asset itself,
        # there is no API call to get JUST the status by the asset ID
        for attr in collibra_assets:
            if attr['name'] == tbl_full_name:
                table_id = get_resource_id(ASSET_IDS, "Table")
                status = search_collibra_asset(tbl_full_name, table_id)[
                    0]['status']['name']
                attr['collibra_status'] = escape(status, True)
                del attr['security_classification']

        # Compare list of dicts from Okera and Collibra to ensure sync was successful
        # The table and each of its columns have a dict that contains the assets name
        # and any attributes it has, example:
        # collibra_assets = [
        #   {'name': 'example_table', 'description': 'foobar'},
        #   {'name': 'col1', 'Security Classification': 'Restricted'},
        #   {'name': 'col2'}]
        # okera_assets = [
        #   {'name': 'example_table', 'description': 'foobar'},
        #   {'name': 'col1', 'security classification': 'restricted'},
        #   {'name': 'col2'}]
        for asset in collibra_assets:
            assert asset in okera_assets

# Bidirectional Tests
#
# Reset Collibra and Okera test environment,
# create dataset `transactions` in Okera,
# import `transactions` into domain
@unittest.skipIf(common.TEST_LEVEL != "all", "Skipping at unit test level")
def test_two_way():
    # PyTest isn't using the global value  but the value set from the
    # previous test so it has to be set again here for the test to pass
    EXPORT_CONFIGS['mapped_collibra_attributes'][0]['prioritize_column_attribute'] = False

    ctx = common.get_test_context()
    ctx.enable_token_auth(token_str=TOKEN)

    tbl_full_name = '.'.join([TEST_DB, TRANSACTIONS_TABLE])

    table_desc = "Dataset to test bidirectional sync."

    # Deletes all assets in the given domain
    _cleanup_collibra(TEST_DB)

    with common.get_planner(ctx, host=HOST, port=PORT) as conn:
        # Clean up Okera environment by deleting database
        conn.execute_ddl(DROP_DDL % TEST_DB)
        # Create new database and dataset `transactions` in Okera
        conn.execute_ddl(DB_DDL % TEST_DB)
        conn.execute_ddl(TRANSACTIONS_DDL % (TEST_DB, TRANSACTIONS_TABLE, table_desc))

        # Setup Collibra environment by creating new test assets,
        # returns list of imported assets with asset ID
        _collibra_setup(TEST_DB)

        # Run import script
        okera_collibra.run(IMPORT_CONFIGS, format_assets([tbl_full_name]), PORT)

        # Collect asset information for `transactions`
        collibra_assets = get_collibra_assets(tbl_full_name)
        okera_assets = get_okera_assets(TEST_DB, TRANSACTIONS_TABLE, conn)

        # Compare list of dicts from Okera and Collibra to ensure sync was successful
        # The table and each of its columns have a dict that contains the assets name
        # and any attributes it has, example:
        # collibra_assets = [
        #   {'name': 'example_table', 'description': 'foobar'},
        #   {'name': 'col1', 'Security Classification': 'Restricted'},
        #   {'name': 'col2'}]
        # okera_assets = [
        #   {'name': 'example_table', 'description': 'foobar'},
        #   {'name': 'col1', 'security classification': 'restricted'},
        #   {'name': 'col2'}]
        for asset in collibra_assets:
            assert asset in okera_assets

        # Get the asset IDs of the previously imported table and columns
        # that test attributes will be added to
        table = search_collibra_asset(
            tbl_full_name, get_resource_id(ASSET_IDS, "Table"), "EXACT")
        col1 = search_collibra_asset(
            tbl_full_name + ".address", get_resource_id(ASSET_IDS, "Column"), "EXACT")
        col2 = search_collibra_asset(
            tbl_full_name + ".ipaddress", get_resource_id(ASSET_IDS, "Column"), "EXACT")
        col3 = search_collibra_asset(
            tbl_full_name + ".sales", get_resource_id(ASSET_IDS, "Column"), "EXACT")

        # Adding test attributes for each asset
        add_collibra_attribute(
            table[0]['id'], "Security Classification", "Restricted")
        add_collibra_attribute(
            col1[0]['id'], "Security Classification", "Confidential")
        add_collibra_attribute(
            col2[0]['id'], "Security Classification", "Highly Confidential")
        add_collibra_attribute(col3[0]['id'], "Description", "Number of sales")

        # Run export script
        collibra_okera.run(EXPORT_CONFIGS, format_assets([tbl_full_name]), PORT)

        collibra_asset_attributes = get_collibra_assets(tbl_full_name)
        okera_asset_attributes = get_okera_assets(TEST_DB, TRANSACTIONS_TABLE, conn)

        # Compare list of dicts from Okera and Collibra after attributes have been synced
        for asset in collibra_asset_attributes:
            assert asset in okera_asset_attributes
