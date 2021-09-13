# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.batchnavigator
#
# lazr.batchnavigator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.batchnavigator is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.batchnavigator. If not, see <http://www.gnu.org/licenses/>.
"Test harness for doctests."

from __future__ import print_function

__metaclass__ = type
__all__ = [
    'load_tests',
    ]

import atexit
import doctest
import os
import pkg_resources

DOCTEST_FLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_NDIFF)


def test_raises(exc_class, method, *args, **kwargs):
    try:
        method(*args, **kwargs)
    except Exception as e:
        if isinstance(e, exc_class):
            print(e)
            return
        raise
    raise Exception("Expected exception %s not raised" % exc_class)


def load_tests(loader, tests, pattern):
    """Load all the doctests."""
    atexit.register(pkg_resources.cleanup_resources)
    doctest_files = []
    if pkg_resources.resource_exists('lazr.batchnavigator', 'docs'):
        for name in pkg_resources.resource_listdir(
                'lazr.batchnavigator', 'docs'):
            if name.endswith('.rst'):
                doctest_files.append(
                    os.path.abspath(
                        pkg_resources.resource_filename(
                            'lazr.batchnavigator', 'docs/%s' % name)))
    tests.addTest(doctest.DocFileSuite(
        *doctest_files, module_relative=False, optionflags=DOCTEST_FLAGS,
        globs={
            "print_function": print_function,
            "test_raises": test_raises,
            }))
    return tests
