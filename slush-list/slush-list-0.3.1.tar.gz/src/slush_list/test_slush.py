"""
Модуль тестирования класса Slush
"""

import unittest
from slush_list import slush_list
from slush_list import main


UPLOAD_FOLDER = './group_lists'


class TestFunctions(unittest.TestCase):
    """Класс тестирования методов класса Students"""

    def setUp(self):
        """Начальные параметры"""

        self.test_slush = slush_list.Students(year="2018", number="3")
        self.test_slush.read_slush(f"{UPLOAD_FOLDER}/2018-3.txt")

        self.test_slush2 = slush_list.Students(year="2017", number="3")
        self.test_slush2.read_slush(f"{UPLOAD_FOLDER}/2018-3.txt")

    def test_read_list(self):
        """Тестирование чтения списка"""

        self.assertTrue(self.test_slush.read_slush(f"{UPLOAD_FOLDER}/2018-3.txt"))

    def test_load_list(self):
        """Тестирование загрузки списка"""

        self.assertTrue(self.test_slush.load_slush())

    def test_relogin(self):
        """Тестирование функции замены login слушателя"""

        self.test_slush.load_slush()

        change = ['nazar_lex', 'nazarov']

        self.assertTrue(self.test_slush.relogin(change[0], change[1]))

    def test_rename(self):
        """Тестирование функции замены fullname слушателя"""

        self.test_slush.load_slush()

        change = ['nazar_lex', '2018-3-21-nazarov']

        self.assertTrue(self.test_slush.rename(change[0], change[1]))

    def test_check(self):
        """Тестирование функции проверки fullname слушателей"""

        self.test_slush.load_slush()

        self.assertTrue(self.test_slush.check_name("2018-3-20-naz"))

    def test_get_stud(self):
        """Тестирование функции поиска слушателя по шаблону"""

        main.groups_dir[self.test_slush.load_slush()] = self.test_slush
        self.assertTrue(main.get_stud("2018-3-20-naz"))

    def test_get_repos(self):
        """Тестирование функции получения списка репозиториев"""

        main.groups_dir[self.test_slush.load_slush()] = self.test_slush
        self.assertTrue(main.get_repos("2018-3", "timp", '-r'))
        self.assertTrue(main.get_repos("2018-3", "timp/roi", '-g'))


class TestFunctionsRaises(unittest.TestCase):
    """Класс тестирования исключений в методах класса Students"""

    def setUp(self):
        """Начальные параметры"""

        self.test_slush_raises = slush_list.Students(year="2018", number="3")
        self.test_slush_raises.read_slush(f"{UPLOAD_FOLDER}/2018-3.txt")

    def test_raise_load(self):
        """Тестирование исключения в функции загрузки списка"""

        self.assertRaises(FileNotFoundError, self.test_slush_raises.read_slush, "123.txt")

    def test_raise_relog(self):
        """Тестирование исключения в функции изменения login слушателя"""

        self.assertRaises(ValueError, self.test_slush_raises.relogin, "123", "nazarov")

    def test_raise_rename(self):
        """Тестирование исключения в функции изменения fullname слушателя"""

        self.assertRaises(Exception, self.test_slush_raises.rename, "123", "2018-3-21-nazarov")


