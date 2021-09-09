from unittest import TestCase
from dk_api_helpers import *

class test_dk_api_helpers(TestCase):
    def test_getTypeOfTestLine(self):
        self.assertEquals(getTypeOfTestLine(''), None)
        self.assertEquals(getTypeOfTestLine('skjasdljkdskdsjlkdasjkl'), None)
        typ,val  = getTypeOfTestLine('Tests: Warning')
        self.assertEquals(typ, "Level")
        self.assertEquals(val, "Warning")
        typ,val  = getTypeOfTestLine('Step (put-dispense)')
        self.assertEquals(typ, "Step")
        self.assertEquals(val, "put-dispense")
        typ,val, desc  = getTypeOfTestLine('7. test-confirmationnum-mismatch-2010 (6624 num_dupes_confnum == 0)')
        self.assertEquals(typ, "Test")
        self.assertEquals(val, "test-confirmationnum-mismatch-2010")
        self.assertEquals(desc, "6624 num_dupes_confnum == 0")

    def test_parseTestString(self):
        with open('./tests/static/PlatformTestResults1.txt','r') as f:
            testData = f.read()
        expected = [(u'test_check_Veeva_Beghou_file_dates_invalid_date', u'check_Veeva_Beghou_file_dates', u'Passed', u'0 count_Veeva_Beghou_tables_invalid_date == 0'), (u'test_check_Veeva_Beghou_duplicate_file_types', u'check_Veeva_Beghou_file_dates', u'Passed', u'0 count_Veeva_Beghou_duplicate_file_types == 0'), (u'test_check_Veeva_Beghou_files', u'check_Veeva_Beghou_file_dates', u'Passed', u'12 count_Veeva_Beghou_files == 12'), (u'test_create_redshift_schema', u'create_schema', u'Passed', u'0 count_tables_in_schema == 0'), (u'test_copy_Veeva_HCPS', u'put_Veeva_Beghou', u'Passed',u'246721 count_Veeva_HCPS > 0'), (u'test_copy_Veeva_AccountGroupOverview', u'put_Veeva_Beghou', u'Passed', '929 count_Veeva_AccountGroupOverview > 0'), (u'test_copy_Veeva_Interaction', u'put_Veeva_Beghou', u'Passed', u'472529 count_Veeva_Interaction > 0'), (u'test_copy_Veeva_AddressChanges', u'put_Veeva_Beghou', u'Passed', '10870 count_Veeva_AddressChanges > 0'), (u'test_copy_Veeva_Pathways', u'put_Veeva_Beghou', u'Passed', '1428 count_Veeva_Pathways > 0')]
        self.assertListEqual(parseTestString(testData), expected)
