"""
Google OpenIdConnect:
    https://python-social-auth.readthedocs.io/en/latest/backends/google.html
"""
from social_core.backends.open_id_connect import OpenIdConnectAuth


class SteamIdOpenIdConnect(OpenIdConnectAuth):
    name = 'steamid-oidc'
    OIDC_ENDPOINT = 'https://steamid.steamforvietnam.net/oidc'
    ID_TOKEN_ISSUER = 'https://steamid.steamforvietnam.net/oidc'

    def user_data(self, access_token):
        """Return user data from Google API"""
        return self.get_json(
            'https://steamid.steamforvietnam.net/oidc/me',
            params={'access_token': access_token, 'alt': 'json'}
        )