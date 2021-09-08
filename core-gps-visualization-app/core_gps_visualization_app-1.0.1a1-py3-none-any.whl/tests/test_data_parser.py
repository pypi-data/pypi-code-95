""" Data parser utils test class"""

from core_gps_visualization_app.components.data.operations import parse_all_data
from core_gps_visualization_app.utils import parser
from datetime import datetime
import unittest
import copy

# Example with a DB containing only 2 documents from a same schema
# In this example, each document only contains two groups identified by 'satellitedID'
# Each group contains two parameters 'elevation' and 'azimuth' besides the identifier
# The main variable between documents is 'time'
# ie. experience is made over time to observe change in other parameters
all_data = [
    {"dict_content": {"receiver": {
        "satellites": {"satellite": [
            {
                "satelliteID": "1",
                "elevation": {"value": "3.0", "unit": "degrees"},
                "azimuth": {"value": "167.0", "unit": "degrees"}
            },
            {
                "satelliteID": "12",
                "elevation": {"value": "6.0", "unit": "degrees"},
                "azimuth": {"value": "266.0", "unit": "degrees"}
            }
        ]
        },
        "receiverinfo": {
            "id": "70325e30-b432-11eb-9b05-14109fd3e671"
        },
        "time": {
            "frame": "1",
            "utc": {
                "value": "2021-02-22T19:28:55"
            }
        }
    }}},
    {"dict_content": {"receiver": {
        "satellites": {"satellite": [
            {
                "satelliteID": "1",
                "elevation": {"value": "7.0", "unit": "degrees"},
                "azimuth": {"value": "467.0", "unit": "degrees"}
            },
            {
                "satelliteID": "12",
                "elevation": {"value": "9.0", "unit": "degrees"},
                "azimuth": {"value": "301.0", "unit": "degrees"}
            }]
        },
        "receiverinfo": {
            "id": "70325e30-b432-11eb-9b05-14109fd3e671"
        },
        "time": {
            "frame": "2",
            "utc": {
                "value": "2021-02-22T19:28:56"
            }
        }
    }}},
    {"dict_content": {"timeintervalcounterdata":
        {
            "timeintervalcounter": {
                "counter": {
                    "countervalue": 0.0032755,
                    "unit": "MJD"
                },
                "timeoffset": {
                    "timeoffsetvalue": 53.864,
                    "unit": "ns"
                },
                "startdate": "2021-03-01T13:45:34"
            }
        }
    }},
    {"dict_content": {"timeintervalcounterdata":
        {
            "timeintervalcounter": {
                "counter": {
                    "countervalue": 0.0033449,
                    "unit": "MJD"
                },
                "timeoffset": {
                    "timeoffsetvalue": 49.786,
                    "unit": "ns"
                },
                "startdate": "2021-03-01T13:45:39"
            }
        }
    }}
]

config_charts = [
    {
        'xName': 'Time (UTC)',
        'yName': 'Elevation',
    },
    {
        'xName': 'Time (UTC)',
        'yName': 'Azimuth',
    },
    {
        'xName': 'Elevation',
        'yName': 'Azimuth',
    },
]

config_charts_different_schemas = [
    {
        'xName': 'Time (UTC)',
        'yName': 'Elevation',
    },
    {
        'xName': 'Time (UTC)',
        'yName': 'Azimuth',
    },
    {
        'xName': 'Elevation',
        'yName': 'Azimuth',
    },
    {
        'xName': 'Time (UTC)',
        'yName': 'Time Offset',
    }
]

config_parameters = [
    {
        'parameterName': 'Time (UTC)',
        'idsNames': [],
        # Same variable on two different schemas
        'parameterPath': ['receiver.time.utc.value', 'timeintervalcounterdata.timeintervalcounter.startdate'],
        'unitPath': None,
        'variablePath': None
    },
    {
        'parameterName': 'Elevation',
        'idsNames': ['Satellite', 'Data Origin'],
        'parameterPath': 'receiver.satellites.satellite/elevation.value',
        'unitPath': 'receiver.satellites.satellite/elevation.unit',
        'variablePath': 'receiver.time.utc.value',
    },
    {
        'parameterName': 'Azimuth',
        'idsNames': ['Satellite', 'Data Origin'],
        'parameterPath': 'receiver.satellites.satellite/azimuth.value',
        'unitPath': 'receiver.satellites.satellite/azimuth.unit',
        'variablePath': 'receiver.time.utc.value',
    },
    {
        'parameterName': 'Time Offset',
        'idsNames': [],
        'parameterPath': 'timeintervalcounterdata.timeintervalcounter/timeoffset.timeoffsetvalue',
        'unitPath': 'timeintervalcounterdata.timeintervalcounter/timeoffset.unit',
        'variablePath': 'timeintervalcounterdata.timeintervalcounter/startdate',
    }
]

