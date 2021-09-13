import datetime

from test_all import test_function

from tests.data.geolayers import (
    geolayer_attributes_only,
    geolayer_attributes_only_boolean_false,
    geolayer_fields_with_bytes_values,
    geolayer_fields_with_bytes_values_forced
)

from tests.data.fields_metadata import (
    geolayer_attributes_only_fields_metadata,
    geolayer_attributes_only_fields_metadata_without_index,
    geolayer_data_fields_metadata_extract
)

from tests.data.features import (
    date_time_value,
    date_value,
    time_value
)

from geoformat.conversion.fields_conversion import (
    update_field_index,
    recast_field_value,
    drop_field,
    recast_field
)

from tests.data.geometries import (
    POINT_WKB_BIG_ENDIAN,
    GEOMETRYCOLLECTION_WKB_BIG_ENDIAN,
    POINT_WKB_HEX_BIG_ENDIAN,
    GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN
)

update_field_index_parameters = {
    0: {
        "fields_metadata": geolayer_data_fields_metadata_extract,
        "field_name": "NOM_DEPT",
        "new_index": 0,
        "return_value": {
            'NOM_DEPT': {'type': 'String', 'width': 10, 'index': 0},
            'CODE_DEPT': {'type': 'String', 'width': 2, 'index': 1},
        }
    },
    1: {
        "fields_metadata": geolayer_data_fields_metadata_extract,
        "field_name": "CODE_DEPT",
        "new_index": 1,
        "return_value": {
            'NOM_DEPT': {'type': 'String', 'width': 10, 'index': 0},
            'CODE_DEPT': {'type': 'String', 'width': 2, 'index': 1},
        }
    },
    2: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_integer",
        "new_index": 10,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 10},
            'field_integer_list': {'type': 'IntegerList', 'index': 0},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 1},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 2},
            'field_string': {'type': 'String', 'width': 5, 'index': 3},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 6},
            'field_datetime': {'type': 'DateTime', 'index': 7},
            'field_binary': {'type': 'Binary', 'index': 8},
            'field_boolean': {'type': 'Boolean', 'index': 9}
        }
    },
    3: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_date",
        "new_index": 10,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 4},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 10},
            'field_time': {'type': 'Time', 'index': 6},
            'field_datetime': {'type': 'DateTime', 'index': 7},
            'field_binary': {'type': 'Binary', 'index': 8},
            'field_boolean': {'type': 'Boolean', 'index': 9}
        }
    },
    4: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 0,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 1},
            'field_integer_list': {'type': 'IntegerList', 'index': 2},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 3},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 4},
            'field_string': {'type': 'String', 'width': 5, 'index': 0},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    5: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 1,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 2},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 3},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 4},
            'field_string': {'type': 'String', 'width': 5, 'index': 1},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    6: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 2,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 3},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 4},
            'field_string': {'type': 'String', 'width': 5, 'index': 2},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    7: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 3,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 4},
            'field_string': {'type': 'String', 'width': 5, 'index': 3},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    8: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 4,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 4},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    9: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 5,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 5},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    10: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 6,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 6},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    11: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 7,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 7},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 6},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    12: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 8,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 8},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 6},
            'field_datetime': {'type': 'DateTime', 'index': 7},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    13: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 9,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 9},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 6},
            'field_datetime': {'type': 'DateTime', 'index': 7},
            'field_binary': {'type': 'Binary', 'index': 8},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    14: {
        "fields_metadata": geolayer_attributes_only_fields_metadata,
        "field_name": "field_string",
        "new_index": 10,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 10},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 6},
            'field_datetime': {'type': 'DateTime', 'index': 7},
            'field_binary': {'type': 'Binary', 'index': 8},
            'field_boolean': {'type': 'Boolean', 'index': 9}
        }
    },
    15: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 0,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 1},
            'field_integer_list': {'type': 'IntegerList', 'index': 2},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 3},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 4},
            'field_string': {'type': 'String', 'width': 5, 'index': 0},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    16: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 1,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 2},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 3},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 4},
            'field_string': {'type': 'String', 'width': 5, 'index': 1},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    17: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 2,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 3},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 4},
            'field_string': {'type': 'String', 'width': 5, 'index': 2},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    18: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 3,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 4},
            'field_string': {'type': 'String', 'width': 5, 'index': 3},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    19: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 4,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 4},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    20: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 5,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 5},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 6},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    21: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 6,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 6},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 7},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    22: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 7,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 7},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 6},
            'field_datetime': {'type': 'DateTime', 'index': 8},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    23: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 8,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 8},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 6},
            'field_datetime': {'type': 'DateTime', 'index': 7},
            'field_binary': {'type': 'Binary', 'index': 9},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    24: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 9,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 9},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 6},
            'field_datetime': {'type': 'DateTime', 'index': 7},
            'field_binary': {'type': 'Binary', 'index': 8},
            'field_boolean': {'type': 'Boolean', 'index': 10}
        }
    },
    25: {
        "fields_metadata": geolayer_attributes_only_fields_metadata_without_index,
        "field_name": "field_string",
        "new_index": 10,
        "return_value": {
            'field_integer': {'type': 'Integer', 'index': 0},
            'field_integer_list': {'type': 'IntegerList', 'index': 1},
            'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
            'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
            'field_string': {'type': 'String', 'width': 5, 'index': 10},
            'field_string_list': {'type': 'StringList', 'width': 8, 'index': 4},
            'field_date': {'type': 'Date', 'index': 5},
            'field_time': {'type': 'Time', 'index': 6},
            'field_datetime': {'type': 'DateTime', 'index': 7},
            'field_binary': {'type': 'Binary', 'index': 8},
            'field_boolean': {'type': 'Boolean', 'index': 9}
        }
    },
}

