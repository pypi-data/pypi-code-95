# pylint: disable=bare-except
# pylint: disable=consider-using-enumerate
# pylint: disable=len-as-condition
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals
# pylint: disable=unidiomatic-typecheck
# pylint: disable=bare-except

import datetime
import json
import math
import os
import random
import statistics
import string
import time
import uuid
import unittest

import pg8000
from prettytable import PrettyTable
import pytest
import pytz

from okera import context, _thrift_api
from okera._thrift_api import TAuthorizeQueryClient
from okera._thrift_api import TAuthorizeQueryParams
from okera._thrift_api import TRequestContext
from okera._thrift_api import TTypeId, TConfigType
from okera._thrift_api import TAttribute

DEFAULT_PRESTO_HOST = os.environ['ODAS_TEST_HOST']
DEFAULT_PRESTO_PORT = os.environ['ODAS_TEST_PORT_PRESTO_COORD_HTTPS']
DEFAULT_REST_SERVER_HOST = os.environ['ODAS_TEST_HOST']
DEFAULT_REST_SERVER_PORT = os.environ['ODAS_TEST_PORT_REST_SERVER']
DEFAULT_ACCESS_PROXY_HOST = os.environ['ODAS_TEST_HOST']
DEFAULT_ACCESS_PROXY_PORT = os.environ['ODAS_TEST_PORT_ACCESS_PROXY']

PERF_DB_HOST = 'okera-psql-aurora.cluster-cyn8yfvyuugz.us-west-2.rds.amazonaws.com'
PERF_DB_USER = 'okera_perf_user'
PERF_DB_DB = 'rpc_perf_db'

TEST_LEVELS = {
    'notests' : 0,
    'smoke' : 1,
    'dev' : 2,
    'checkin' : 3,
    'ci' : 4,
    'all' : 5,
}

TEST_LEVEL = 'smoke'
if 'TEST_LEVEL' in os.environ:
    TEST_LEVEL = os.environ['TEST_LEVEL']
elif 'CEREBRO_TEST_LEVEL' in os.environ:
    TEST_LEVEL = os.environ['CEREBRO_TEST_LEVEL']
ROOT_TOKEN = os.environ['OKERA_HOME'] + '/integration/tokens/cerebro.token'

identity = lambda x: x

def get_env_var(name, coercer, default):
    if name in os.environ:
        return coercer(os.environ[name])
    return default

def get_bool_env_var(name, default):
    return get_env_var(name, lambda x: str(x).lower() in ['true'], default)

# If true, run the perf benchmarks.
RUN_PERF = get_env_var('RUN_PERF', bool, False)
SKIP_PERF_DATA_LOAD = get_env_var('SKIP_PERF_DATA_LOAD', bool, False)
DEFAULT_ITERS = get_env_var('PERF_ITERATIONS', int, 50)
QUIET = get_env_var("PERF_QUIET", bool, False)

def test_level_lt(min_level):
    if TEST_LEVEL not in TEST_LEVELS:
        return False
    return TEST_LEVELS[TEST_LEVEL] < TEST_LEVELS[min_level]

def get_test_context(auth_mech=None, dialect=None, namespace='okera', tz=pytz.utc):
    if auth_mech is None:
        auth_mech = get_env_var('PYCEREBRO_TEST_AUTH_MECH', identity, 'NOSASL')

    ctx = context(dialect=dialect, namespace=namespace, tz=tz)
    if auth_mech == 'NOSASL':
        ctx.disable_auth()
    elif auth_mech == 'TOKEN':
        ctx.enable_token_auth(token_file=ROOT_TOKEN)
    else:
        ctx.disable_auth()
    return ctx

def get_planner(ctx, host=None, port=None, dialect='okera', presto_port=None,
                namespace=None):
    if host is not None:
        host = host
    else:
        host = get_env_var('ODAS_TEST_HOST', identity, 'localhost')

    if port is not None:
        port = port
    else:
        port = get_env_var('ODAS_TEST_PORT_PLANNER_THRIFT', int, 12050)
    if 'presto' in dialect:
        ctx.enable_token_auth(token_str='root')
        return ctx.connect(host=host,
                           port=port,
                           presto_host=host,
                           presto_port=DEFAULT_PRESTO_PORT,
                           namespace=namespace)
    return ctx.connect(host=host, port=port, presto_port=presto_port, namespace=namespace)

