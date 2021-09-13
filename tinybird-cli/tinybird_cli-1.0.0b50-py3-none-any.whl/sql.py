import re
import string


def as_subquery(sql):
    return f'''(\n{sql}\n)'''


def get_format(q):
    """
    retrieves FORMAT from CH sql
    >>> get_format('select * from test')
    >>> get_format('select * from test formAt JSON')
    'JSON'
    """
    FORMAT_RE = r'\s+format\s+(\w+)\s*$'
    q = q.strip()
    format = re.findall(FORMAT_RE, q, re.I)
    return format[0] if format else None


def remove_format(q):
    """
    removes FORMAT from CH sql
    >>> remove_format('select * from test')
    'select * from test'
    >>> remove_format('select * from test formAt JSON')
    'select * from test'
    """
    FORMAT_RE = r'\s+(format)\s+(\w+)\s*$'
    q = q.strip()
    return re.sub(FORMAT_RE, '', q, flags=re.I)


def col_name(name, backquotes=True):
    """
    >>> col_name('`test`', True)
    '`test`'
    >>> col_name('`test`', False)
    'test'
    >>> col_name('test', True)
    '`test`'
    >>> col_name('test', False)
    'test'
    >>> col_name('', True)
    ''
    >>> col_name('', False)
    ''
    """
    if not name:
        return name
    if name[0] == '`' and name[-1] == '`':
        return name if backquotes else name[1:-1]
    return f"`{name}`" if backquotes else name


def schema_to_sql_columns(schema):
    """ return an array with each column in SQL
    >>> schema_to_sql_columns([{'name': 'temperature', 'type': 'Float32', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'temperature'}, {'name': 'temperature_delta', 'type': 'Float32', 'codec': 'CODEC(Delta(4), LZ4))', 'default_value': 'MATERIALIZED temperature', 'nullable': False, 'normalized_name': 'temperature_delta'}])
    ['`temperature` Float32', '`temperature_delta` Float32 MATERIALIZED temperature CODEC(Delta(4), LZ4))']
    >>> schema_to_sql_columns([{'name': 'temperature_delta', 'type': 'Float32', 'codec': '', 'default_value': 'MATERIALIZED temperature', 'nullable': False, 'normalized_name': 'temperature_delta'}])
    ['`temperature_delta` Float32 MATERIALIZED temperature']
    >>> schema_to_sql_columns([{'name': 'temperature_delta', 'type': 'Float32', 'codec': 'CODEC(Delta(4), LZ4))', 'default_value': '', 'nullable': False, 'normalized_name': 'temperature_delta'}])
    ['`temperature_delta` Float32 CODEC(Delta(4), LZ4))']
    >>> schema_to_sql_columns([{'name': 'temperature_delta', 'type': 'Float32', 'nullable': False, 'normalized_name': 'temperature_delta'}])
    ['`temperature_delta` Float32']
    """
    columns = []
    for x in schema:
        name = x['normalized_name'] if 'normalized_name' in x else x['name']
        _type = ("Nullable(%s)" if x['nullable'] else '%s') % x['type']
        parts = [col_name(name, backquotes=True), _type]
        if 'default_value' in x and x['default_value'] not in ('', None):
            parts.append(x['default_value'])
        if 'codec' in x and x['codec'] not in ('', None):
            parts.append(x['codec'])
        c = ' '.join([x for x in parts if x]).strip()
        columns.append(c)
    return columns


def mark_error_string(s, i, context=20, line=0):
    """
    >>> mark_error_string('0123456789', 0, 4)
    '01234\\n^---'
    >>> mark_error_string('0123456789', 9, 4)
    '456789\\n     ^---'
    >>> mark_error_string('01234\\n56789', 1)
    '01234\\n ^---'
    """
    marker = '^---'
    ss = s.splitlines()[line]
    start = max(0, i - context - 1)
    end = min(len(ss), i + context + 1)
    return ss[start:end] + "\n" + (" " * (i - start)) + marker


def format_parse_error(table_structure, i, position, hint=None, line=0):
    message = f"{hint}\n" if hint else ""
    position -= 1
    message += mark_error_string(table_structure, position, line=line)
    message += f" found '{table_structure[i]}' at position {position}"
    return message