drop_field_parameters = {
    0: {
        "geolayer": {
            "metadata": {
                "name": "new_geolayer",
                "fields": {
                    'field_integer': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 0},
                    'field_integer_list': {'type': 'String', 'width': 13, 'index': 1},
                    'field_real': {'type': 'String', 'width': 7, 'index': 2},
                    'field_real_list': {'type': 'String', 'width': 19, 'index': 3},
                    'field_string': {'type': 'String', 'width': 26, 'index': 4},
                    'field_date': {'type': 'Date', 'index': 5},
                    'field_time': {'type': 'String', 'width': 15, 'index': 6},
                    'field_binary': {'type': 'String', 'width': 201, 'index': 7},
                    'field_boolean': {'type': 'String', 'width': 5, 'index': 8},
                    'field_string_list': {'type': 'String', 'width': 16, 'index': 9},
                    'field_datetime': {'type': 'DateTime', 'index': 10}
                }
            },
            "features": {
                0: {
                    "attributes": {
                        "field_integer": 586.,
                        "field_integer_list": "[5879, 8557]",
                        "field_real": "8789.98",
                        "field_real_list": "[89798.3654, 8757.]",
                        "field_string": None,
                        "field_date": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                        microsecond=999).date(),  # 5
                        "field_time": '18:41:04',
                        "field_binary": "b'\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00'",
                        "field_boolean": "True",
                    },
                },
                1: {
                    "attributes": {
                        "field_integer": 1466.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]",
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "salut",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": str(b'\x00\x00\x00\x00\x01@\xef\xf3k\n=p\xa4@\xbd\xe6\x8b\x02\x0cI\xba'),
                        "field_boolean": "False",
                    }
                },
                2: {
                    "attributes": {
                        "field_integer": 149.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]"
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "2020-03-31 11:22:10.000999",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": None,
                        "field_boolean": "1",
                    }
                }
            }
        },
        "field_name_to_drop": 'field_integer',
        "return_value": {
            "metadata": {
                "name": "new_geolayer",
                "fields": {
                    'field_integer_list': {'type': 'String', 'width': 13, 'index': 0},
                    'field_real': {'type': 'String', 'width': 7, 'index': 1},
                    'field_real_list': {'type': 'String', 'width': 19, 'index': 2},
                    'field_string': {'type': 'String', 'width': 26, 'index': 3},
                    'field_date': {'type': 'Date', 'index': 4},
                    'field_time': {'type': 'String', 'width': 15, 'index': 5},
                    'field_binary': {'type': 'String', 'width': 201, 'index': 6},
                    'field_boolean': {'type': 'String', 'width': 5, 'index': 7},
                    'field_string_list': {'type': 'String', 'width': 16, 'index': 8},
                    'field_datetime': {'type': 'DateTime', 'index': 9}
                }
            },
            "features": {
                0: {
                    "attributes": {
                        "field_integer_list": "[5879, 8557]",
                        "field_real": "8789.98",
                        "field_real_list": "[89798.3654, 8757.]",
                        "field_string": None,
                        "field_date": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                        microsecond=999).date(),  # 5
                        "field_time": '18:41:04',
                        "field_binary": "b'\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00'",
                        "field_boolean": "True",
                    },
                },
                1: {
                    "attributes": {
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]",
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "salut",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": str(b'\x00\x00\x00\x00\x01@\xef\xf3k\n=p\xa4@\xbd\xe6\x8b\x02\x0cI\xba'),
                        "field_boolean": "False",
                    }
                },
                2: {
                    "attributes": {
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]"
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "2020-03-31 11:22:10.000999",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": None,
                        "field_boolean": "1",
                    }
                }
            }
        }
    },
    1: {
        "geolayer": {
            "metadata": {
                "name": "new_geolayer",
                "fields": {
                    'field_integer': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 0},
                    'field_integer_list': {'type': 'String', 'width': 13, 'index': 1},
                    'field_real': {'type': 'String', 'width': 7, 'index': 2},
                    'field_real_list': {'type': 'String', 'width': 19, 'index': 3},
                    'field_string': {'type': 'String', 'width': 26, 'index': 4},
                    'field_date': {'type': 'Date', 'index': 5},
                    'field_time': {'type': 'String', 'width': 15, 'index': 6},
                    'field_binary': {'type': 'String', 'width': 201, 'index': 7},
                    'field_boolean': {'type': 'String', 'width': 5, 'index': 8},
                    'field_string_list': {'type': 'String', 'width': 16, 'index': 9},
                    'field_datetime': {'type': 'DateTime', 'index': 10}
                }
            },
            "features": {
                0: {
                    "attributes": {
                        "field_integer": 586.,
                        "field_integer_list": "[5879, 8557]",
                        "field_real": "8789.98",
                        "field_real_list": "[89798.3654, 8757.]",
                        "field_string": None,
                        "field_date": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                        microsecond=999).date(),  # 5
                        "field_time": '18:41:04',
                        "field_binary": "b'\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00'",
                        "field_boolean": "True",
                    },
                },
                1: {
                    "attributes": {
                        "field_integer": 1466.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]",
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "salut",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": str(b'\x00\x00\x00\x00\x01@\xef\xf3k\n=p\xa4@\xbd\xe6\x8b\x02\x0cI\xba'),
                        "field_boolean": "False",
                    }
                },
                2: {
                    "attributes": {
                        "field_integer": 149.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]"
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "2020-03-31 11:22:10.000999",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": None,
                        "field_boolean": "1",
                    }
                }
            }
        },
        "field_name_to_drop": 'field_datetime',
        "return_value": {
            "metadata": {
                "name": "new_geolayer",
                "fields": {
                    'field_integer': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 0},
                    'field_integer_list': {'type': 'String', 'width': 13, 'index': 1},
                    'field_real': {'type': 'String', 'width': 7, 'index': 2},
                    'field_real_list': {'type': 'String', 'width': 19, 'index': 3},
                    'field_string': {'type': 'String', 'width': 26, 'index': 4},
                    'field_date': {'type': 'Date', 'index': 5},
                    'field_time': {'type': 'String', 'width': 15, 'index': 6},
                    'field_binary': {'type': 'String', 'width': 201, 'index': 7},
                    'field_boolean': {'type': 'String', 'width': 5, 'index': 8},
                    'field_string_list': {'type': 'String', 'width': 16, 'index': 9},
                }
            },
            "features": {
                0: {
                    "attributes": {
                        "field_integer": 586.,
                        "field_integer_list": "[5879, 8557]",
                        "field_real": "8789.98",
                        "field_real_list": "[89798.3654, 8757.]",
                        "field_string": None,
                        "field_date": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                        microsecond=999).date(),  # 5
                        "field_time": '18:41:04',
                        "field_binary": "b'\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00'",
                        "field_boolean": "True",
                    },
                },
                1: {
                    "attributes": {
                        "field_integer": 1466.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]",
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "salut",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_binary": str(b'\x00\x00\x00\x00\x01@\xef\xf3k\n=p\xa4@\xbd\xe6\x8b\x02\x0cI\xba'),
                        "field_boolean": "False",
                    }
                },
                2: {
                    "attributes": {
                        "field_integer": 149.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]"
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "2020-03-31 11:22:10.000999",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_binary": None,
                        "field_boolean": "1",
                    }
                }
            }
        }
    },
    2: {
        "geolayer": {
            "metadata": {
                "name": "new_geolayer",
                "fields": {
                    'field_integer': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 0},
                    'field_integer_list': {'type': 'String', 'width': 13, 'index': 1},
                    'field_real': {'type': 'String', 'width': 7, 'index': 2},
                    'field_real_list': {'type': 'String', 'width': 19, 'index': 3},
                    'field_string': {'type': 'String', 'width': 26, 'index': 4},
                    'field_date': {'type': 'Date', 'index': 5},
                    'field_time': {'type': 'String', 'width': 15, 'index': 6},
                    'field_binary': {'type': 'String', 'width': 201, 'index': 7},
                    'field_boolean': {'type': 'String', 'width': 5, 'index': 8},
                    'field_string_list': {'type': 'String', 'width': 16, 'index': 9},
                    'field_datetime': {'type': 'DateTime', 'index': 10}
                }
            },
            "features": {
                0: {
                    "attributes": {
                        "field_integer": 586.,
                        "field_integer_list": "[5879, 8557]",
                        "field_real": "8789.98",
                        "field_real_list": "[89798.3654, 8757.]",
                        "field_string": None,
                        "field_date": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                        microsecond=999).date(),  # 5
                        "field_time": '18:41:04',
                        "field_binary": "b'\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00'",
                        "field_boolean": "True",
                    },
                },
                1: {
                    "attributes": {
                        "field_integer": 1466.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]",
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "salut",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": str(b'\x00\x00\x00\x00\x01@\xef\xf3k\n=p\xa4@\xbd\xe6\x8b\x02\x0cI\xba'),
                        "field_boolean": "False",
                    }
                },
                2: {
                    "attributes": {
                        "field_integer": 149.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]"
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "2020-03-31 11:22:10.000999",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": None,
                        "field_boolean": "1",
                    }
                }
            }
        },
        "field_name_to_drop": 'field_string',
        "return_value": {
            "metadata": {
                "name": "new_geolayer",
                "fields": {
                    'field_integer': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 0},
                    'field_integer_list': {'type': 'String', 'width': 13, 'index': 1},
                    'field_real': {'type': 'String', 'width': 7, 'index': 2},
                    'field_real_list': {'type': 'String', 'width': 19, 'index': 3},
                    'field_date': {'type': 'Date', 'index': 4},
                    'field_time': {'type': 'String', 'width': 15, 'index': 5},
                    'field_binary': {'type': 'String', 'width': 201, 'index': 6},
                    'field_boolean': {'type': 'String', 'width': 5, 'index': 7},
                    'field_string_list': {'type': 'String', 'width': 16, 'index': 8},
                    'field_datetime': {'type': 'DateTime', 'index': 9}
                }
            },
            "features": {
                0: {
                    "attributes": {
                        "field_integer": 586.,
                        "field_integer_list": "[5879, 8557]",
                        "field_real": "8789.98",
                        "field_real_list": "[89798.3654, 8757.]",
                        "field_date": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                        microsecond=999).date(),  # 5
                        "field_time": '18:41:04',
                        "field_binary": "b'\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00'",
                        "field_boolean": "True",
                    },
                },
                1: {
                    "attributes": {
                        "field_integer": 1466.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]",
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": str(b'\x00\x00\x00\x00\x01@\xef\xf3k\n=p\xa4@\xbd\xe6\x8b\x02\x0cI\xba'),
                        "field_boolean": "False",
                    }
                },
                2: {
                    "attributes": {
                        "field_integer": 149.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]"
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": None,
                        "field_boolean": "1",
                    }
                }
            }
        },
    },
    3: {
        "geolayer": {
            "metadata": {
                "name": "new_geolayer",
                "fields": {
                    'field_integer': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 0},
                    'field_integer_list': {'type': 'String', 'width': 13, 'index': 1},
                    'field_real': {'type': 'String', 'width': 7, 'index': 2},
                    'field_real_list': {'type': 'String', 'width': 19, 'index': 3},
                    'field_string': {'type': 'String', 'width': 26, 'index': 4},
                    'field_date': {'type': 'Date', 'index': 5},
                    'field_time': {'type': 'String', 'width': 15, 'index': 6},
                    'field_binary': {'type': 'String', 'width': 201, 'index': 7},
                    'field_boolean': {'type': 'String', 'width': 5, 'index': 8},
                    'field_string_list': {'type': 'String', 'width': 16, 'index': 9},
                    'field_datetime': {'type': 'DateTime', 'index': 10}
                }
            },
            "features": {
                0: {
                    "attributes": {
                        "field_integer": 586.,
                        "field_integer_list": "[5879, 8557]",
                        "field_real": "8789.98",
                        "field_real_list": "[89798.3654, 8757.]",
                        "field_string": None,
                        "field_date": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                        microsecond=999).date(),  # 5
                        "field_time": '18:41:04',
                        "field_binary": "b'\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00'",
                        "field_boolean": "True",
                    },
                },
                1: {
                    "attributes": {
                        "field_integer": 1466.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]",
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "salut",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": str(b'\x00\x00\x00\x00\x01@\xef\xf3k\n=p\xa4@\xbd\xe6\x8b\x02\x0cI\xba'),
                        "field_boolean": "False",
                    }
                },
                2: {
                    "attributes": {
                        "field_integer": 149.,
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]"
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string": "2020-03-31 11:22:10.000999",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_datetime": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                            microsecond=999),
                        "field_binary": None,
                        "field_boolean": "1",
                    }
                }
            }
        },
        "field_name_to_drop": ['field_string', 'field_integer', 'field_datetime'],
        "return_value": {
            "metadata": {
                "name": "new_geolayer",
                "fields": {
                    'field_integer_list': {'type': 'String', 'width': 13, 'index': 0},
                    'field_real': {'type': 'String', 'width': 7, 'index': 1},
                    'field_real_list': {'type': 'String', 'width': 19, 'index': 2},
                    'field_date': {'type': 'Date', 'index': 3},
                    'field_time': {'type': 'String', 'width': 15, 'index': 4},
                    'field_binary': {'type': 'String', 'width': 201, 'index': 5},
                    'field_boolean': {'type': 'String', 'width': 5, 'index': 6},
                    'field_string_list': {'type': 'String', 'width': 16, 'index': 7},
                }
            },
            "features": {
                0: {
                    "attributes": {
                        "field_integer_list": "[5879, 8557]",
                        "field_real": "8789.98",
                        "field_real_list": "[89798.3654, 8757.]",
                        "field_date": datetime.datetime(year=2020, month=3, day=31, hour=11, minute=22, second=10,
                                                        microsecond=999).date(),  # 5
                        "field_time": '18:41:04',
                        "field_binary": "b'\\x00\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x02\\x00\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x01?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00?\\xf0\\x00\\x00\\x00\\x00\\x00\\x00'",
                        "field_boolean": "True",
                    },
                },
                1: {
                    "attributes": {
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]",
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_binary": str(b'\x00\x00\x00\x00\x01@\xef\xf3k\n=p\xa4@\xbd\xe6\x8b\x02\x0cI\xba'),
                        "field_boolean": "False",
                    }
                },
                2: {
                    "attributes": {
                        "field_integer_list": "[987, 2345.0]",  # good value "[987, 2345.0]"
                        "field_real": "8789",
                        "field_real_list": "[2, 5]",
                        "field_string_list": "['hi', 'mister']",
                        "field_time": "11:22:10.000999",
                        "field_binary": None,
                        "field_boolean": "1",
                    }
                }
            }
        },
    }
}

