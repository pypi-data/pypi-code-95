# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.lifecycle
#
# lazr.lifecycle is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.lifecycle is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.lifecycle.  If not, see <http://www.gnu.org/licenses/>.
"Test harness for doctests."

# pylint: disable-msg=E0611,W0142

from __future__ import print_function

__metaclass__ = type
__all__ = [
    'load_tests',
    ]

import atexit
import doctest
import os
from pkg_resources import (
    resource_filename, resource_exists, resource_listdir, cleanup_resources)
import warnings

DOCTEST_FLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_NDIFF)


def raise_warning(message, category=None, stacklevel=1):
    if category is None:
        kind = 'UserWarning'
    else:
        kind = category.__class__.__name__

    print("%s: %s" % (kind, message))


def setUp(test):
    """Makes any warning an error."""
    test.globs['print_function'] = print_function
    test.globs['saved_warn'] = warnings.warn
    warnings.warn = raise_warning


def tearDown(test):
    """Reset the warnings."""
    warnings.warn = test.globs['saved_warn']


def find_doctests(suffix):
    """Find doctests matching a certain suffix."""
    doctest_files = []
    # Match doctests against the suffix.
    if resource_exists('lazr.lifecycle', 'docs'):
        for name in resource_listdir('lazr.lifecycle', 'docs'):
            if name.endswith(suffix):
                doctest_files.append(
                    os.path.abspath(
                        resource_filename('lazr.lifecycle', 'docs/%s' % name)))
    return doctest_files


def load_tests(loader, tests, pattern):
    """Load all the doctests."""
    atexit.register(cleanup_resources)
    tests.addTest(doctest.DocFileSuite(
        *find_doctests('.rst'),
        module_relative=False, setUp=setUp, tearDown=tearDown,
        optionflags=DOCTEST_FLAGS))
    return tests