def get_worker(ctx, host=None, port=None):
    if host is not None:
        host = host
    else:
        host = get_env_var('ODAS_TEST_HOST', identity, 'localhost')

    if port is not None:
        port = port
    else:
        port = get_env_var('ODAS_TEST_PORT_WORKER_THRIFT', int, 13050)

    return ctx.connect_worker(host=host, port=port)

def get_rest_server_url(scheme='http',
                        host=DEFAULT_REST_SERVER_HOST, port=DEFAULT_REST_SERVER_PORT):
    return "%s://%s:%s" % (scheme, host, port)

def get_access_proxy_url(scheme='http',
                         host=DEFAULT_ACCESS_PROXY_HOST, port=DEFAULT_ACCESS_PROXY_PORT):
    return "%s://%s:%s" % (scheme, host, port)

def measure_latency(iters, fn, msg=None, quiet=False):
    durations = []
    for _ in range(0, iters):
        start = time.time()
        fn()
        durations.append((time.time() - start) * 1000)
    durations = sorted(durations)
    if quiet or QUIET:
        return durations
    if msg:
      print("\n%s\n    Iterations: %s" % (msg, iters))
    else:
      print("\nIterations " + str(iters))
    print("Mean " + str(statistics.mean(durations)) + " ms")
    print("50%: " + str(durations[int(len(durations) * .5)]) + " ms")
    print("90%: " + str(durations[int(len(durations) * .90)]) + " ms")
    print("95%: " + str(durations[int(len(durations) * .95)]) + " ms")
    print("99%: " + str(durations[int(len(durations) * .99)]) + " ms")
    print("99.5%: " + str(durations[int(len(durations) * .995)]) + " ms")
    print("99.9%: " + str(durations[int(len(durations) * .999)]) + " ms")
    return durations

def configure_botocore_patch():
    os.environ['OKERA_PATCH_BOTO'] = 'True'
    os.environ['OKERA_PLANNER_HOST'] = \
        get_env_var('ODAS_TEST_HOST', identity, 'localhost')
    os.environ['OKERA_PLANNER_PORT'] = \
        get_env_var('ODAS_TEST_PORT_PLANNER_THRIFT', identity, 12050)
    from okera import initialize_default_context, check_and_patch_botocore
    initialize_default_context()
    check_and_patch_botocore()

def upsert_config(conn, config_type, key, value):
    """Upsert a configuration.

    config_type : TConfigType
        The type of configurations to return.
    key : str
        The key for this configuration. This must be unique with config_type.
    value : str
        The value for this config.

    Returns
    -------
    bool
        Returns true if the config was updated or false if it was inserted.
    list(str), optional
        List of warnings that were generated as part of this request.
    """
    request = _thrift_api.TConfigUpsertParams()
    request.config_type = config_type
    request.key = key
    if isinstance(value, str):
        request.params = {'value': value}
    else:
        request.params = value
    result = conn.service.client.UpsertConfig(request)
    # TODO: server needs to return if it was an upsert or not
    return True, result.warnings

def delete_config(conn, config_type, key):
    """Upsert a configuration.

    config_type : TConfigType
        The type of configurations to return.
    key : str
        The key for this configuration. This must be unique with config_type.

    Returns
    -------
    bool
        Returns true if the config was deleted.
    list(str), optional
        List of warnings that were generated as part of this request.
    """
    request = _thrift_api.TConfigDeleteParams()
    request.config_type = config_type
    request.key = key
    result = conn.service.client.DeleteConfig(request)
    # TODO: server needs to return if it was deleted or not
    return True, result.warnings

