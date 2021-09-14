'''
Class user
'''
import requests
from .user import User #pylint: disable=[relative-beyond-top-level]

class DBService():
    '''
    DBService class is to help data adminstrators access and interact with the database

    *Users can access to database
    *Database will then indentify and check the authentication of users
    *Users can modify and interact with database based on their authorization.

    Parameter: __base_url - link to database
    access_token- token for accessing database (if applicable)
    '''
    def __init__(self, base_url, access_token=None):
        self.__headers = {} if access_token is None else {'Authorization': f'Bearer {access_token}'}
        self.__base_url = base_url
        self.__current_user = {}

    def __repr__(self):
        return '<DBService>'

    def colab_google_login(self):
        try:
            from google.colab import auth
            from oauth2client.client import GoogleCredentials
        except:
            print('Only avalable on Google Colab')
            return
        auth.authenticate_user()
        google_access_token = GoogleCredentials.get_application_default().get_access_token().access_token
        self.auth(google_access_token=google_access_token)

    def auth(self, google_access_token='', user=None):
        '''
        auth: Authenticate access to google data base (including the action of examinee entering
        the test)
        parameter: google_access_token - token for accessing database (if applicable)
        user-user information (if there is no token)
        '''
        if ((google_access_token) and (type(google_access_token) is str)):
            response = (requests.post(f'{self.__base_url}/auth/google/token',
                    {'access_token': google_access_token}).json())
        elif ((user) and (type(user) is User)):
            response = requests.post(f'{self.__base_url}/auth/login',
                                     {'email': getattr(user, 'email', ''),
                                      'password': getattr(user, 'password', '')}
                                    ).json()
        else:
            print('ERROR: Credential Information required')
            return
        if response['statusCode'] == 'SUCCESS':
            self.__current_user = User(response['data']['user'])
            access_token = response['data']['accessToken']
            self.__headers['Authorization'] = f'Bearer {access_token}'
            print(f"Welcome {self.__current_user.email}!")
        else:
            print(f"ERROR: {response['message']}")

    def is_user(self):
        if self.__headers and self.__current_user:
            return True
        return False

    def get_current_user_id(self):
        if not self.is_user():
            return False
        return self.__current_user._id

    def get_current_user_name(self):
        if not self.is_user():
            return False
        return self.__current_user.name

    def get(self, path, query_params=None):
        '''
        get: Get data from data base
        parameter: path- path leads to data (? not sure if path is fixed or depending on datum)
        '''
        response = requests.get(self.__base_url + path, headers=self.__headers, params=query_params).json()
        if response['statusCode'] == 'SUCCESS':
            return response['data']
        else:
            print(f"ERROR: {response['message']}")
            return None

    def post(self, path, data):
        '''
        post: Add a new datum to database
        parameter: data- a data to modify on
        '''
        response = requests.post(self.__base_url + path, json=data, headers=self.__headers).json()
        if response['statusCode'] == 'SUCCESS':
            if 'message' in response:
                print(response['message'])
            return response['data']
        else:
            print(f"ERROR: {response['message']}")
            return None

    def put(self, path, data):
        '''
        put: Modify a datum on databse
        parameter: data- a data to put
        '''
        response = requests.put(self.__base_url + path, json=data, headers=self.__headers).json()
        if response['statusCode'] == 'SUCCESS':
            print(response['message'])
            return response['data']
        else:
            print(f"ERROR: {response['message']}")
            return None

    def delete(self, path):
        '''
        delete: Delete a datum in database
        parameter: path- path leads to data
        '''
        response = requests.delete(self.__base_url + path, headers=self.__headers).json()
        if response['statusCode']=='success':
            print(response['message'])
        else:
            print(f"ERROR: {response['message']}")


