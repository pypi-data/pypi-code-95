# Copyright 20010 Canonical Ltd.  All rights reserved.

"""Test harness for LAZR doctests."""

from __future__ import absolute_import, print_function

__metaclass__ = type
__all__ = []

import os
import doctest
from pkg_resources import resource_filename

from van.testing.layer import zcml_layer, wsgi_intercept_layer
from zope.testing import renormalizing

from lazr.restful.example.base.tests.test_integration import (
    CookbookWebServiceTestPublication, DOCTEST_FLAGS)
from lazr.restful.testing.webservice import WebServiceApplication


checker = renormalizing.OutputChecker()


class FunctionalLayer:
    allow_teardown = False
    zcml = os.path.abspath(resource_filename(
        'lazr.restful.example.base_extended', 'site.zcml'))
zcml_layer(FunctionalLayer)


class WSGILayer(FunctionalLayer):
    @classmethod
    def make_application(self):
        return WebServiceApplication({}, CookbookWebServiceTestPublication)
wsgi_intercept_layer(WSGILayer)


def load_tests(loader, tests, pattern):
    """See `zope.testing.testrunner`."""
    doctest_files = ['../README.txt']
    globs = {
        'absolute_import': absolute_import,
        'print_function': print_function,
        }
    suite = doctest.DocFileSuite(
        *doctest_files, optionflags=DOCTEST_FLAGS, globs=globs,
        checker=checker)
    suite.layer = WSGILayer
    tests.addTest(suite)
    return tests