def parse_table_structure(table_structure):  # noqa: C901
    """This parses the SQL schema for a CREATE TABLE
    Columns follow the syntax: name1 [type1] [DEFAULT|MATERIALIZED|ALIAS expr1] [compression_codec] [TTL expr1][,]
    Reference: https://clickhouse.tech/docs/en/sql-reference/statements/create/table/#syntax-forms

    >>> parse_table_structure('c Float32, b String')
    [{'name': 'c', 'type': 'Float32', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'c'}, {'name': 'b', 'type': 'String', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'b'}]

    >>> parse_table_structure('c Nullable(Float32)')
    [{'name': 'c', 'type': 'Float32', 'codec': None, 'default_value': None, 'nullable': True, 'normalized_name': 'c'}]

    >>> parse_table_structure('c Nullable(Float32) DEFAULT NULL')
    [{'name': 'c', 'type': 'Float32', 'codec': None, 'default_value': None, 'nullable': True, 'normalized_name': 'c'}]

    >>> parse_table_structure("c String DEFAULT 'bla'")
    [{'name': 'c', 'type': 'String', 'codec': None, 'default_value': "DEFAULT 'bla'", 'nullable': False, 'normalized_name': 'c'}]

    >>> parse_table_structure('`foo.bar` UInt64')
    [{'name': 'foo.bar', 'type': 'UInt64', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'foo.bar'}]

    >>> parse_table_structure('double_value Float64 CODEC(LZ4HC(2))')
    [{'name': 'double_value', 'type': 'Float64', 'codec': 'CODEC(LZ4HC(2))', 'default_value': None, 'nullable': False, 'normalized_name': 'double_value'}]
    >>> parse_table_structure('doubl/e_value Float64 CODEC(LZ4HC(2))')
    Traceback (most recent call last):
    ...
    ValueError: wrong value
    doubl/e_value Float64 CODE
         ^--- found '/' at position 5
    >>> parse_table_structure('`c` nullable(Float32)')
    [{'name': 'c', 'type': 'Float32', 'codec': None, 'default_value': None, 'nullable': True, 'normalized_name': 'c'}]
    >>> parse_table_structure('c Float32 b String')
    Traceback (most recent call last):
    ...
    ValueError: DEFAULT|MATERIALIZED|ALIAS|CODEC or comma (,) expected
    c Float32 b String
              ^--- found 'b' at position 10
    >>> parse_table_structure('c Int32 CODEC(Delta, LZ4)\\n')
    [{'name': 'c', 'type': 'Int32', 'codec': 'CODEC(Delta, LZ4)', 'default_value': None, 'nullable': False, 'normalized_name': 'c'}]
    >>> parse_table_structure('c  SimpleAggregateFunction(sum, Int32),\\np SimpleAggregateFunction(sum, Int32)')
    [{'name': 'c', 'type': 'SimpleAggregateFunction(sum, Int32)', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'c'}, {'name': 'p', 'type': 'SimpleAggregateFunction(sum, Int32)', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'p'}]
    >>> parse_table_structure('c Int32 CODEC(Delta, LZ4) Materialized b*2\\n')
    Traceback (most recent call last):
    ...
    ValueError: Unexpected DEFAULT|MATERIALIZED|ALIAS after CODEC
    32 CODEC(Delta, LZ4) Materialized b*2
                         ^--- found 'M' at position 26
    >>> parse_table_structure('c Int32 CODEC(Delta, LZ4) Materialized ifNull(b*2, 0)\\n')
    Traceback (most recent call last):
    ...
    ValueError: Unexpected DEFAULT|MATERIALIZED|ALIAS after CODEC
    32 CODEC(Delta, LZ4) Materialized ifNull(b
                         ^--- found 'M' at position 26
    >>> parse_table_structure('c Int32 Materialized b*2\\n')
    [{'name': 'c', 'type': 'Int32', 'codec': None, 'default_value': 'MATERIALIZED b*2', 'nullable': False, 'normalized_name': 'c'}]
    >>> parse_table_structure('c Int32 Materialized b != 1 ? b*2: pow(b, 3)\\n')
    [{'name': 'c', 'type': 'Int32', 'codec': None, 'default_value': 'MATERIALIZED b != 1 ? b*2: pow(b, 3)', 'nullable': False, 'normalized_name': 'c'}]
    >>> parse_table_structure('')
    []
    >>> parse_table_structure('`date` Date,`timezone` String,`offset` Int32')
    [{'name': 'date', 'type': 'Date', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'date'}, {'name': 'timezone', 'type': 'String', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'timezone'}, {'name': 'offset', 'type': 'Int32', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'offset'}]
    >>> parse_table_structure('c Int32 Materialized b*2 CODEC(Delta, LZ4)\\n')
    [{'name': 'c', 'type': 'Int32', 'codec': 'CODEC(Delta, LZ4)', 'default_value': 'MATERIALIZED b*2', 'nullable': False, 'normalized_name': 'c'}]
    >>> parse_table_structure('c Int32 Materialized ifNull(b*2, 0) CODEC(Delta, LZ4)\\n')
    [{'name': 'c', 'type': 'Int32', 'codec': 'CODEC(Delta, LZ4)', 'default_value': 'MATERIALIZED ifNull(b*2, 0)', 'nullable': False, 'normalized_name': 'c'}]
    >>> parse_table_structure('`temperature_delta` Float32 MATERIALIZED temperature CODEC(Delta(4), LZ4)')
    [{'name': 'temperature_delta', 'type': 'Float32', 'codec': 'CODEC(Delta(4), LZ4)', 'default_value': 'MATERIALIZED temperature', 'nullable': False, 'normalized_name': 'temperature_delta'}]
    >>> parse_table_structure('foo^bar Float32')
    Traceback (most recent call last):
    ...
    ValueError: wrong value
    foo^bar Float32
       ^--- found '^' at position 3
    >>> parse_table_structure('foo Float#32')
    Traceback (most recent call last):
    ...
    ValueError: wrong value
    foo Float#32
             ^--- found '#' at position 9
    >>> parse_table_structure('foo Float32 DEFAULT 13, bar UInt64')
    [{'name': 'foo', 'type': 'Float32', 'codec': None, 'default_value': 'DEFAULT 13', 'nullable': False, 'normalized_name': 'foo'}, {'name': 'bar', 'type': 'UInt64', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'bar'}]
    >>> parse_table_structure('foo Float32 DEFAULT 1$$$3')
    Traceback (most recent call last):
    ...
    ValueError: wrong value
    foo Float32 DEFAULT 1$$$3
                         ^--- found '$' at position 21
    >>> parse_table_structure('foo Float32 CODEC(Delta(4), LZ#4)')
    Traceback (most recent call last):
    ...
    ValueError: wrong value
    32 CODEC(Delta(4), LZ#4)
                         ^--- found '#' at position 30
    >>> parse_table_structure('\\n    `temperature` Float32,\\n    `temperature_delta` Float32 MATERIALIZED temperature CODEC(Delta(4), LZ4))\\n    ')
    [{'name': 'temperature', 'type': 'Float32', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'temperature'}, {'name': 'temperature_delta', 'type': 'Float32', 'codec': 'CODEC(Delta(4), LZ4))', 'default_value': 'MATERIALIZED temperature', 'nullable': False, 'normalized_name': 'temperature_delta'}]
    >>> parse_table_structure('temperature Float32, temperature_delta Float32 MATERIALIZED temperature Codec(Delta(4)), temperature_doubledelta Float32 MATERIALIZED temperature Codec(DoubleDelta), temperature_doubledelta_lz4 Float32 MATERIALIZED temperature Codec(DoubleDelta, LZ4)')
    [{'name': 'temperature', 'type': 'Float32', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'temperature'}, {'name': 'temperature_delta', 'type': 'Float32', 'codec': 'Codec(Delta(4))', 'default_value': 'MATERIALIZED temperature', 'nullable': False, 'normalized_name': 'temperature_delta'}, {'name': 'temperature_doubledelta', 'type': 'Float32', 'codec': 'Codec(DoubleDelta)', 'default_value': 'MATERIALIZED temperature', 'nullable': False, 'normalized_name': 'temperature_doubledelta'}, {'name': 'temperature_doubledelta_lz4', 'type': 'Float32', 'codec': 'Codec(DoubleDelta, LZ4)', 'default_value': 'MATERIALIZED temperature', 'nullable': False, 'normalized_name': 'temperature_doubledelta_lz4'}]
    >>> parse_table_structure('t UInt8  CODEC(Delta(1), LZ4)')
    [{'name': 't', 'type': 'UInt8', 'codec': 'CODEC(Delta(1), LZ4)', 'default_value': None, 'nullable': False, 'normalized_name': 't'}]
    >>> parse_table_structure('tt UInt8  MATERIALIZED t')
    [{'name': 'tt', 'type': 'UInt8', 'codec': None, 'default_value': 'MATERIALIZED t', 'nullable': False, 'normalized_name': 'tt'}]
    >>> parse_table_structure('tt UInt8  MATERIALIZED t  CODEC(Delta(1), LZ4)')
    [{'name': 'tt', 'type': 'UInt8', 'codec': 'CODEC(Delta(1), LZ4)', 'default_value': 'MATERIALIZED t', 'nullable': False, 'normalized_name': 'tt'}]
    >>> parse_table_structure('tt SimpleAggregateFunction(any, Nullable(UInt8))')
    [{'name': 'tt', 'type': 'SimpleAggregateFunction(any, Nullable(UInt8))', 'codec': None, 'default_value': None, 'nullable': False, 'normalized_name': 'tt'}]
    >>> parse_table_structure("timestamp DateTime MATERIALIZED toDateTime(JSONExtractInt(JSONExtractRaw(record, 'payload'), 'timestamp') / 1000)")
    [{'name': 'timestamp', 'type': 'DateTime', 'codec': None, 'default_value': "MATERIALIZED toDateTime(JSONExtractInt(JSONExtractRaw(record, 'payload'), 'timestamp') / 1000)", 'nullable': False, 'normalized_name': 'timestamp'}]
    """
    # ' ',^' ', ' '|','
    LSTRIP, NAME, TYPE, CODEC, DEFAULT_VALUE = 1, 2, 3, 4, 5
    # FINISH = 6
    mode = LSTRIP
    name = ''
    _type = ''
    codec = ''
    default_value = ''
    columns = []
    valid_chars = string.ascii_letters + string.digits + '._`*<>+-\''
    valid_chars_fn = valid_chars + "(), =!?:/\n"
    parenthesis = 0

    def eof(i):
        return i == len(table_structure)

    def col(name, type, codec, default_value):
        return dict(name=col_name(name.strip(), backquotes=False),
                    type=type.strip(),
                    codec=codec.strip(),
                    default_value=default_value.strip())

    line = 0
    pos = 0
    for i, c in enumerate(table_structure):
        pos += 1
        if c == '\n':
            line += 1
            pos = 0
        if c == '(':
            parenthesis += 1
        if c == ')':
            parenthesis -= 1

        if mode == LSTRIP and c not in ' \n':
            mode = NAME
            name += c

        elif mode == NAME:
            if c in ' \n':
                mode = TYPE
            elif c not in valid_chars:
                raise ValueError(format_parse_error(
                    table_structure, i, pos, "wrong value", line=line))
            else:
                name += c

        elif mode == TYPE:
            if c in ' \n' and parenthesis == 0 and _type != '':
                if _type.lower() != 'nested':
                    mode = DEFAULT_VALUE
            elif (c in ',' or eof(i)) and parenthesis == 0:
                columns.append(col(name, _type, codec, default_value=''))
                name, _type, codec, default_value, mode = '', '', '', '', LSTRIP
            elif c not in valid_chars_fn:
                raise ValueError(format_parse_error(
                    table_structure, i, pos, "wrong value", line=line))
            else:
                _type += c

        elif mode == DEFAULT_VALUE:
            if c in ' \n' and parenthesis == 0 and default_value != '':
                if table_structure[i + 1:i + 1 + 5].lower() == 'codec':
                    mode = CODEC
            if (c in ',' or eof(i)) and parenthesis == 0:
                columns.append(col(name, _type, codec, default_value))
                name, _type, codec, default_value, mode = '', '', '', '', LSTRIP
            elif c not in valid_chars_fn:
                raise ValueError(format_parse_error(
                    table_structure, i, pos, "wrong value", line=line))
            else:
                if default_value == '':
                    if c not in 'cCmMdDaA \n':
                        raise ValueError(format_parse_error(
                            table_structure, i, pos, "DEFAULT|MATERIALIZED|ALIAS|CODEC or comma (,) expected", line=line))
                    if codec != '':
                        raise ValueError(format_parse_error(table_structure, i, pos, "Unexpected DEFAULT|MATERIALIZED|ALIAS after CODEC", line=line))
                if c in ' \n' and default_value == '':
                    continue
                default_value += c

            default_value = default_value.upper() \
                if default_value.upper() in ('DEFAULT', 'MATERIALIZED', 'ALIAS', 'CODEC') else default_value
            if default_value[:5].lower() == 'codec':
                mode = CODEC
                codec = default_value
                default_value = ''

        elif mode == CODEC:
            if c in ' \n' and parenthesis == 0 and codec != '':
                mode = DEFAULT_VALUE
            if (c in ',' or eof(i)) and parenthesis == 0:
                columns.append(col(name, _type, codec, default_value))
                name, _type, codec, default_value, mode = '', '', '', '', LSTRIP
            elif c not in valid_chars_fn:
                raise ValueError(format_parse_error(table_structure, i, pos, "wrong value", line=line))
            else:
                codec += c

    if name:
        columns.append(col(name, _type, codec, default_value))

    # normalize columns
    for column in columns:
        nullable = column['type'].lower().startswith('nullable')
        column['type'] = column['type'] if not nullable else column['type'][len('Nullable('):-1]  # ')'
        column['nullable'] = nullable
        column['codec'] = column['codec'] if column['codec'] else None
        column['name'] = column['name']
        column['normalized_name'] = column['name']
        default_value = column['default_value'] if column['default_value'] else None
        if nullable and default_value and default_value.lower() == 'default null':
            default_value = None
        column['default_value'] = default_value

    return columns


