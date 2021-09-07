from moosetools import __version__, __app__

import pkg_resources

# https://openlibrary.org/developers/api - books, authors, works, etc
# https://www.abstractapi.com/holidays-api - world-wide holidays
# https://unixtime.co.za/ - time stamp convertor


def test_version():
    assert __version__ == pkg_resources.get_distribution(__app__).version
