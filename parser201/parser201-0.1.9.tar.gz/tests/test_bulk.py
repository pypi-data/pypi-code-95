#!/usr/bin/env python

"""Tests for `parser201` package using bulk parametrized tests"""

import pickle
import os
import lzma
from parser201.parser201 import LogParser

BENCH = os.path.join(os.path.dirname(__file__), 'benchmark.bin')

# --------------------------------------------------------------

# Generate and parameterize tests


def pytest_generate_tests(metafunc):
    with lzma.open(BENCH, 'rb') as f:
        L = pickle.load(f)
    metafunc.parametrize('testNode', L)

    return

# --------------------------------------------------------------
# Tests
# --------------------------------------------------------------

# IP address


def test_ip(testNode):
    assert LogParser(testNode['inputline']).ipaddress == testNode['ipaddress']

# User ID


def test_userid(testNode):
    assert LogParser(testNode['inputline']).userid == testNode['userid']

# User Name


def test_username(testNode):
    assert LogParser(testNode['inputline']).username == testNode['username']

# Timestamp


def test_timestamp(testNode):
    assert LogParser(testNode['inputline']).timestamp == testNode['timestamp']

# Request Line


def test_requestline(testNode):
    assert LogParser(testNode['inputline']
                     ).requestline == testNode['requestline']

# Status Code


def test_statuscode(testNode):
    assert LogParser(testNode['inputline']
                     ).statuscode == testNode['statuscode']

# Data Size


def test_datasize(testNode):
    assert LogParser(testNode['inputline']).datasize == testNode['datasize']

# Referrer


def test_referrer(testNode):
    assert LogParser(testNode['inputline']).referrer == testNode['referrer']

# User Agent


def test_useragent(testNode):
    assert LogParser(testNode['inputline']).useragent == testNode['useragent']

# Verify operation of the __str__ method


def test_str(testNode):
    assert str(LogParser(testNode['inputline'])) == testNode['string']

# --------------------------------------------------------------