def alter_table_operations(schema_a, schema_b):

    operations = []
    operations_quarantine = []

    def columns_signature(schema):
        columns = parse_table_structure(schema)
        columns_dict = {c['normalized_name']: (i, c) for i, c in enumerate(columns)}
        columns_signature = [tuple([c['normalized_name']] + list(zip(c.keys(), c.values()))) for c in columns]
        return columns_dict, columns_signature

    columns_a, signature_a = columns_signature(schema_a)
    columns_b, signature_b = columns_signature(schema_b)

    dropped_modified_columns = set(signature_a) - set(signature_b)
    for c, *_c_args in dropped_modified_columns:
        if c in columns_b:
            current_column = schema_to_sql_columns([columns_a[c][1]])[0]
            modified_column = schema_to_sql_columns([columns_b[c][1]])[0]
            raise ValueError(f"Modifying the '{c}' column is not supported. Changing from '{current_column}' to '{modified_column}'")
        else:
            raise ValueError(f"Dropping the '{c}' column is not supported")

    new_columns = []
    added_columns = set(signature_b) - set(signature_a)
    for c, *_c_args in added_columns:
        position, column = columns_b[c]
        if position < len(columns_a):
            raise ValueError(f"Could not add column '{c}' at position {position + 1}, new columns must be added at the end of the table")
        new_column = schema_to_sql_columns([column])[0]
        new_column_quarantine = schema_to_sql_columns([{
            'name': column['name'],
            'normalized_name': column['normalized_name'],
            'type': 'String',
            'nullable': True,
            'default_value': None,
            'codec': None
        }])[0]
        new_columns.append((position, new_column, new_column_quarantine))

    for _position, new_column, new_column_quarantine in sorted(new_columns):
        operations.append(f"ADD COLUMN {new_column}")
        operations_quarantine.append(f"ADD COLUMN {new_column_quarantine}")

    return operations, operations_quarantine


