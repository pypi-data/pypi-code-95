import datetime

geoformat_field_type_to_python_type = {
    'Integer': int,
    'IntegerList': int,
    'Real': float,
    'RealList': float,
    'String': str,
    'StringList': str,
    'Binary': bytes,
    'Date': datetime.date,
    'Time': datetime.time,
    'DateTime': datetime.datetime,
    'Boolean': bool
}

geoformat_field_type_to_postgresql_type = {
    'Integer': 'integer',
    'IntegerList': "integer[]",
    'Real': 'numeric',
    'RealList': 'numeric[]',
    'String': 'character varying',
    'StringList': 'character varying[]',
    'Binary': 'bytea',
    'Date': 'date',
    'Time': 'time',
    'DateTime': 'timestamp',
    'Boolean': 'boolean'
}

geoformat_field_type_to_geojson_field_type = {
    'Binary': str,
    'Date': str,
    'Time': str,
    'DateTime': str,
}

python_type_to_field_type = {
    str: 'String',
    (str, list): 'StringList',
    float: 'Real',
    (float, list): 'RealList',
    int: 'Integer',
    (int, list): 'IntegerList',
    datetime.date: 'Date',
    datetime.time: 'Time',
    datetime.datetime: 'DateTime',
    bytes: 'Binary',
    bool: 'Boolean',
}

recast_black_list = {
    'Integer': {'Binary', 'Date', 'Time', 'DateTime'},
    'IntegerList': {'Real', 'Integer', 'Binary', 'Date', 'Time', 'DateTime', 'Boolean'},
    'Real': {'Binary', 'Date', 'Time', 'DateTime'},
    'RealList': {'Integer', 'Real', 'Binary', 'Date', 'Time', 'DateTime', 'Boolean'},
    'String': {'Date', 'Time', 'DateTime'},
    'StringList': {'Integer', 'Real', 'Binary', 'Date', 'Time', 'DateTime', 'Boolean'},
    'Date': {'Integer', 'IntegerList', 'Real', 'RealList', 'Binary', 'Time', 'DateTime'},
    'Time': {'Integer', 'IntegerList', 'Real', 'RealList', 'Binary', 'Date', 'DateTime'},
    'DateTime': {'Integer', 'IntegerList', 'Real', 'RealList', 'Binary'},
    'Binary': {'Integer', 'IntegerList', 'Real', 'RealList', 'Date', 'Time', 'DateTime'},
    'Boolean': {'IntegerList', 'RealList', 'StringList', 'Date', 'Time', 'DateTime'}
}
ogr_cod_field_type_to_geoformat_field_type = {
    0: 'Integer',
    1: 'IntegerList',
    2: 'Real',
    3: 'RealList',
    4: 'String',
    5: 'StringList',
    6: 'String',  # WideString
    7: 'StringList',  # WideStringList
    8: 'Binary',
    9: 'Date',
    10: 'Time',
    11: 'DateTime'
}
field_metadata_width_required = {'Real', 'RealList', 'String', 'StringList'}
field_metadata_precision_required = {'Real', 'RealList'}

