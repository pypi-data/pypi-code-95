""" Модуль содержит тесты для всех функций из модуля functions,
используемых в методах WServer """
import datetime
import unittest
from wserver_compound import functions
from wserver_compound import settings
from wserver_compound.tests import test_objects


class FunctionsTest(unittest.TestCase):
    """ TestCase for functions """

    def test_format_time(self):
        """ Тестирование фунцкии по форматированию времени акта"""
        response = functions.format_act_time('2021.08.24 01:55:38')
        self.assertTrue(isinstance(response, datetime.datetime))

    def test_generate_photo_name(self):
        """ Тестирование генератора названия фотографии, сохраняемых на винте
        """
        record_id = 555
        response_rec_id = functions.generate_photo_name(record_id)
        self.assertTrue(settings.PHOTOS_DIR in response_rec_id)
        response_no_arg = functions.generate_photo_name()
        self.assertTrue(str(None) in response_no_arg)

    def test_save_photo_database(self):
        """ Тестирование функции сохранения данных о фото в базу данных """
        response = functions.save_photo_database(test_objects.test_sql_shell,
                                                 None,
                                                 'RANDOM_PATH',
                                                 None)
        self.assertTrue(response['status'], isinstance(response['info'], int))

    def test_encode_photo(self):
        """ Тесты на кодировку фото в base64, декодировку и сравнение """
        photo_path = settings.TEST_PHOTO
        photo_obj = functions.encode_photo(photo_path)
        self.assertTrue(isinstance(photo_obj, bytes))
        photo_bytes_str = str(photo_obj)
        new_photo_path = functions.save_photo(photo_bytes_str,
                                              functions.generate_photo_name(1))
        new_photo_obj = functions.encode_photo(new_photo_path)
        self.assertEqual(photo_obj, new_photo_obj)

    def test_get_user_ip(self):
        correct_response = functions.get_user_ip(test_objects.test_sql_shell,
                                                 9)
        self.assertTrue(isinstance(correct_response, str))
        incorrect_response = functions.get_user_ip(test_objects.test_sql_shell,
                                                   1333)
        self.assertTrue(not incorrect_response)

    def test_get_all_polygon_ids(self):
        response = functions.get_all_polygon_ids(test_objects.test_sql_shell)
        print(response)

    def test_set_record_unactive(self):
        response = functions.set_record_unactive(test_objects.test_sql_shell,
                                                 'auto', 572159, active=True)

if __name__ == '__main__':
    unittest.main()