def engine_can_be_replicated(engine):
    """
    >>> engine_can_be_replicated('MergeTree() order by tuple()')
    True
    >>> engine_can_be_replicated('JOIN(ANY, LEFT, foo)')
    False
    >>> engine_can_be_replicated('ReplicatingMergeTree() order by tuple()')
    True
    >>> engine_can_be_replicated(None)
    False
    """
    if not engine:
        return False
    return 'mergetree' in engine.lower()


def engine_supports_delete(engine):
    """
    >>> engine_supports_delete('MergeTree() order by tuple()')
    True
    >>> engine_supports_delete('JOIN(ANY, LEFT, foo)')
    False
    >>> engine_supports_delete('ReplicatingMergeTree() order by tuple()')
    True
    >>> engine_supports_delete(None)
    False
    """
    if not engine:
        return False
    return 'mergetree' in engine.lower()


def engine_replicated_to_local(engine):
    """
    >>> engine_replicated_to_local("ReplicatedMergeTree('/clickhouse/tables/{layer}-{shard}/test.foo','{replica}') order by (test)")
    'MergeTree() order by (test)'
    >>> engine_replicated_to_local("ReplicatedReplacingMergeTree('/clickhouse/tables/{layer}-{shard}/test.foo', '{replica}', timestamp) order by (test)")
    'ReplacingMergeTree(timestamp) order by (test)'
    >>> engine_replicated_to_local("Join(ANY, LEFT, test)")
    'Join(ANY, LEFT, test)'
    >>> engine_replicated_to_local("ReplicatedVersionedCollapsingMergeTree('/clickhouse/tables/{layer}-{shard}/test.foo', '{replica}', sign,version) ORDER BY pk TTL toDate(local_timeplaced) + toIntervalDay(3) SETTINGS index_granularity = 8192")
    'VersionedCollapsingMergeTree(sign, version) ORDER BY pk TTL toDate(local_timeplaced) + toIntervalDay(3) SETTINGS index_granularity = 8192'
    """
    def _replace(m):
        parts = m.groups()
        s = parts[0] + "MergeTree("
        if parts[1]:
            tk = parts[1].split(',')
            if len(tk) > 2:  # remove key and {replica} part
                s += ', '.join([x.strip() for x in tk[2:]])
        s += ")" + parts[2]
        return s

    if 'Replicated' not in engine:
        return engine

    return re.sub(r"Replicated(.*)MergeTree\(([^\)]*)\)(.*)",
                  _replace,
                  engine.strip()
                  )


