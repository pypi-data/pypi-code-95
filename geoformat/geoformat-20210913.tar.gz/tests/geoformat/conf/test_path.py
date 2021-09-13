from pathlib import Path

from test_all import test_function

from geoformat.conf.path import (
    add_extension_path,
    path_to_file_path,
    verify_input_path_is_file
)

from geoformat.conf.error_messages import path_not_valid

add_extension_path_parameters = {
    0: {
            "path": Path('data/geojson/test'),
            "add_extension": None,
            "return_value": Path('data/geojson/test')
    },
    1: {
            "path": Path('data/geojson/test'),
            "add_extension": '.geojson',
            "return_value": Path('data/geojson/test.geojson')
    },
    2: {
            "path": Path('data/geojson/test.geojson'),
            "add_extension": '.kml',
            "return_value": Path('data/geojson/test.geojson.kml')
    }
}

verify_input_path_is_file_parameters = {
    0: {
        "path": Path(__file__).parent.parent.parent.parent.joinpath('geoformat/conf/path.py'),
        "return_value": Path(__file__).parent.parent.parent.parent.joinpath('geoformat/conf/path.py')
    },
    1: {
        "path": Path(__file__).parent.parent.parent.parent.joinpath('geoformat/conf'),
        "return_value": path_not_valid.format(path=Path(__file__).parent.parent.parent.parent.joinpath('geoformat/conf'))
    },
    2: {
        "path": Path(__file__).parent.parent.parent.parent.joinpath('geoformat/foo'),
        "return_value": path_not_valid.format(path=Path(__file__).parent.parent.parent.parent.joinpath('geoformat/foo'))
    }
}

path_to_file_path_parameters = {
    0: {
        "path": Path(__file__).parent.parent.parent.joinpath('data').as_posix(),
        "geolayer_name": 'test',
        "overwrite": True,
        "add_extension": None,
        "return_value": Path(__file__).parent.parent.parent.joinpath('data/test')
    },
    1: {
        "path": Path(__file__).parent.parent.parent.joinpath('data/test').as_posix(),
        "geolayer_name": 'test',
        "overwrite": True,
        "add_extension": None,
        "return_value": Path(__file__).parent.parent.parent.joinpath('data/test')
    },
    2: {
        "path": Path(__file__).parent.parent.parent.joinpath('data/test').as_posix(),
        "geolayer_name": 'test',
        "overwrite": True,
        "add_extension": '.geojson',
        "return_value": Path(__file__).parent.parent.parent.joinpath('data/test.geojson')
    },
    3: {
        "path": Path(__file__).parent.parent.parent.joinpath('data'),
        "geolayer_name": 'test',
        "overwrite": True,
        "add_extension": None,
        "return_value": Path(__file__).parent.parent.parent.joinpath('data/test')
    },
    4: {
        "path": Path(__file__).parent.parent.parent.joinpath('data/test'),
        "geolayer_name": 'test',
        "overwrite": True,
        "add_extension": None,
        "return_value": Path(__file__).parent.parent.parent.joinpath('data/test')
    },
    5: {
        "path": Path(__file__).parent.parent.parent.joinpath('data/test'),
        "geolayer_name": 'test',
        "overwrite": True,
        "add_extension": '.geojson',
        "return_value": Path(__file__).parent.parent.parent.joinpath('data/test.geojson')
    }
}


def test_all():

    # add_extension_path
    print(test_function(add_extension_path, add_extension_path_parameters))

    # verify_input_path_is_file
    print(test_function(verify_input_path_is_file, verify_input_path_is_file_parameters))

    # path_to_file_path
    print(test_function(path_to_file_path, path_to_file_path_parameters))


if __name__ == '__main__':
    test_all()