class FlaskTestCase(unittest.TestCase):
    """Класс тестирования web-приложения"""

    def setUp(self):
        """Начальные параметры"""

        main.app.config['TESTING'] = True
        self.app = main.app.test_client(self)

    def search_slush(self, fullname):
        """Вспомогательная функция для тестирования поиска слушателя в web-приложении"""

        return self.app.post('/', data=dict(
            fullname=fullname,
        ), follow_redirects=True)

    def load(self, year, number, file):
        """Вспомогательная функция для тестирования загрузки группы в web-приложении"""

        return self.app.post('/load', data=dict(
            year=year,
            number=number,
            file=file
        ), follow_redirects=True)

    def relogin(self, group, old_login, new_login):
        """Вспомогательная функция для тестирования изменения login в web-приложении"""

        return self.app.post('/relogin', data=dict(
            group=group,
            old_login=old_login,
            new_login=new_login
        ), follow_redirects=True)

    def rename(self, group, login, new_name):
        """Вспомогательная функция для тестирования изменения fullname в web-приложении"""

        return self.app.post('/rename', data=dict(
            group=group,
            login=login,
            new=new_name
        ), follow_redirects=True)

    def delete_group(self, group):
        """Вспомогательная функция для тестирования удаления группы в web-приложении"""

        return self.app.post('/delete', data=dict(
            group=group,
        ), follow_redirects=True)

    def repos(self, choice, group, repo_name):
        """Вспомогательная функция для тестирования отображения repo в web-приложении"""

        return self.app.post('/repos', data=dict(
            choice=choice,
            group=group,
            repo_name=repo_name
        ), follow_redirects=True)

    def test_index(self):
        """Тестирование корректного запуска web-приложения"""

        response = self.app.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

        response = self.search_slush('')
        self.assertIn('fullname не введен'.encode(), response.data)

        response = self.search_slush('321123')
        self.assertIn('Неверно введенный fullname'.encode(), response.data)

        response = self.search_slush('2020-3-21-naz')
        self.assertIn('ullname не найден'.encode(), response.data)

    def test_load(self):
        """Тестирование загрузки группы в web-приложении"""

        response = self.app.get('/load', content_type='html/text')
        self.assertEqual(response.status_code, 200)

        response = self.load(None, '3', f"{UPLOAD_FOLDER}/2018-3.txt")
        self.assertIn('Не указан год поступления'.encode(), response.data)

        response = self.load('2018', '', f"{UPLOAD_FOLDER}/2018-3.txt")
        self.assertIn('Не указан порядковый номер группы'.encode(), response.data)

        response = self.load('2018', '3', '')
        self.assertIn('Неверный формат файла'.encode(), response.data)

    def test_relogin(self):
        """Тестирование изменения login в web-приложении"""

        response = self.app.get('/relogin', content_type='html/text')
        self.assertEqual(response.status_code, 200)

        self.assertTrue(self.relogin('2018-3', 'nazar_lex', 'nazarov'))
        response = self.relogin('2018-3', 'nazarov', 'nazar_lex')
        self.assertIn('Login изменен'.encode(), response.data)

        response = self.relogin('2018-3', 'nazarov', 'nazar_lex')
        self.assertIn('Введенный login отсутствует в списке'.encode(), response.data)

        response = self.relogin(None, 'nazar_lex', 'nazarov')
        self.assertIn('Не указана группа'.encode(), response.data)

        response = self.relogin('2018-3', '', 'nazarov')
        self.assertIn('Не указан старый login'.encode(), response.data)

        response = self.relogin('2018-3', 'nazar_lex', '')
        self.assertIn('Не указан новый login'.encode(), response.data)

    def test_rename(self):
        """Тестирование изменения fullname в web-приложении"""

        response = self.app.get('/rename', content_type='html/text')
        self.assertEqual(response.status_code, 200)

        self.assertTrue(self.rename('2018-3', 'nazar_lex', '2018-3-33-nazarov'))
        response = self.rename('2018-3', 'nazar_lex', '2018-3-20-naz')
        self.assertIn('Fullname изменен'.encode(), response.data)

        response = self.rename('2018-3', 'nazar', '2018-3-20-naz')
        self.assertIn('Введенный login отсутствует в списке'.encode(), response.data)

        response = self.rename(None, 'nazar_lex', '2018-3-20-naz')
        self.assertIn('Не указана группа'.encode(), response.data)

        response = self.rename('2018-3', '', '2018-3-20-naz')
        self.assertIn('Не указан login'.encode(), response.data)

        response = self.rename('2018-3', 'nazar_lex', '')
        self.assertIn('Не указан новый fullname'.encode(), response.data)

        response = self.rename('2018-3', 'nazar_lex', '2019-3-33-naz')
        self.assertIn('Не верно указан год поступления в новом fullname'.encode(), response.data)

        response = self.rename('2018-3', 'nazar_lex', '2018-4-33-naz')
        self.assertIn('Не верно указан порядковый номер группы в новом fullname'.encode(), response.data)

    def test_delete_group(self):
        """Тестирование удаления группы в web-приложении"""

        response = self.app.get('/delete', content_type='html/text')
        self.assertEqual(response.status_code, 200)

        response = self.delete_group('')
        self.assertIn('Не указана группа'.encode(), response.data)

        response = self.delete_group('2020-3')
        self.assertIn('Введенный номер группы отсутствует в списке'.encode(), response.data)

    def test_repos(self):
        """Тестирование отображения repo в web-приложении"""

        response = self.app.get('/repos', content_type='html/text')
        self.assertEqual(response.status_code, 200)

        response = self.repos(None, '2018-3', 'timp')
        self.assertIn('Не указана операция'.encode(), response.data)

        response = self.repos('repo', '', 'timp')
        self.assertIn('Не указана группа'.encode(), response.data)

        response = self.repos('repo', '2018-3', '')
        self.assertIn('Не указано имя репозитория или группы'.encode(), response.data)


if __name__ == '__main__':
    unittest.main()
