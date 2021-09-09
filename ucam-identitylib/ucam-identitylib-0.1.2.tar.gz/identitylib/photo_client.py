from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from functools import lru_cache
from requests import auth


class NoSuchPhotoException(Exception):
    def __init__(self):
        super().__init__('No photo found for query criteria')


class PhotoClient:
    """
    A client which allows information to be fetched from the University Photo API.

    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = 'https://api.apps.cam.ac.uk/photo/v1beta1/',
        token_url: str = 'https://api.apps.cam.ac.uk/oauth/client_credential/accesstoken'
    ):
        self.client_id = client_id
        self.client_secret = client_secret

        self.base_url = base_url.rstrip('/')
        self.token_url = token_url

    @property
    @lru_cache()
    def session(self):
        """
        Lazy-init a OAuth2-wrapped session and fetch a token before it's used.

        """

        client = BackendApplicationClient(client_id=self.client_id)
        session = OAuth2Session(client=client)

        session.fetch_token(
            token_url=self.token_url,
            auth=auth.HTTPBasicAuth(self.client_id, self.client_secret)
        )
        return session

    def get_transient_image_url(self, photo_id: str):
        """
        Returns a transient image url which can be used to by unauthenticated clients
        to fetch the url of the given photo id.

        """
        response = self.session.get(
            f'{self.base_url}/photos/{photo_id}/content', allow_redirects=False
        )
        if response.status_code == 404:
            raise NoSuchPhotoException()
        response.raise_for_status()

        if not response.headers.get('Location'):
            raise RuntimeError('Photo API did not return a transient image url within redirect')

        return response.headers['Location']