config_ids = [
    {
        'idName': 'Satellite',
        'idPath': 'receiver.satellites.satellite/satelliteID',
    },
    {
        'idName': 'Data Origin',
        'idPath': 'receiver.receiverinfo.id',
    }]


class TestParseAllData(unittest.TestCase):
    expected_result = [
        {
            'x': ('Time (UTC)', None),
            'y': ('Elevation', 'degrees'),
            'ids': [{'Data Origin': '70325e30-b432-11eb-9b05-14109fd3e671'}, {'Satellite': '1'}],
            'data': [(parser.parse_date("2021-02-22T19:28:55"), 3.0),
                     (parser.parse_date("2021-02-22T19:28:56"), 7.0)]
        },
        {
            'x': ('Time (UTC)', None),
            'y': ('Elevation', 'degrees'),
            'ids': [{'Data Origin': '70325e30-b432-11eb-9b05-14109fd3e671'}, {'Satellite': '12'}],
            'data': [(parser.parse_date("2021-02-22T19:28:55"), 6.0),
                     (parser.parse_date("2021-02-22T19:28:56"), 9.0)]
        },
        {
            'x': ('Time (UTC)', None),
            'y': ('Azimuth', 'degrees'),
            'ids': [{'Data Origin': '70325e30-b432-11eb-9b05-14109fd3e671'}, {'Satellite': '1'}],
            'data': [(parser.parse_date("2021-02-22T19:28:55"), 167.0),
                     (parser.parse_date("2021-02-22T19:28:56"), 467.0)]
        },
        {
            'x': ('Time (UTC)', None),
            'y': ('Azimuth', 'degrees'),
            'ids': [{'Data Origin': '70325e30-b432-11eb-9b05-14109fd3e671'}, {'Satellite': '12'}],
            'data': [(parser.parse_date("2021-02-22T19:28:55"), 266.0),
                     (parser.parse_date("2021-02-22T19:28:56"), 301.0)]
        },
        {
            'x': ('Elevation', 'degrees'),
            'y': ('Azimuth', 'degrees'),
            'ids': [{'Data Origin': '70325e30-b432-11eb-9b05-14109fd3e671'}, {'Satellite': '1'}],
            'data': [(3.0, 167.0), (7.0, 467.0)]
        },
        {
            'x': ('Elevation', 'degrees'),
            'y': ('Azimuth', 'degrees'),
            'ids': [{'Data Origin': '70325e30-b432-11eb-9b05-14109fd3e671'}, {'Satellite': '12'}],
            'data': [(6.0, 266.0), (9.0, 301.0)]
        }
    ]

    additional_result = {
            'x': ('Time (UTC)', None),
            'y': ('Time Offset', 'ns'),
            'ids': None,
            'data': [(parser.parse_date("2021-03-01T13:45:34"), 53.864),
                     (parser.parse_date("2021-03-01T13:45:39"), 49.786)]
        }

    def test_parse_all_data(self):
        parsed_data = parse_all_data(all_data, config_charts, config_parameters, config_ids)
        self.assertTrue(parsed_data == self.expected_result)

    def test_parse_all_data_different_schemas(self):
        parsed_data = parse_all_data(all_data, config_charts_different_schemas, config_parameters, config_ids)
        self.expected_result.append(self.additional_result)
        self.assertTrue(parsed_data == self.expected_result)


