import pytest

from stag.ecs import Page, Metadata, Path
from stag.plugins._jinja_functions import sorted_pages


@pytest.fixture
def files():
    return [
        Page("/static.txt"),
        Page("/bar", metadata=Metadata(date="2021-08-09")),
        Page("/empty", metadata=Metadata()),
        Page("/foo", metadata=Metadata(date="2021-08-10")),
        Page("/baz", metadata=Metadata(date="2020-11-11")),
    ]


def test_sort_default_key(files):
    srt = sorted_pages(files)
    assert srt == [files[1], files[4], files[2], files[3], files[0]]


def test_sort_default_key_reverse(files):
    srt = sorted_pages(files, reverse=True)
    assert srt == [files[0], files[3], files[2], files[4], files[1]]


def test_sort_date(files):
    srt = sorted_pages(files, key="date")
    assert srt[0] == files[4]
    assert srt[1] == files[1]
    assert srt[2] == files[3]
    # last 2 elements don't have date, so they are considered equal and their
    # order is undefined


def test_sort_date_reverse(files):
    srt = sorted_pages(files, key="date", reverse=True)
    # first 2 elements don't have date, so they are considered equal and their
    # order is undefined
    assert srt[2] == files[3]
    assert srt[3] == files[1]
    assert srt[4] == files[4]
