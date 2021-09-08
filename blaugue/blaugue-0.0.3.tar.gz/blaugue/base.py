import requests


class BlaugueBase:

    def __init__(self, user, password):
        # self.base_url = 'http://127.0.0.1:2000' # local tests
        self.base_url = 'http://blaugue.camponovo.xyz'
        self.api_url = 'http://127.0.0.1:2000/api' # local tests
        # self.api_url = 'http://blaugue.camponovo.xyz/api'
        self.headers = {'blaugueathoken': 'no', 'blaugueuser': user}
        self.user = user
        self.password = password

    @property
    def search_url(self):
        return self.api_url + '/search/{}'

    @property
    def user_url(self):
        return self.api_url + '/user/{}'

    @property
    def last_posts_url(self):
        return self.api_url + '/last-posts'

    @property
    def post_url(self):
        return self.api_url + '/post/{}'

    @property
    def chat_url(self):
        return self.api_url + '/chat/{}'

    @property
    def url(self):
        return self.api_url

    @property
    def baseurl(self):
        return self.base_url

    def set_token(self):
        self.headers['blaugueathoken'] = self.get_token()
        self.headers['blaugueuser'] = self.user

    def isright(self):
        try:
            return self.request(self.api_url + '/auth/verify').json()['account_status']
        except:
            raise BlaugueError('Invalid Account informations !')

    def get_password(self):
        return bytes(self.request(self.api_url + '/get_password').content)

    def get_token(self):
        return self.request(self.api_url + '/auth/' + self.user + '/' + self.password).content.decode()

    def request(self, url):
        return requests.get(url, headers=self.headers)


class BlaugueError(Exception):
    """
    BlaugueError class
    """