recast_field_value_parameters = {
    0: {
        "field_value": 456.894,
        "recast_value_to_python_type": int,
        "resize_value_width": None,
        "resize_value_precision": None,
        "return_value": 456
    },
    1: {
        "field_value": 456.894,
        "recast_value_to_python_type": float,
        "resize_value_width": 5,
        "resize_value_precision": 2,
        "return_value": 456.89
    },
    2: {
        "field_value": 456.894,
        "recast_value_to_python_type": float,
        "resize_value_width": 5,
        "resize_value_precision": 3,
        "return_value": 456.89
    },
    3: {
        "field_value": 456.894,
        "recast_value_to_python_type": float,
        "resize_value_width": 4,
        "resize_value_precision": 3,
        "return_value": 456.8
    }
}

recast_field_parameters = {
    0: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer',
        "recast_to_geoformat_type": 'Real',
        "rename_to": None,
        "resize_width": 3,
        "resize_precision": 1,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Real', 'width': 3, "precision": 1, 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586.0,
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    1: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer',
        "recast_to_geoformat_type": 'Real',
        "rename_to": None,
        "resize_width": 3,
        "resize_precision": 0,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Real', 'width': 3, "precision": 0, 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586.0,
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    2: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 3,
        "resize_precision": 0,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'String', 'width': 3, 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": '586',
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    3: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer',
        "recast_to_geoformat_type": 'String',
        "rename_to": "field_string_2",
        "resize_width": 2,
        "resize_precision": 0,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_string_2': {'type': 'String', 'width': 2, 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_string_2": '58',
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    4: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer',
        "recast_to_geoformat_type": 'StringList',
        "rename_to": None,
        "resize_width": 2,
        "resize_precision": 0,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'StringList', 'width': 2, 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": ['58'],
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    5: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer',
        "recast_to_geoformat_type": 'RealList',
        "rename_to": None,
        "resize_width": 3,
        "resize_precision": 2,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'RealList', 'width': 3, 'precision': 2, 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": [586.],
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    6: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Boolean', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": True,
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    7: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer_list',
        "recast_to_geoformat_type": 'IntegerList',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    8: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer_list',
        "recast_to_geoformat_type": 'RealList',
        "rename_to": None,
        "resize_width": 6,
        "resize_precision": 2,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'RealList', 'width': 6, 'precision': 2, 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879., 8557.],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    9: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer_list',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 16,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'String', 'width': 16, 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": '[5879, 8557]',
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    10: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer_list',
        "recast_to_geoformat_type": 'StringList',
        "rename_to": None,
        "resize_width": 4,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'StringList', 'width': 4, 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": ['5879', '8557'],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    11: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_integer_list',
        "recast_to_geoformat_type": 'StringList',
        "rename_to": None,
        "resize_width": 4,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'StringList', 'width': 4, 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": ['5879', '8557'],
                        "field_real": 8789.97568,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    12: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real',
        "recast_to_geoformat_type": 'Integer',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Integer', 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    13: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real',
        "recast_to_geoformat_type": 'IntegerList',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'IntegerList', 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": [8789],
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    14: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real',
        "recast_to_geoformat_type": 'RealList',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'RealList', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": [8789.97568],
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    15: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'String', 'width': 10, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": '8789.97568',
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    16: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 4,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'String', 'width': 4, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": '8789',
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    17: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real',
        "recast_to_geoformat_type": 'StringList',
        "rename_to": None,
        "resize_width": 4,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'StringList', 'width': 4, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": ['8789'],
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    19: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Boolean', 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": True,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    20: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Boolean', 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": True,
                        "field_real_list": [89798.3654, 8757.97568],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    21: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real_list',
        "recast_to_geoformat_type": 'IntegerList',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'IntegerList', 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": [89798, 8757],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    22: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real_list',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 24,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'String', 'width': 24, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": '[89798.3654, 8757.97568]',
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    23: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_real_list',
        "recast_to_geoformat_type": 'StringList',
        "rename_to": None,
        "resize_width": 10,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'StringList', 'width': 10, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes": {
                        "field_integer": 586,
                        "field_integer_list": [5879, 8557],
                        "field_real": 8789.97568,
                        "field_real_list": ["89798.3654", "8757.97568"],
                        "field_string": "salut",
                        "field_string_list": ["bonjour", "monsieur"],
                        "field_none": None,
                        "field_date": date_value,
                        "field_time": time_value,
                        "field_datetime": date_time_value,
                        "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                        "field_boolean": True
                    }
                }
            }
        }
    },
    24: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_string',
        "recast_to_geoformat_type": 'StringList',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'StringList', "width": 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": ["salut"],
                            "field_string_list": ["bonjour", "monsieur"],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    25: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_string',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'Boolean', 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": True,
                            "field_string_list": ["bonjour", "monsieur"],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    26: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_string_list',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 23,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'String', 'width': 23, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": "['bonjour', 'monsieur']",
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    27: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_date',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 10,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'String', "width": 10, 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": str(date_value),
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    28: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_date',
        "recast_to_geoformat_type": 'StringList',
        "rename_to": None,
        "resize_width": 10,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'StringList', "width": 10, 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": [str(date_value)],
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    29: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_date',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Boolean', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": True,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    30: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_time',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 15,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'String', 'width': 15, 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": str(time_value),
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    31: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_time',
        "recast_to_geoformat_type": 'StringList',
        "rename_to": None,
        "resize_width": 15,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'StringList', 'width': 15, 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": [str(time_value)],
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    32: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_time',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": 15,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Boolean', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": True,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    33: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_datetime',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 26,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'String', 'width': 26, 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": str(date_time_value),
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    34: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_datetime',
        "recast_to_geoformat_type": 'StringList',
        "rename_to": None,
        "resize_width": 26,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'StringList', 'width': 26, 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": [str(date_time_value)],
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    35: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_datetime',
        "recast_to_geoformat_type": 'Date',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'Date', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value.date(),
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    36: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_datetime',
        "recast_to_geoformat_type": 'Time',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'Time', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value.time(),
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    37: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_datetime',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'Boolean', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": True,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": True
                        }
                }
            }
        }
    },
    38: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_binary',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 201,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'String', 'width': 201, 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00'.hex(),
                            "field_boolean": True
                        }
                }
            }
        }
    },
    39: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_binary',
        "recast_to_geoformat_type": 'StringList',
        "rename_to": None,
        "resize_width": 201,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'StringList', 'width': 201, 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": [
                                b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00'.hex()],
                            "field_boolean": True
                        }
                }
            }
        }
    },
    40: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_binary',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Boolean', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": True,
                            "field_boolean": True
                        }
                }
            }
        }
    },
    41: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_boolean',
        "recast_to_geoformat_type": 'Integer',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Integer', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": 1
                        }
                }
            }
        }
    },
    42: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_boolean',
        "recast_to_geoformat_type": 'Real',
        "rename_to": None,
        "resize_width": 2,
        "resize_precision": 1,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Real', 'width': 2, 'precision': 1, 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": 1.
                        }
                }
            }
        }
    },
    43: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_boolean',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 4,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'String', 'width': 4, 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": "True"
                        }
                }
            }
        }
    },
    44: {
        "geolayer_to_recast": geolayer_attributes_only,
        "field_name_to_recast": 'field_boolean',
        "recast_to_geoformat_type": 'Binary',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Binary', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 586,
                            "field_integer_list": [5879, 8557],
                            "field_real": 8789.97568,
                            "field_real_list": [89798.3654, 8757.97568],
                            "field_string": "salut",
                            "field_string_list": ['bonjour', 'monsieur'],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00',
                            "field_boolean": b'\x00'
                        }
                }
            }
        }
    },
    45: {
        "geolayer_to_recast": geolayer_attributes_only_boolean_false,
        "field_name_to_recast": 'field_integer',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only_boolean_false',
                'fields': {
                    'field_integer': {'type': 'Boolean', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": False,
                            "field_integer_list": [],
                            "field_real": 0.,
                            "field_real_list": [],
                            "field_string": "False",
                            "field_string_list": [],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'',
                            "field_boolean": False
                        }
                }
            }
        }
    },
    46: {
        "geolayer_to_recast": geolayer_attributes_only_boolean_false,
        "field_name_to_recast": 'field_real',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only_boolean_false',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Boolean', 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 0,
                            "field_integer_list": [],
                            "field_real": False,
                            "field_real_list": [],
                            "field_string": "False",
                            "field_string_list": [],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'',
                            "field_boolean": False
                        }
                }
            }
        }
    },
    47: {
        "geolayer_to_recast": geolayer_attributes_only_boolean_false,
        "field_name_to_recast": 'field_string',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only_boolean_false',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'Boolean', 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Binary', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 0,
                            "field_integer_list": [],
                            "field_real": 0.,
                            "field_real_list": [],
                            "field_string": False,
                            "field_string_list": [],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": b'',
                            "field_boolean": False
                        }
                }
            }
        }
    },
    48: {
        "geolayer_to_recast": geolayer_attributes_only_boolean_false,
        "field_name_to_recast": 'field_binary',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            'metadata': {
                'name': 'attributes_only_boolean_false',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 5},
                    'field_date': {'type': 'Date', 'index': 6},
                    'field_time': {'type': 'Time', 'index': 7},
                    'field_datetime': {'type': 'DateTime', 'index': 8},
                    'field_binary': {'type': 'Boolean', 'index': 9},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 0,
                            "field_integer_list": [],
                            "field_real": 0.,
                            "field_real_list": [],
                            "field_string": "False",
                            "field_string_list": [],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": False,
                            "field_boolean": False
                        }
                }
            }
        }
    },
    49: {
        "geolayer_to_recast": geolayer_attributes_only_boolean_false,
        "field_name_to_recast": 'field_binary',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": 2,
        "return_value": {
            'metadata': {
                'name': 'attributes_only_boolean_false',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 3},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 4},
                    'field_string': {'type': 'String', 'width': 5, 'index': 5},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 6},
                    'field_date': {'type': 'Date', 'index': 7},
                    'field_time': {'type': 'Time', 'index': 8},
                    'field_datetime': {'type': 'DateTime', 'index': 9},
                    'field_binary': {'type': 'Boolean', 'index': 2},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 0,
                            "field_integer_list": [],
                            "field_real": 0.,
                            "field_real_list": [],
                            "field_string": "False",
                            "field_string_list": [],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary": False,
                            "field_boolean": False
                        }
                }
            }
        }
    },
    50: {
        "geolayer_to_recast": geolayer_attributes_only_boolean_false,
        "field_name_to_recast": 'field_binary',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": 'field_binary_to_bool',
        "resize_width": None,
        "resize_precision": None,
        "reindex": 5,
        "return_value": {
            'metadata': {
                'name': 'attributes_only_boolean_false',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 6},
                    'field_date': {'type': 'Date', 'index': 7},
                    'field_time': {'type': 'Time', 'index': 8},
                    'field_datetime': {'type': 'DateTime', 'index': 9},
                    'field_binary_to_bool': {'type': 'Boolean', 'index': 5},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 0,
                            "field_integer_list": [],
                            "field_real": 0.,
                            "field_real_list": [],
                            "field_string": "False",
                            "field_string_list": [],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary_to_bool": False,
                            "field_boolean": False
                        }
                }
            }
        }
    },
    51: {
        "geolayer_to_recast": geolayer_attributes_only_boolean_false,
        "field_name_to_recast": 'field_binary',
        "recast_to_geoformat_type": 'Boolean',
        "rename_to": 'field_binary_to_bool',
        "resize_width": None,
        "resize_precision": None,
        "reindex": 5,
        "return_value": {
            'metadata': {
                'name': 'attributes_only_boolean_false',
                'fields': {
                    'field_integer': {'type': 'Integer', 'index': 0},
                    'field_integer_list': {'type': 'IntegerList', 'index': 1},
                    'field_real': {'type': 'Real', 'width': 9, 'precision': 5, 'index': 2},
                    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5, 'index': 3},
                    'field_string': {'type': 'String', 'width': 5, 'index': 4},
                    'field_string_list': {'type': 'StringList', 'width': 8, 'index': 6},
                    'field_date': {'type': 'Date', 'index': 7},
                    'field_time': {'type': 'Time', 'index': 8},
                    'field_datetime': {'type': 'DateTime', 'index': 9},
                    'field_binary_to_bool': {'type': 'Boolean', 'index': 5},
                    'field_boolean': {'type': 'Boolean', 'index': 10}
                }
            },
            'features': {
                0: {
                    "attributes":
                        {
                            "field_integer": 0,
                            "field_integer_list": [],
                            "field_real": 0.,
                            "field_real_list": [],
                            "field_string": "False",
                            "field_string_list": [],
                            "field_none": None,
                            "field_date": date_value,
                            "field_time": time_value,
                            "field_datetime": date_time_value,
                            "field_binary_to_bool": False,
                            "field_boolean": False
                        }
                }
            }
        }
    },
    52: {
        "geolayer_to_recast": geolayer_fields_with_bytes_values,
        "field_name_to_recast": 'field_hexa_a',
        "recast_to_geoformat_type": 'Binary',
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            "metadata": {
                "name": "bytes_values",
                "fields": {
                    'field_bytes': {'type': 'Binary', 'index': 0},
                    'field_hexa_a': {'type': 'Binary', 'index': 1},
                    'field_hexa_b': {'type': 'String', 'width': 1116, 'index': 2},
                    'field_bytes_hexa_a': {'type': 'String', 'width': 1647, 'index': 3},
                    'field_bytes_hexa_b': {'type': 'String', 'width': 1116, 'index': 4}
                }
            },
            "features": {
                0: {
                    "attributes": {
                        "field_bytes": POINT_WKB_BIG_ENDIAN,
                        "field_hexa_a": None,
                        "field_hexa_b": POINT_WKB_HEX_BIG_ENDIAN,
                        "field_bytes_hexa_a": POINT_WKB_HEX_BIG_ENDIAN,
                        "field_bytes_hexa_b": "hello world"
                    }
                },
                1: {
                    "attributes": {
                        "field_bytes": None,
                        "field_hexa_a": bytes.fromhex(POINT_WKB_HEX_BIG_ENDIAN),
                        "field_hexa_b": 'hello world',
                        "field_bytes_hexa_a": None,
                        "field_bytes_hexa_b": POINT_WKB_BIG_ENDIAN.hex()
                    }
                },
                2: {
                    "attributes": {
                        "field_bytes": GEOMETRYCOLLECTION_WKB_BIG_ENDIAN,
                        "field_hexa_a": bytes.fromhex(GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN),
                        "field_hexa_b": GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN,
                        "field_bytes_hexa_a": GEOMETRYCOLLECTION_WKB_BIG_ENDIAN.hex(),
                        "field_bytes_hexa_b": GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN
                    }
                },
            }
        }
    },
    53: {
        "geolayer_to_recast": geolayer_fields_with_bytes_values_forced,
        "field_name_to_recast": 'field_bytes_hexa_a',
        "recast_to_geoformat_type": 'String',
        "rename_to": None,
        "resize_width": 1647,
        "resize_precision": None,
        "reindex": None,
        "return_value": {
            "metadata": {
                "name": "bytes_values",
                "fields": {
                    'field_bytes': {'type': 'Binary', 'index': 0},
                    'field_hexa_a': {'type': 'Binary', 'index': 1},
                    'field_hexa_b': {'type': 'String', 'width': 1116, 'index': 2},
                    'field_bytes_hexa_a': {'type': 'String', 'width': 1647, 'index': 3},
                    'field_bytes_hexa_b': {'type': 'String', 'width': 1116, 'index': 4}
                }
            },
            "features": {
                0: {
                    "attributes": {
                        "field_bytes": POINT_WKB_BIG_ENDIAN,
                        "field_hexa_a": None,
                        "field_hexa_b": POINT_WKB_HEX_BIG_ENDIAN,
                        "field_bytes_hexa_a": POINT_WKB_HEX_BIG_ENDIAN,
                        "field_bytes_hexa_b": "hello world"
                    }
                },
                1: {
                    "attributes": {
                        "field_bytes": None,
                        "field_hexa_a": bytes.fromhex(POINT_WKB_HEX_BIG_ENDIAN),
                        "field_hexa_b": 'hello world',
                        "field_bytes_hexa_a": None,
                        "field_bytes_hexa_b": POINT_WKB_BIG_ENDIAN.hex()
                    }
                },
                2: {
                    "attributes": {
                        "field_bytes": GEOMETRYCOLLECTION_WKB_BIG_ENDIAN,
                        "field_hexa_a": bytes.fromhex(GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN),
                        "field_hexa_b": GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN,
                        "field_bytes_hexa_a": GEOMETRYCOLLECTION_WKB_BIG_ENDIAN.hex(),
                        "field_bytes_hexa_b": GEOMETRYCOLLECTION_WKB_HEX_BIG_ENDIAN
                    }
                },
            }
        }
    },
    54: {
        "geolayer_to_recast": {'metadata': {'name': 'feature_list_structure_alpha',
                                            'fields': {'field_datetime': {'type': 'DateTime', 'index': 0}}},
                               'features': {0: {
                                   'attributes': {'field_datetime': datetime.datetime(2020, 3, 31, 11, 22, 10, 999)}},
                                            1: {'attributes': {'field_datetime': datetime.date(2020, 3, 31)}}}},
        "field_name_to_recast": 'field_datetime',
        "recast_to_geoformat_type": "DateTime",
        "rename_to": None,
        "resize_width": None,
        "resize_precision": None,
        "reindex": None,
        "return_value": {'metadata': {'name': 'feature_list_structure_alpha',
                                      'fields': {'field_datetime': {'type': 'DateTime', 'index': 0}}}, 'features': {
            0: {'attributes': {'field_datetime': datetime.datetime(2020, 3, 31, 11, 22, 10, 999)}},
            1: {'attributes': {'field_datetime': datetime.datetime(2020, 3, 31, 0, 0)}}}}
    }
}


def test_all():
    # update_field_index
    print(test_function(update_field_index, update_field_index_parameters))

    # recast_field_value
    print(test_function(recast_field_value, recast_field_value_parameters))

    # drop_field
    print(test_function(drop_field, drop_field_parameters))

    # recast_fields
    print(test_function(recast_field, recast_field_parameters))


if __name__ == '__main__':
    test_all()
