# -*- coding: utf-8 -*-

import unittest

from yamlns.testutils import assertNsEqual

# Readable verbose testcase listing
unittest.TestCase.__str__ = unittest.TestCase.id

def _inProduction():
    import erppeek_wst
    import dbconfig
    c = erppeek_wst.ClientWST(**dbconfig.erppeek)
    c.begin()
    destructive_testing_allowed = c._execute(
        'res.config', 'get', 'destructive_testing_allowed', False)
    c.rollback()
    c.close()

    if destructive_testing_allowed: return False
    return True

def destructiveTest(decorated):
    return unittest.skipIf(_inProduction(),
        "Destructive test being run in a production setup!!")(decorated)



# vim: ts=4 sw=4 et