class TestParseValueByPath(unittest.TestCase):
    # dict_content is the first dict of all_data list
    dict_content = all_data[0]['dict_content']
    none_path = None
    # Only one of those two paths is valid
    list_path = ['receiver.time.utc.value', 'timeintervalcounterdata.timeintervalcounter/startdate']
    simple_path = 'receiver.satellites.satellite/azimuth.value'
    ids_list_of_dicts = [{'Data Origin': '70325e30-b432-11eb-9b05-14109fd3e671'}, {'Satellite': '1'}]

    def test_parse_value_if_path_is_none(self):
        value = parser.parse_value_by_path(self.dict_content, self.none_path)
        expected_result = None
        self.assertTrue(value == expected_result)

    def test_parse_value_if_path_is_list(self):
        value = parser.parse_value_by_path(self.dict_content, self.list_path)
        expected_result = parser.parse_date("2021-02-22T19:28:55")
        self.assertTrue(value == expected_result)

    def test_get_value_by_path(self):
        value = parser.get_value_by_path(self.dict_content, self.simple_path, self.ids_list_of_dicts)
        expected_result = '167.0'
        self.assertTrue(value == expected_result)


class TestGetPathByName(unittest.TestCase):
    list_of_dicts = [{'d1a': 'v1a', 'd1b': 'v1b'}, {'d2a': 'v2a', 'd2b': 'v2b'}]
    key = 'd1a'
    value = 'v1a'
    path_key = 'd1b'

    def test_get_path_by_name(self):
        path_value = parser.get_path_by_name(self.list_of_dicts, self.key, self.value, self.path_key)
        expected_result = 'v1b'
        self.assertTrue(path_value == expected_result)


class TestGetElementsByUnion(unittest.TestCase):
    list_of_dicts = [{'d1a': 'v1a', 'common_key': [1, 2, 4, 6, 8, 10, 12]},
                     {'d2a': 'v2a', 'common_key': [1, 3, 6, 9, 12]}]
    id_1 = 'v1a'
    id_2 = 'v2a'
    union_point = 'common_key'

    def test_get_elements_by_union(self):
        # elements_by_union is the union between the two lists that share the common_key
        # No need to sort since in real use, those values are independent dicts
        expected_result = [1, 2, 3, 4, 6, 8, 9, 10, 12]
        elements_by_union = parser.get_elements_by_union(self.list_of_dicts, self.id_1, self.id_2,
                                                         self.union_point)
        self.assertTrue(set(expected_result) == set(elements_by_union))