def engine_local_to_replicated(engine, database, name):
    """
    transforms a engine definition to a replicated one

    >>> engine_local_to_replicated('MergeTree() order by (test)', 'test', 'foo')
    "ReplicatedMergeTree('/clickhouse/tables/{layer}-{shard}/test.foo','{replica}') order by (test)"
    >>> engine_local_to_replicated('MergeTree order by (test)', 'test', 'foo')
    "ReplicatedMergeTree('/clickhouse/tables/{layer}-{shard}/test.foo','{replica}') order by (test)"
    >>> engine_local_to_replicated('ReplacingMergeTree(timestamp) order by (test)', 'test', 'foo')
    "ReplicatedReplacingMergeTree('/clickhouse/tables/{layer}-{shard}/test.foo','{replica}',timestamp) order by (test)"
    >>> engine_local_to_replicated('AggregatingMergeTree order by (test)', 'test', 'foo')
    "ReplicatedAggregatingMergeTree('/clickhouse/tables/{layer}-{shard}/test.foo','{replica}') order by (test)"
    """

    def _replace(m):
        parts = m.groups()

        engine_type = parts[0]
        engine_args = f",{parts[2]}" if parts[2] else ""
        engine_settings = parts[3]

        replication_args = f"'/clickhouse/tables/{{layer}}-{{shard}}/{database}.{name}','{{replica}}'"

        return f"Replicated{engine_type}MergeTree({replication_args}{engine_args}){engine_settings}"

    return re.sub(r"(.*)MergeTree(\(([^\)]*)\))*(.*)", _replace, engine.strip())