def list_configs(conn, config_type):
    """List configurations of the specified type.

    config_type : TConfigType
        The type of configurations to return.

    Returns
    -------
    map(str, str)
        List of configs as a map of key values.
    """
    table_name = None
    if config_type == TConfigType.AUTOTAGGER_REGEX:
        table_name = "okera_system.tagging_rules"
    elif config_type == TConfigType.SYSTEM_CONFIG:
        table_name = "okera_system.configs"
    else:
        raise ValueError("Invalid config type.")
    return conn.scan_as_json(table_name)

def read_sql_file(path, **kwargs):
    sql = open(path, 'r').read()
    return sql.format(**kwargs)

class PerfResults():
    """
    Utility class for running, storing  and reporing perf results
    """
    def __init__(self):
        self.results = PrettyTable(
          ['rpc', 'name', 'user', 'mean', '50%', '90%', '99%', 'max', 'iters']
        )

    def measure(self, fn, msg, user, rpc, iters=DEFAULT_ITERS):
        """
        Measure and store the latency of fn().
          msg: Name  of test cases
          user: User (typically admin or not, running the function)
          rpc: Name of RPC/API being used.
        """
        if not RUN_PERF:
            return
        label = "%s(%s)" % (msg, user)
        latencies = measure_latency(iters, fn, msg=label)
        mean = "{:.3f}".format(statistics.mean(latencies))
        p50 = "{:.3f}".format(latencies[int(len(latencies) * .5)])
        p90 = "{:.3f}".format(latencies[int(len(latencies) * .9)])
        p99 = "{:.3f}".format(latencies[int(len(latencies) * .99)])
        m = "{:.3f}".format(latencies[-1])
        row = [rpc, msg, user, mean, p50, p90, p99, m, iters]
        self.results.add_row(row)

    def finalize_results(self):
        if not  RUN_PERF:
            return
        print("\nPerf tests done:")
        print(self.results)

        # We want some globals that are the same across python modules so we can
        # correlate the entire run. This can be done by storing a global inside
        # the pytest object.
        globals = {}
        if hasattr(pytest, 'okera_globals'):
            globals = pytest.okera_globals
        else:
            # First time, generate it
            globals['now'] = datetime.datetime.now()
            globals['id'] = uuid.uuid1()
            pytest.okera_globals = globals

        if 'CEREBRO_PERF_DB_PASSWORD' in os.environ:
            self.persist_results(globals)

    def skip_data_load(self):
        return SKIP_PERF_DATA_LOAD

    def run_perf(self):
        return RUN_PERF

    def persist_results(self, globals):
        print("Persisting results to database.")
        id = globals['id']
        now = globals['now']
        build = -1
        version = 'latest'
        owner = ''
        if 'BUILD_NUMBER' in os.environ:
            build = int(os.environ['BUILD_NUMBER'])
        if 'ODAS_DOCKER_VERSION' in os.environ:
            v = os.environ['ODAS_DOCKER_VERSION']
            if 'jenkins' not in v:
                # Jenkins generates latest versions that are unique, ignore
                version = v
        if 'OKERA_BENCHMARK_OWNER' in os.environ:
            owner = os.environ['OKERA_BENCHMARK_OWNER']
        conn = pg8000.connect(host=PERF_DB_HOST,
                            user=PERF_DB_USER,
                            password=os.environ['CEREBRO_PERF_DB_PASSWORD'],
                            database=PERF_DB_DB,
                            ssl=True)
        cur = conn.cursor()
        for row in self.results:
            row.border = False
            row.header = False
            rpc = row.get_string(fields=['rpc']).strip()
            name = row.get_string(fields=['name']).strip()
            user = row.get_string(fields=['user']).strip()
            mean = row.get_string(fields=['mean']).strip()
            p50 = row.get_string(fields=['50%']).strip()
            p90 = row.get_string(fields=['90%']).strip()
            p99 = row.get_string(fields=['99%']).strip()
            max = row.get_string(fields=['max']).strip()
            iters = row.get_string(fields=['iters']).strip()

            values = (id, now, build, version, owner, rpc,
                      name, user, mean, p50, p90, p99, max, iters)
            sql = """INSERT INTO perf_results
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cur.execute(sql, values)
        conn.commit()

class SchemaNode():
  def __init__(self):
      self.col = None
      self.children = []

  @staticmethod
  def convert(cols, idx, schema):
        node = SchemaNode()
        node.col = cols[idx]
        schema.append(node)
        idx += 1
        if node.col.type.num_children:
            for _ in range(0, node.col.type.num_children):
                idx = SchemaNode.convert(cols, idx, node.children)
        return idx

class TmpView():
    def __init__(self, conn, sql):
        self.conn = conn
        # TODO: make this more unique so can be used concurrently
        self.db = "test_tmp_db"
        self.view = "tmp_view"
        self.conn.execute_ddl("CREATE DATABASE IF NOT EXISTS %s" % self.db)
        self.conn.execute_ddl("DROP VIEW IF EXISTS %s.%s" % (self.db, self.view))
        self.conn.execute_ddl("CREATE VIEW %s.%s AS %s" % (self.db, self.view, sql))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.execute_ddl("DROP VIEW IF EXISTS %s.%s" % (self.db, self.view))

    def name(self):
        return '%s.%s' % (self.db, self.view)

class JsonGeneratorNode():
    def __init__(self):
        self.types = []
        self.children = {}

    def to_json(self):
        result = {}
        result['types'] = []
        for t in self.types:
            result['types'].append(TTypeId._VALUES_TO_NAMES[t])
        result['types'] = ', '.join(result['types'])
        if not self.children:
            return result
        for name, child in self.children.items():
            result[name] = child.to_json()
        return result

class JsonGenerator():
    def __init__(self,
                 types=None,
                 record_probabilities=None,
                 array_probabilties=None,
                 null_probability=.1,
                 empty_record_probability=.1,
                 min_fields=1,
                 max_fields=5,
                 max_array_len=3,
                 min_records=2,
                 max_records=10,
                 max_string_len=20,
                 seed=0,
                 max_recursion=5,
                 missing_fields_probability=0,
                 generate_variadic_schema=False,
                 generate_empty_record_all_types=False):
        random.seed(seed)
        if not types:
            types = [[TTypeId.BOOLEAN],
                     [TTypeId.BIGINT],
                     [TTypeId.DOUBLE],
                     [TTypeId.DATE],
                     [TTypeId.TIMESTAMP_NANOS],
                     [TTypeId.STRING]]
            if generate_variadic_schema:
                # This indicates that if this "type" is selected in the schema, the
                # data will be one of these types
                types.append([TTypeId.BIGINT, TTypeId.DOUBLE])
                types.append([TTypeId.BIGINT, TTypeId.DATE])
                types.append([TTypeId.DOUBLE, TTypeId.BOOLEAN])
                types.append([TTypeId.DATE, TTypeId.TIMESTAMP_NANOS])
                types.append([TTypeId.BOOLEAN, TTypeId.BIGINT, TTypeId.DATE,
                              TTypeId.TIMESTAMP_NANOS, TTypeId.DOUBLE, TTypeId.STRING])

        # Probabilities of generating record/array schemas by level. We want to
        # generate them with higher probabilities at the beginning to minimize
        # generating a lot of simple schemas.
        # This generate a CDF (i.e the remaining percentage is used to generate a
        # simple type).
        if not record_probabilities:
            record_probabilities = [.5, .4, .3, .25, .25, .2, .1]
        if not array_probabilties:
            array_probabilities = [.3, .3, .3, .25, .25, .2, .1]

        self.__min_fields = min_fields
        self.__max_fields = max_fields
        self.__min_records = min_records
        self.__max_records = max_records
        self.__max_array_len = max_array_len
        self.__null_probability = null_probability
        self.__max_string_len = max_string_len
        self.__empty_record_probability = empty_record_probability
        self.__max_recursion = max_recursion
        self.__types = types
        self.__array_probabilities = array_probabilities
        self.__record_probabilities = record_probabilities

        # Configs to control schema merge cases
        self.__generate_invalid_schema_merges = False
        self.__generate_empty_record_all_types = generate_empty_record_all_types
        self.__missing_fields_probability = missing_fields_probability

        self.__field_idx = 0
        self.__schema = None

        print("Generating with configuration")
        print("    Seed:  %s" % seed)
        print("    Types:  %s" % self.__types)
        print("    Record Probabilities:  %s" % self.__record_probabilities)
        print("    Array Probabilities:  %s" % self.__array_probabilities)
        print("    Max Array Len: %d" % (self.__max_array_len))
        print("    Max String Len: %d" % (self.__max_string_len))
        print("    Null Probability: %s" % (self.__null_probability))
        print("    Empty Record Probability: %s" % (self.__empty_record_probability))
        print("    Missing Field Probability: %s" % (self.__missing_fields_probability))
        print("    Max Depth: %d" % (self.__max_recursion))
        print("    # Fields: [%d, %d]" % (self.__min_fields, self.__max_fields))
        print("    # Records: [%d, %d]" % (self.__min_records, self.__max_records))
        print("    Generate variadic schemas: %s" % generate_variadic_schema)
        print("    Generate invalid merges: %s" %\
            self.__generate_invalid_schema_merges)
        print("    Generate empty records all types: %s" %\
            self.__generate_empty_record_all_types)

    def new_schema(self):
        self.__field_idx = 0
        self.__schema = self._generate_schema([TTypeId.RECORD], 0)

    def _random_type(self, level):
        prob_record = self.__record_probabilities[\
            min(level, len(self.__record_probabilities) - 1)]
        prob_array = self.__array_probabilities[\
            min(level, len(self.__array_probabilities) - 1)]
        r = random.random()
        if r < prob_record:
            return [TTypeId.RECORD]
        if r < prob_record + prob_array:
            return [TTypeId.ARRAY]
        return random.choice(self.__types)

    def _generate_schema(self, types, level):
        # Recursively generates a test schema
        node = JsonGeneratorNode()
        if level == self.__max_recursion:
            node.types = [TTypeId.STRING]
            return node

        node.types = types
        if types == [TTypeId.RECORD]:
            num_fields = random.randint(self.__min_fields, self.__max_fields - 1)
            for idx in range(0, num_fields):
                t = self._random_type(level)
                if level == 0:
                    name = 'c' + str(idx)
                else:
                    name = 'f' + str(self.__field_idx)
                    self.__field_idx += 1
                node.children[name] = self._generate_schema(t, level + 1)
        elif types == [TTypeId.ARRAY]:
            t = self._random_type(level)
            node.children['item'] = self._generate_schema(t, level + 1)
        return node

    def __generate_random_data(self, schema):
        if random.random() < self.__null_probability:
            return None
        t = random.choice(schema.types)
        if self.__generate_empty_record_all_types or t == TTypeId.RECORD:
            if random.random() < self.__empty_record_probability:
                return {}

        if t == TTypeId.BIGINT:
            digits = random.random() * 10
            v = int(pow(10, digits) * random.random())
            if random.random() < .1:
                return -v
            return v
        if t == TTypeId.DOUBLE:
            digits = random.random() * 10
            v = pow(10, digits) * random.random()
            if random.random() < .1:
                return -v
            return v
        if t == TTypeId.BOOLEAN:
            if random.random() > 0.5:
                return True
            return False
        if t == TTypeId.DATE:
            return '2020-01-01'
        if t == TTypeId.TIMESTAMP_NANOS:
            return '2020-01-01 01:02:03.123'
        if t == TTypeId.STRING:
            n = random.randint(0, self.__max_string_len - 1)
            return ''.join(random.choice(string.ascii_lowercase) for i in range(n))
        if t == TTypeId.RECORD:
            return self.__generate_record(schema)
        if t == TTypeId.ARRAY:
            return self.__generate_array(schema.children['item'])
        return 'Unsupported Type %s' % t

    def __generate_array(self, schema):
        result = []
        num_children = random.randint(0, self.__max_array_len - 1)
        for _ in range(0, num_children):
            result.append(self.__generate_random_data(schema))
        return result

    def __generate_record(self, schema):
        record = {}
        for name, child in schema.children.items():
            if random.random() < self.__missing_fields_probability:
                continue
            record[name] = self.__generate_random_data(child)
        return record

    def generate(self, generate_record_idx=False):
        n = self.__min_records
        if self.__min_records != self.__max_records:
            n = random.randint(self.__min_records, self.__max_records - 1)
        data = []
        for idx in range(0, n):
            r = self.__generate_record(self.__schema)
            if generate_record_idx:
                r['idx'] = idx
            data.append(r)
        return data

class TestBase(unittest.TestCase):
    """ Base class with some common test utilities. """
    @staticmethod
    def _ddl_count(conn, sql):
        return len(conn.execute_ddl(sql))

    @staticmethod
    def _recreate_test_role(conn, role, users):
        conn.execute_ddl("DROP ROLE IF EXISTS %s" % role)
        conn.execute_ddl("CREATE ROLE %s" % role)
        for user in users:
            conn.execute_ddl("GRANT ROLE %s TO GROUP %s" % (role, user))

    @staticmethod
    def _recreate_test_db(conn, db):
        conn.execute_ddl("DROP DATABASE IF EXISTS %s CASCADE" % db)
        conn.execute_ddl("CREATE DATABASE %s" % db)

    @staticmethod
    def _create_all_types(conn, db, include_date=False):
        ddl = '''
            CREATE EXTERNAL TABLE %s.alltypes(
              bool_col BOOLEAN,
              tinyint_col TINYINT,
              smallint_col SMALLINT,
              int_col INT,
              bigint_col BIGINT,
              float_col FLOAT,
              double_col DOUBLE,
              string_col STRING,
              varchar_col VARCHAR(10),
              char_col CHAR(5),
        '''
        if include_date:
            ddl += 'date_col DATE,\n'
        ddl += '''
              timestamp_col TIMESTAMP,
              decimal_col decimal(24, 10)
            )
            ROW FORMAT DELIMITED FIELDS TERMINATED BY '|'
            STORED AS TEXTFILE
            LOCATION 's3://cerebrodata-test/alltypes/'
        '''
        conn.execute_ddl(ddl % db)

    @staticmethod
    def _get_t_attribute_obj(namespace, key):
        attribute = TAttribute()
        attribute.attribute_namespace = namespace
        attribute.key = key
        return attribute

    @staticmethod
    def _tag_all_columns(conn, db, dataset, ns, key, create_tag=False):
        if create_tag:
            conn.delete_attribute(ns, key)
            conn.create_attribute(ns, key)
        ds = conn.list_datasets(db, name=dataset)[0]
        for col in ds.schema.cols:
            if col.name:
                conn.assign_attribute(ns, key, db, dataset, col.name)

    @staticmethod
    def get_random_leaf_column(conn, db, tbl):
        """ Returns a random path to a leaf col in this table."""
        tbl = conn.list_datasets(db, name=tbl)[0]
        schema = TestBase.convert_schema(tbl.schema.cols)
        result = ''
        flattened = ''
        while schema:
            col = random.choice(schema)
            if col.col.name:
                if result:
                    result += '.'
                if flattened:
                    flattened += '__'
                result += col.col.name.lower()
                flattened += col.col.name.lower()
            # else:
            #     if flattened:
            #         flattened += '__'
            #     flattened += 'item'
            schema = col.children
        return result, flattened

    @staticmethod
    def convert_schema(cols):
        """ Converts a flattened inorder schema list to a tree """
        schema = []
        idx = 0
        while idx < len(cols):
            idx = SchemaNode.convert(cols, idx, schema)
        return schema

    @staticmethod
    def _visible_cols(cols):
        result = []
        for c in cols:
            if c.hidden:
                continue
            result.append(c)
        return result

    @staticmethod
    def _top_level_columns(cols):
        total_children = 0
        for c in cols:
            if c.type.num_children:
                total_children += c.type.num_children
        return len(cols) - total_children

    @staticmethod
    def collect_column_attributes(ds):
        result = {}
        for col in ds.schema.cols:
            if not col.attribute_values:
                continue
            for v in col.attribute_values:
                key = v.database
                if v.table:
                    key += '.' + v.table
                    if v.column:
                        key += '.' + v.column
                if key not in result:
                    result[key] = []
                result[key].append(
                    v.attribute.attribute_namespace + '.' + v.attribute.key)
        for _, v in result.items():
            v.sort()
        return result


    @staticmethod
    def _try_parse_datetime(v):
        if not isinstance(v, str):
            return None

        FORMATS = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d',
        ]

        for fmt in FORMATS:
            try:
                return datetime.datetime.strptime(v, fmt)
            except ValueError:
                pass
        return None

    @staticmethod
    def _is_float(v):
        if v is None:
            return False
        try:
            float(v)
            return True
        except:
            return False

    @staticmethod
    def _equals(v1, v2):
        if TestBase._is_float(v1) and TestBase._is_float(v2):
            v1 = float(v1)
            v2 = float(v2)

        if isinstance(v1, float) and isinstance(v2, float):
            return v1 == v2 or (math.isnan(v1) and math.isnan(v2)) \
                or abs(v1 - v2) < .0001
        if v1 != v2:
            # Try as datetime with different formats
            d1 = TestBase._try_parse_datetime(v1)
            d2 = TestBase._try_parse_datetime(v2)
            if d1 is not None and d1 == d2:
                return True
            print("Values do not match. %s != %s" % (v1, v2))
            print("Types: %s != %s" % (type(v1), type(v2)))
        return v1 == v2

    @staticmethod
    def _is_empty_dictionary(v):
        """ Checks if v is None or a dictionary (recursively) of None values """
        if v is None:
            return True
        if type(v) != dict:
            return False
        for _, val in v.items():
            if not TestBase._is_empty_dictionary(val):
                return False
        return True

    @staticmethod
    def __deep_compare(actual, expected, allow_missing, empty_struct_equals_null,
                       required_type, empty_array_equals_null, zero_equals_none):
        if empty_struct_equals_null:
            if type(actual) == dict and (expected is None or len(expected) == 0):
                # We don't support nullable structs, so instead every field in the
                # struct is None
                for k, v in actual.items():
                    if not TestBase._is_empty_dictionary(v):
                        print("actual has a non-null struct. Expecting null.")
                        return False
                return True
            if type(expected) == dict and len(expected) == 0 and actual is None:
                # Allow empty struct to be considered equal to null. A struct with no
                # fields is otherwise not possible.
                return True

        # For parquet file format, the actual is empty for an empty list.
        if empty_array_equals_null:
            if type(expected) == list and (actual is None):
                return True

        # As we are strongly typed, we will convert the types to the "bigger" type for
        # schema merge cases.
        if type(actual) == str and type(expected) in [int, float]:
            expected = str(expected)
        if type(actual) == str and type(expected) == bool:
            if expected:
                expected = "true"
            else:
                expected = "false"
        if type(actual) == float and type(expected) == int:
            expected = float(expected)

        if type(actual) != type(expected):
            if type(actual) == list and type(expected) == dict:
                # Can't tell difference between empty list and empty dict
                if not actual and not expected:
                    return True
            # Handle some schema merge cases that are ambiguous with empty records
            if type(actual) == dict and not actual and \
                    type(expected) in [bool, float, int]:
                return True
            if type(actual) in [bool, float, int] and type(expected) == dict \
                    and not expected:
                return True
            if type(actual) == float and math.isnan(actual) and expected is None:
                return True
            if actual == "" and expected is None and zero_equals_none:
                return True
            if type(actual) == type(None) and type(expected) in [float, int]:
                if zero_equals_none and expected in [0, 0.0]:
                    return True
            if required_type and type(expected) in [bool, float, int, str]:
                if type(expected) != required_type:
                    # The required type doesn't match so the expected should be None
                    if actual is not None and \
                            not TestBase._equals(actual, required_type(expected)):
                        print("Expecting actual to be None. %s, %s" % (actual, expected))
                        return False
                    return True
            print("Types don't match %s != %s" % (type(actual), type(expected)))
            print("%s != %s" % (actual, expected))
            return False

        if type(actual) == dict:
            for k, v in actual.items():
                # Handle the case where some field that exists in the Okera version
                # but is null might not exist in the raw file version, but only if
                # allow_missing is set
                if k in expected:
                    if not TestBase.__deep_compare(
                            v, expected[k], allow_missing,
                            empty_struct_equals_null, required_type,
                            empty_array_equals_null, zero_equals_none):
                        print("Key %s from expected is not in actual." % k)
                        print("%s != %s" % (v, expected[k]))
                        return False
                elif k not in expected and not \
                        (TestBase._is_empty_dictionary(v) and allow_missing):
                    print("Key %s from actual is not in expected." % k)
                    return False
            for k, v in expected.items():
                if k not in actual and not allow_missing:
                    print("Key %s from expected is not in actual." % k)
                    return False
        elif type(actual) == list:
            if len(actual) != len(expected):
                print("Length of arrays are not equal. %s != %s" % \
                      (len(actual), len(expected)))
                return False
            for idx in range(len(actual)):
                if not TestBase.__deep_compare(
                        actual[idx], expected[idx], allow_missing,
                        empty_struct_equals_null, required_type,
                        empty_array_equals_null, zero_equals_none):
                    print("List elements don't match at idx %s. %s != %s" % \
                          (idx, actual[idx], expected[idx]))
                    return False
        else:
            return TestBase._equals(actual, expected)

        return True

    @staticmethod
    def _lower_keys(x):
        if isinstance(x, list):
            return [TestBase._lower_keys(v) for v in x]
        if isinstance(x, dict):
            return dict((k.lower(), TestBase._lower_keys(v)) for k, v in x.items())
        return x

    @staticmethod
    def compare_json(asserter, actual, expected, allow_missing, empty_struct_equals_null,
                     batch_mode, required_type, empty_array_equals_null,
                     zero_equals_none=False):
        actual = TestBase._lower_keys(actual)
        expected = TestBase._lower_keys(expected)

        if batch_mode and len(actual) != len(expected):
            print("Failure: Lengths did not match %s != %s" % \
                (len(actual), len(expected)))
            return False
        asserter.assertEqual(len(actual), len(expected))

        for idx in range(len(actual)):
            obj1 = actual[idx]
            obj2 = expected[idx]

            if TestBase.__deep_compare(
                    obj1, obj2, allow_missing, empty_struct_equals_null,
                    required_type, empty_array_equals_null, zero_equals_none):
                continue
            if batch_mode:
                return False
            print("EXPECTED:\n%s" % json.dumps(expected, indent=2, sort_keys=True))
            print("\nACTUAL:\n%s" % json.dumps(actual, indent=2, sort_keys=True))
            asserter.assertEqual(json.dumps(actual, indent=2, sort_keys=True),
                                 json.dumps(expected, indent=2, sort_keys=True))
        return True

    def authorize_query(self, conn, query, user=None, use_tmp_tables=False, client=None,
                        return_full_result=False, cte=False, token=None):
        request = TAuthorizeQueryParams()
        request.sql = query
        request.requesting_user = user
        request.use_session_local_tables = use_tmp_tables
        request.client = client
        request.cte_rewrite = cte
        if token:
            request.ctx = TRequestContext()
            request.ctx.auth_token = token

        result = conn.service.client.AuthorizeQuery(request)
        if client == TAuthorizeQueryClient.TEST_ACK:
            return ''
        if return_full_result:
            return ' '.join(result.result_sql.split())
        self.assertTrue(result.table is None)
        if result.requires_worker:
            return None
        self.assertTrue(result.result_schema is not None or cte)
        return ' '.join(result.result_sql.split())


def random_string(length):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))
