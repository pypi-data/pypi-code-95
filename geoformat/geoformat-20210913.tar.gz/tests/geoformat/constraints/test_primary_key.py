import datetime

from geoformat.constraints.primary_key import create_pk

from test_all import test_function

from tests.data.geolayers import (
    geolayer_attributes_only_without_none_value,
    geolayer_fr_dept_geometry_only,
    geolayer_attributes_to_force_only_forced
)

from geoformat.conf.error_messages import (
    missing_field,
    non_unique_values
)

create_pk_parameters = {
    0: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_integer',
        "return_value": {586: 0}
    },
    1: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_integer_list',
        "return_value": {(5879, 8557): 0}
    },
    2: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_real',
        "return_value": {8789.97568: 0}
    },
    3: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_real_list',
        "return_value": {(89798.3654, 8757.97568): 0}
    },
    4: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_string',
        "return_value": {'salut': 0}
    },
    5: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_string_list',
        "return_value": {('bonjour', 'monsieur'): 0}
    },
    6: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_date',
        "return_value": {datetime.date(2020, 3, 31): 0}
    },
    7: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_time',
        "return_value": {datetime.time(11, 22, 10, 999): 0}
    },
    8: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_datetime',
        "return_value": {datetime.datetime(2020, 3, 31, 11, 22, 10, 999): 0}
    },
    9: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_binary',
        "return_value": {b'\x00\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01?\xf0\x00\x00\x00\x00\x00\x00?\xf0\x00\x00\x00\x00\x00\x00': 0}
    },
    10: {
        "geolayer": geolayer_attributes_only_without_none_value,
        "pk_field_name": 'field_boolean',
        "return_value": {True: 0}
    },
    11: {
        "geolayer": geolayer_fr_dept_geometry_only,
        "pk_field_name": 'foo',
        "return_value": missing_field.format(field_name='foo')
    },
    12: {
        "geolayer": geolayer_attributes_to_force_only_forced,
        "pk_field_name": "field_integer_list",
        "return_value": non_unique_values.format(field_name="field_integer_list")
    }
}


def test_all():

    # create_pk
    print(test_function(create_pk, create_pk_parameters))


if __name__ == '__main__':
    test_all()