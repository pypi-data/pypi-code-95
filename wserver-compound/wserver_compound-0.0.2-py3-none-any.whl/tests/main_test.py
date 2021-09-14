from wserver_compound.main import WServer
from wserver_compound.tests import test_objects
from wserver_compound import functions
from wserver_compound import settings
import unittest


class MainTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(MainTest, self).__init__(*args, **kwargs)
        self.wserver = WServer(1488, test_objects.test_sql_shell)

    def test_get_act(self):
        resp = self.wserver.set_act(auto_id=None, gross=9000, tare=8000,
                                    cargo=1000,
                                    time_in='2021.08.24 23:31',
                                    time_out='2021.09.25 13:44:12',
                                    carrier_id=None,
                                    trash_cat_id=None, trash_type_id=None,
                                    polygon_id=None, operator=None, ex_id=1338)
        self.assertTrue(resp['status'])
        test_photo = functions.encode_photo(settings.TEST_PHOTO)
        photo_resp = self.wserver.set_photos(resp['info'], str(test_photo), 1)
        self.assertTrue(resp['photo_resp'])