class TestAddOrUpdateCharts(unittest.TestCase):
    chart_dict_update = {
        'x': ('x_name1', 'x_unit1'),
        'y': ('y_name1', 'y_unit1'),
        'ids': [{'idA': 'idA_1a'}, {'idB': 'idB_1a'}],
        # Same 'x', 'y' and 'ids' than 1st element of list_of_charts but additional data provided
        'data': [(1, 1), (2, 2), (3, 3), (4, 4)]
    }

    chart_dict_add = {
        'x': ('x_name3', 'x_unit3'),
        'y': ('y_name3', 'y_unit3'),
        # Same 'ids' than list_of_charts 1st element but unique 'x' and 'y'
        'ids': [{'idA': 'idA_1a'}, {'idB': 'idB_1a'}],
        'data': [(2, 3), (4, 6), (6, 9)]
    }

    chart_dict_add_another = {
        'x': ('x_name1', 'x_unit1'),
        'y': ('y_name1', 'y_unit1'),
        # Same 'x' and 'y' than list_of_charts 1st element but unique 'ids' for that combination
        'ids': [{'idA': 'idA_2a'}, {'idB': 'idB_2a'}],
        'data': [(2, 5), (4, 10), (6, 15)]
    }

    list_of_charts = [
        {
            'x': ('x_name1', 'x_unit1'),
            'y': ('y_name1', 'y_unit1'),
            'ids': [{'idA': 'idA_1a'}, {'idB': 'idB_1a'}],
            'data': [(1, 1), (2, 2), (3, 3)]
        },
        {
            'x': ('x_name1', 'x_unit1'),
            # Same 'x' and 'y' than 1st element but 'ids' different
            'y': ('y_name1', 'y_unit1'),
            'ids': [{'idA': 'idA_1b'}, {'idB': 'idB_1b'}],
            'data': [(3, 4), (6, 8), (9, 12), (12, 16)]
        },
        {
            'x': ('x_name2', 'x_unit2'),
            'y': ('y_name2', 'y_unit2'),
            'ids': [{'idA': 'idA_2a'}, {'idB': 'idB_2a'}],
            'data': [(2, 2), (4, 4), (8, 16), (16, 256)]
        },
        {
            'x': ('x_name2', 'x_unit2'),
            'y': ('y_name2', 'y_unit2'),
            # Same ids than 1st element but 'x' and 'y' different
            'ids': [{'idA': 'idA_1a'}, {'idB': 'idB_1a'}],
            'data': [(2, 12), (4, 4), (6, 6), (8, 256)]
        }
    ]

    def test_update_charts(self):
        # chart_dict_update 'data' has replaced 'data' from 1st element of list_of_charts
        # it added a new tuple at the end of the list
        # because their 'ids' lists are the same for a unique combination of 'x' and 'y'
        list_of_charts_copy = copy.deepcopy(self.list_of_charts)
        chart_dict_update_copy = copy.deepcopy(self.chart_dict_update)
        list_of_charts_copy[0]['data'] = chart_dict_update_copy['data']
        expected_result = list_of_charts_copy
        updated_list_of_charts = parser.add_or_update_charts(self.chart_dict_update,
                                                             self.list_of_charts)
        self.assertTrue(expected_result == updated_list_of_charts)

    def test_add_charts(self):
        # chart_dict_add entire dict has been added at the end of list_of_charts
        # because no other element had the same 'x' and 'y' for this 'ids' list
        list_of_charts_copy = copy.deepcopy(self.list_of_charts)
        list_of_charts_copy.append(self.chart_dict_add)
        expected_result = list_of_charts_copy
        updated_list_of_charts = parser.add_or_update_charts(self.chart_dict_add,
                                                             self.list_of_charts)
        self.assertTrue(expected_result == updated_list_of_charts)

    def test_add_another_charts(self):
        # chart_dict_add entire dict has been added at the end of list_of_charts
        # because no other element had the same 'ids' list for this 'x' and 'y'
        list_of_charts_copy = copy.deepcopy(self.list_of_charts)
        list_of_charts_copy.append(self.chart_dict_add_another)
        expected_result = list_of_charts_copy
        updated_list_of_charts = parser.add_or_update_charts(self.chart_dict_add_another,
                                                             self.list_of_charts)
        self.assertTrue(expected_result == updated_list_of_charts)


class TestGetChartDictByIds(unittest.TestCase):
    x_tuple = ('x_name1', 'x_unit1')
    y_tuple = ('y_name1', 'y_unit1')
    ids_list = [{'idA': 'idA_1a'}, {'idB': 'idB_1a'}]

    # Not in list_of_charts
    ids_list_no_result = [{'idA': 'idA_4a'}, {'idB': 'idB_1a'}]
    x_name_no_result = 'x_name5'

    list_of_charts = [
        # this dict has the same 'ids', 'x' and 'y' than variables above
        {
            'x': ('x_name1', 'x_unit1'),
            'y': ('y_name1', 'y_unit1'),
            'ids': [{'idA': 'idA_1a'}, {'idB': 'idB_1a'}],
            'data': [(1, 1), (2, 2), (3, 3)]
        },
        {
            'x': ('x_name1', 'x_unit1'),
            # Same 'x' and 'y' than 1st element but 'ids' different
            'y': ('y_name1', 'y_unit1'),
            'ids': [{'idA': 'idA_1b'}, {'idB': 'idB_1b'}],
            'data': [(3, 4), (6, 8), (9, 12), (12, 16)]
        },
        {
            'x': ('x_name2', 'x_unit2'),
            'y': ('y_name2', 'y_unit2'),
            'ids': [{'idA': 'idA_2a'}, {'idB': 'idB_2a'}],
            'data': [(2, 2), (4, 4), (8, 16), (16, 256)]
        },
        {
            'x': ('x_name2', 'x_unit2'),
            'y': ('y_name2', 'y_unit2'),
            # Same ids than 1st element but 'x' and 'y' different
            'ids': [{'idA': 'idA_1a'}, {'idB': 'idB_1a'}],
            'data': [(2, 12), (4, 4), (6, 6), (8, 256)]
        }
    ]

    def test_get_chart_dict_by_ids(self):
        # Expected first element of the list_of_charts
        expected_result = {
            'x': ('x_name1', 'x_unit1'),
            'y': ('y_name1', 'y_unit1'),
            'ids': [{'idA': 'idA_1a'}, {'idB': 'idB_1a'}],
            'data': [(1, 1), (2, 2), (3, 3)]
        }
        retrieved_chart = parser.get_chart_dict_by_ids(self.x_tuple, self.y_tuple, self.ids_list, self.list_of_charts)
        self.assertTrue(expected_result == retrieved_chart)

    def test_get_chart_dict_by_ids_no_result(self):
        # No result with this 'ids' list
        expected_result = None
        no_chart_retrieved = parser.get_chart_dict_by_ids(self.x_tuple, self.y_tuple, self.ids_list_no_result,
                                                          self.list_of_charts)
        self.assertTrue(expected_result == no_chart_retrieved)

    def test_get_chart_dict_by_ids_no_result_2(self):
        # No result with this 'x' and 'y' combination
        expected_result = None
        no_chart_retrieved = parser.get_chart_dict_by_ids(self.x_name_no_result, self.y_tuple, self.ids_list,
                                                          self.list_of_charts)
        self.assertTrue(expected_result == no_chart_retrieved)


