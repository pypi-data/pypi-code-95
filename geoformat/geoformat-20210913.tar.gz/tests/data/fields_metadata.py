
geolayer_attributes_only_fields_metadata = {
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


geolayer_attributes_only_fields_metadata_without_index = {
    'field_integer': {'type': 'Integer'},
    'field_integer_list': {'type': 'IntegerList'},
    'field_real': {'type': 'Real', 'width': 9, 'precision': 5},
    'field_real_list': {'type': 'RealList', 'width': 10, 'precision': 5},
    'field_string': {'type': 'String', 'width': 5},
    'field_string_list': {'type': 'StringList', 'width': 8},
    'field_date': {'type': 'Date'},
    'field_time': {'type': 'Time'},
    'field_datetime': {'type': 'DateTime'},
    'field_binary': {'type': 'Binary'},
    'field_boolean': {'type': 'Boolean'}
}

geolayer_data_fields_metadata_complete = {
    'CODE_DEPT': {'type': 'String', 'width': 2, 'index': 0},
    'NOM_DEPT': {'type': 'String', 'width': 23, 'index': 1}
}

geolayer_data_fields_metadata_extract = {
    'CODE_DEPT': {'type': 'String', 'width': 2, 'index': 0},
    'NOM_DEPT': {'type': 'String', 'width': 10, 'index': 1}
}