def engine_patch_replicated_engine(engine, engine_full, new_table_name):
    """
    >>> engine_patch_replicated_engine("ReplicatedMergeTree", "ReplicatedMergeTree('/clickhouse/tables/1-1/table_name', 'replica') PARTITION BY toYYYYMM(EventDate) ORDER BY (CounterID, EventDate, intHash32(UserID)) SAMPLE BY intHash32(UserID) SETTINGS index_granularity = 8192", 'table_name_staging')
    "ReplicatedMergeTree('/clickhouse/tables/1-1/table_name_staging', 'replica') PARTITION BY toYYYYMM(EventDate) ORDER BY (CounterID, EventDate, intHash32(UserID)) SAMPLE BY intHash32(UserID) SETTINGS index_granularity = 8192"
    >>> engine_patch_replicated_engine("ReplicatedMergeTree", "ReplicatedMergeTree('/clickhouse/tables/{layer}-{shard}/sales_product_rank_rt_replicated_2', '{replica}') PARTITION BY toYYYYMM(date) ORDER BY (purchase_location, sku_rank_lc, date)", 'sales_product_rank_rt_replicated_2_staging')
    "ReplicatedMergeTree('/clickhouse/tables/{layer}-{shard}/sales_product_rank_rt_replicated_2_staging', '{replica}') PARTITION BY toYYYYMM(date) ORDER BY (purchase_location, sku_rank_lc, date)"
    >>> engine_patch_replicated_engine("ReplicatedMergeTree", None, 't_000') is None
    True
    >>> engine_patch_replicated_engine("Log", "Log()", 't_000')
    'Log()'
    >>> engine_patch_replicated_engine("MergeTree", "MergeTree PARTITION BY toYYYYMM(event_date) ORDER BY (event_date, event_time) SETTINGS index_granularity = 1024", 't_000')
    'MergeTree PARTITION BY toYYYYMM(event_date) ORDER BY (event_date, event_time) SETTINGS index_granularity = 1024'
    """
    if not engine_full:
        return None
    if engine.lower().startswith('Replicated'.lower()):
        parts = re.split(
            r"(Replicated.*MergeTree\(')([^']*)('.*)", engine_full)
        paths = parts[2].split('/')
        paths[-1] = new_table_name
        zoo_path = '/'.join(paths)
        return ''.join(parts[:2] + [zoo_path] + parts[3:])
    return engine_full
