###############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

# Uncomment to disable the tests.
#__test__ = False

from LbNightlyTools.Utils import retry_call, _retry_wrapper


def test_retry_call():
    try:
        retry_call(['false'], retry=3)
        assert False, "exception expected"
    except RuntimeError, exc:
        assert str(exc) == "the command ['false'] failed 3 times"


def test_retry_wrapper():
    import time

    class F(object):
        def __init__(self, fail_count=3):
            self.counter = fail_count + 1

        def __call__(self):
            self.counter -= 1
            return self.counter

    f = F()
    f.__name__ = 'f'

    rf = _retry_wrapper(f, lambda r: r == 0)

    start = time.time()
    rf(retry=5, retry_sleep=1)
    assert time.time() - start >= 2
