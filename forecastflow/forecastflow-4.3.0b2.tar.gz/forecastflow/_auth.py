import json
import logging

import requests

from . import config

logger = logging.Logger(__name__)


def sign_in_with_password(email: str, password: str) -> dict:
    """
    Sign in with e-mail and password by using firebase REST API.
    Document is here https://firebase.google.com/docs/reference/rest/auth/#section-sign-in-email-password .

    Args:
        email:
            User's e-mail to sign in.

        password:
            Password for sign in.

    Returns:
        Dictionary object. keys = ['kind',
            'localId', 'email', 'displayName', 'idToken', 'registered', 'refreshToken', 'expiresIn']
    """
    api_key = config.firebase['apiKey']
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    data = {'email': email, 'password': password, 'returnSecureToken': True}
    res = requests.post(url, json.dumps(data))
    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise Exception(res.text)


def refresh_id_token(refresh_token: str) -> dict:
    """
    Refresh a ID token by using refresh token.
    Document is here https://firebase.google.com/docs/reference/rest/auth/#section-refresh-token .

    Args:
        refresh_token:
            A Firebase Auth refresh token

    Returns:
        Dictionary. keys = ['access_token', 'expires_in', 'token_type', 'refresh_token',
            'id_token, 'user_id', 'project_id']
    """
    api_key = config.firebase['apiKey']
    url = f'https://securetoken.googleapis.com/v1/token?key={api_key}'
    payload = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
    res = requests.post(url, json.dumps(payload))
    if res.status_code == 200:
        return json.loads(res.text)
    else:
        raise Exception(res.text)
