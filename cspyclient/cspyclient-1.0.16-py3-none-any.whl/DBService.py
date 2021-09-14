import requests

from .User import User

class DBService():
    '''
    DBService class is to help data adminstrators access and interact with the database

    *Users can access to database
    *Database will then indentify and check the authentication of users
    *Users can modify and interact with database based on their authorization. 

    Parameter: base_url - link to database
    access_token- token for accessing database (if applicable)
    '''   
    def __init__(self, base_url, access_token=None):
        self.headers = {} if access_token is None else {'Authorization': f'Bearer {access_token}'}
        self.base_url = base_url
        self.current_user = {}

    def __repr__(self):
        return '<DBService>'

    def auth(self, google_access_token='', user=None):
        '''
        auth: Authenticate access to google data base (including the action of examinee entering the test)
        parameter: google_access_token - token for accessing database (if applicable)
        user-user information (if there is no token)
        '''
        if ((google_access_token) and (type(google_access_token) is str)):
            response = requests.post(f'{self.base_url}/auth/login/google', {'access_token': google_access_token}).json()
        elif ((user) and (type(user) is User)):
            response = requests.post(f'{self.base_url}/auth/login', 
                                     {'email': getattr(user, 'email', ''), 
                                      'password': getattr(user, 'password', '')}
                                    ).json()
        else:
            print('ERROR: Credential Information required')
            return
        
        if ('success' in response):
            self.current_user = User(response['data']['user'])
            access_token = response['data']['accessToken']
            self.headers['Authorization'] = f'Bearer {access_token}'
            print(f"Welcome {self.current_user.email}!")
        else:
            print(f"ERROR: {response['errors']['message']}")
    
    def get(self, path):
        '''
        get: Get data from data base
        parameter: path- path leads to data (? not sure if path is fixed or depending on datum)
        '''
        response = requests.get(self.base_url + path, headers=self.headers).json()
        if ('success' in response):
            return response['data']
        else:
            print(f"ERROR: {response['errors']['message']}")
            return None

    def post(self, path, data):
        '''
        post: Add a new datum to database
        parameter: data- a data to modify on
        '''
        response = requests.post(self.base_url + path, json=data, headers=self.headers).json()
        if ('success' in response):
            if ('message' in response):
                print(response['message'])
            return response['data']
        else:
            print(f"ERROR: {response['errors']['message']}")
            return None

    def put(self, path, data):
        '''
        put: Modify a datum on databse
        parameter: data- a data to put
        '''
        response = requests.put(self.base_url + path, json=data, headers=self.headers).json()
        if ('success' in response):
            print(response['message'])
            return response['data']
        else:
            print(f"ERROR: {response['errors']['message']}")
            return None
    
    def delete(self, path):
        '''
        delete: Delete a datum in database
        parameter: path- path leads to data
        '''
        response = requests.delete(self.base_url + path, headers=self.headers).json()
        if ('success' in response):
            print(response['message'])
        else:
            print(f"ERROR: {response['errors']['message']}")
            
API_URL = 'https://cs-platform-306304.et.r.appspot.com/api'
db = DBService(API_URL)