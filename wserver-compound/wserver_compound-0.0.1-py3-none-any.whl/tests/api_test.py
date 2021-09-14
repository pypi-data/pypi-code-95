""" В модуле содержится WServer с QPI и тестовый QDK для работы с ним. """
import unittest
from wserver_compound.main import WServer
from wserver_compound.tests import test_objects
from qdk.main import QDK


class ApiTest(unittest.TestCase):
    """ Тестовый класс """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wserver = WServer(9996, dbname='gdb', user='watchman',
                               password='hect0r1337', host='192.168.100.118')
        self.qdk = QDK('localhost', 9996)
        self.qdk.make_connection()

    def test_hello_world(self):
        """ Тестируем базовую работу QSCT. """
        self.qdk.execute_method(method_name='hello_world')
        response = self.qdk.get_data()
        self.assertTrue(response['status'],
                        response['info']['status'])

    def test_add_act(self):
        """ Тестируем добавление акта """
        self.qdk.execute_method('add_act', auto_id=None, gross=9000, tare=8000,
                                    cargo=1000,
                                    time_in='2021.08.24 23:31',
                                    time_out='2021.09.25 13:44:12',
                                    carrier_id=None,
                                    trash_cat_id=None, trash_type_id=None,
                                    polygon_id=None, operator=None, ex_id=1338)
        response = self.qdk.get_data()
        self.assertTrue(response['status'] and
                        response['core_method'] == 'add_act' and
                        isinstance(response['info'], int))

    def test_some(self):
        self.qdk.execute_method('test_some')
        response = self.qdk.get_data()
        print("RESP", response)


if __name__ == "__main__":
    unittest.main()