class TestGetIdsValuesByPaths(unittest.TestCase):
    # dict_content is the first dict of all_data list
    dict_content = all_data[0]['dict_content']
    ids_paths_list_of_tuples = [('Data Origin', 'receiver.receiverinfo.id'),
                                ('Satellite', 'receiver.satellites.satellite/satelliteID')]

    def test_get_ids_values_by_paths(self):
        expected_result = [[{'Data Origin': '70325e30-b432-11eb-9b05-14109fd3e671'}, {'Satellite': '1'}],
                           [{'Data Origin': '70325e30-b432-11eb-9b05-14109fd3e671'}, {'Satellite': '12'}]]
        ids_values = parser.get_ids_values_by_paths(self.dict_content, self.ids_paths_list_of_tuples)
        self.assertTrue(expected_result == ids_values)


class TestGetIdsPathByName(unittest.TestCase):
    ids_list_of_dicts = [{'Satellite': 1}, {'Data Origin': '70325e30-b432-11eb-9b05-14109fd3e671'}]

    def test_get_ids_path_by_name(self):
        expected_result = [{'satelliteID': 1}, {'id': '70325e30-b432-11eb-9b05-14109fd3e671'}]
        ids_values = parser.get_ids_path_by_name(self.ids_list_of_dicts, config_ids)
        self.assertTrue(expected_result == ids_values)


class TestParseDate(unittest.TestCase):
    date = '2021-03-23T08:30:05'

    def test_parse_date(self):
        expected_result = datetime(2021, 3, 23, 8, 30, 5)
        parsed_date = parser.parse_date(self.date)
        self.assertTrue(expected_result == parsed_date)


class TestParseTimeRangeData(unittest.TestCase):
    time_range = "Minutes"
    list_of_tuples_data = [(parser.parse_date("2021-02-22T19:28:55"), 3), (parser.parse_date("2021-02-22T19:28:56"), 5),
                           (parser.parse_date("2021-02-22T19:28:57"), 8), (parser.parse_date("2021-02-22T19:28:58"), 6),
                           (parser.parse_date("2021-02-22T19:28:59"), 4), (parser.parse_date("2021-02-22T19:29:00"), 5),
                           (parser.parse_date("2021-02-22T19:29:01"), 2), (parser.parse_date("2021-02-22T19:29:02"), 7),
                           (parser.parse_date("2021-02-22T19:29:03"), 9), (parser.parse_date("2021-02-22T19:29:04"), 8)
                           ]

    def test_parse_time_range_data(self):
        # Date truncated to the minute and 5 is median of [3, 5, 8, 6, 4] and 7 is median of [5, 2, 7, 9, 8]
        expected_result = [(datetime(year=2021, month=2, day=22, hour=19, minute=28), 5),
                           (datetime(year=2021, month=2, day=22, hour=19, minute=29), 7)]
        parsed_data = parser.parse_time_range_data(self.list_of_tuples_data, self.time_range)
        self.assertTrue(expected_result == parsed_data)


if __name__ == '__main__':
    unittest.main()
