import unittest
from typing import List

import Connector


class PRPConnectorTest(unittest.TestCase):
    connection: Connector.PRPConnector = Connector.PRPConnector('admin', 'adminTest', 'https://marblch.pythonanywhere.com/')

    def test_test_message(self):
        response: dict = PRPConnectorTest.connection.test_message()
        self.assertEqual({'message': 'success'}, response)

    def test_login(self):
        response: int = PRPConnectorTest.connection.get_user()
        self.assertEqual(1, response)

    def test_get_index(self):
        response: List[dict] = PRPConnectorTest.connection.get_all('todo')
        self.assertEqual(list, type(response))

    def test_write_delete(self):
        write_response = PRPConnectorTest.connection.write_item('todo', 'title=test&description=test description')
        self.assertEqual({'message': 'Entry added successfully', 'type': 'success'}, write_response)
        read_response_1: List[dict] = PRPConnectorTest.connection.get_item('todo', 'title', 'test')
        self.assertEqual('test', read_response_1[0]['title'])
        self.assertEqual('test description', read_response_1[0]['description'])
        item_id: int = int(read_response_1[0]['id'])
        delete_response = PRPConnectorTest.connection.delete_item('todo', item_id)
        self.assertEqual({'message': 'Entry deleted successfully', 'type': 'success'}, delete_response)
        read_response_2 = PRPConnectorTest.connection.get_item('todo', 'title', 'test')
        self.assertEqual([], read_response_2)

    def test_write_update_delete(self):
        PRPConnectorTest.connection.write_item('todo', 'title=test&description=test description')
        read_response_1: List[dict] = PRPConnectorTest.connection.get_item('todo', 'title', 'test')
        item_id: int = int(read_response_1[0]['id'])
        update_response: dict = PRPConnectorTest.connection.update_item('todo', 'id={id}&title=update&description=updated description'.format(id=str(item_id)))
        self.assertEqual('success', update_response['type'])
        read_response_2: List[dict] = PRPConnectorTest.connection.get_item('todo', 'title', 'test')
        self.assertEqual([], read_response_2)
        read_response_3: List[dict] = PRPConnectorTest.connection.get_item('todo', 'title', 'update')
        self.assertEqual('updated description', read_response_3[0]['description'])
        self.assertEqual(item_id, read_response_3[0]['id'])
        PRPConnectorTest.connection.delete_item('todo', item_id)


class ToDoConnectorTest(unittest.TestCase):
    connection: Connector.ToDoConnector = Connector.ToDoConnector('admin', 'adminTest', 'https://marblch.pythonanywhere.com/')

    def test_get_index(self):
        response: List[dict] = ToDoConnectorTest.connection.get_all_todo()
        self.assertEqual(list, type(response))

    def test_write_update_delete(self):
        ToDoConnectorTest.connection.write_item_todo(title='test', description='test description')
        read_response_1: List[dict] = ToDoConnectorTest.connection.get_item_todo(key='title', value='test')
        item_id: int = int(read_response_1[0]['id'])
        update_response: dict = ToDoConnectorTest.connection.update_item_todo(item_id=item_id, title='update', description='updated description')
        self.assertEqual('success', update_response['type'])
        read_response_2: List[dict] = ToDoConnectorTest.connection.get_item_todo(key='title', value='test')
        self.assertEqual([], read_response_2)
        read_response_3: List[dict] = ToDoConnectorTest.connection.get_item_todo(key='title', value='update')
        self.assertEqual('updated description', read_response_3[0]['description'])
        self.assertEqual(item_id, read_response_3[0]['id'])
        ToDoConnectorTest.connection.delete_item_todo(item_id)
