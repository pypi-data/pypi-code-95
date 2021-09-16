import pytest
import pathlib
import re
import os
from nbconvert.preprocessors import ExecutePreprocessor

# https://stackoverflow.com/questions/7012921/recursive-grep-using-python
def findfiles(path, regex):
    regObj = re.compile(regex)
    res = []
    for root, dirs, fnames in os.walk(path):
        for fname in fnames:
            if regObj.match(fname):
                res.append(os.path.join(root, fname))
    return res


@pytest.fixture(params=findfiles(pathlib.Path(__file__).parent.parent.absolute(), r'example.*\.(py)$'))
def example_filename(request):
    return request.param


def test_run_examples(example_filename):
    with open(example_filename, encoding="utf8") as f:
        exec(f.read())
