'''
User class
'''
from .utils import Utils #pylint: disable=[relative-beyond-top-level]


class User():
    '''
    User class is to create object for user (examinee) with corresponding information.

    * Users register their personal information to do their test
    * The system will automatically save their information to the database for reporting resutls

    Parameter: data - datum of user with all information in: ['_id', 'name', 'email', 'password',
    'created_by', 'updated_by', 'created_at', 'updated_at']
    '''
    def __init__(self, data):
        self.ATTRIBUTES = ['_id', 'name', 'email', 'password', 'created_by', 'updated_by',
        'created_at', 'updated_at']
        for key in data.keys():
            snake_key = Utils.to_snake_case(key)
            if snake_key in self.ATTRIBUTES:
                setattr(self, snake_key, data[key])

    def __repr__(self):
        user_id = getattr(self, '_id', '')
        name = getattr(self, 'name', '')
        email = getattr(self, 'email', '')
        return f'User:\n _id: {user_id}; Name: {name}; Email: {email}'

    def to_json(self):
        '''
        to_json: convert data to json standard
        '''
        return {Utils.to_camel_case(key):getattr(self, key) for key in self.ATTRIBUTES
            if getattr(self, key, None)}

    @classmethod
    def register(cls, db_service, name, email, password):
        '''
        register: register user to the database
        parameter: db_service - database service class to add
        name, email, password- information to add
        '''
        data = {"name":name, "email":email, 'password': password}
        res = db_service.post('/auth/register', data)
        return res
