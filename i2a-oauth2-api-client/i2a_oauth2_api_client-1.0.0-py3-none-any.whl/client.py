import requests
import os
from urllib.parse import urljoin

from i2a_oauth2_api_client.exceptions import I2AOauth2ClientException, I2AOauth2ClientUnauthorizedException,\
    I2AOauth2ClientValidationError, I2AOauth2ClientNotFoundError


class I2AOauth2Client:

    I2A_OAUTH_API_SERVER_URL = 'https://oauth2-qa.i2asolutions.com'
    I2A_OAUTH_API_ROOT_PATH = '/api/v1'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def common_headers(self):
        return {
            'Client-Id': self.client_id
        }

    def common_headers_with_secret(self):
        headers = self.common_headers()
        headers['Client-Secret'] = self.client_secret
        return headers

    def get_full_url(self, resource_path):
        return urljoin(self.I2A_OAUTH_API_SERVER_URL, os.path.join(self.I2A_OAUTH_API_ROOT_PATH, resource_path))

    def ping(self):
        url = self.get_full_url('ping/')
        response = requests.get(url, headers=self.common_headers())
        if response.status_code != 200:
            raise I2AOauth2ClientException(
                f'Ping attempt at {url} has failed. Make sure I2A Oauth2 URL is correct and that the '
                f'service is running'
            )

    def build_full_username(self, email):
        return f"{email}@{self.client_id}"

    def register_user(self, email, password1, password2, first_name=None, last_name=None):
        full_username = self.build_full_username(email)
        return self.register_user_with_full_username(full_username, password1, password2, first_name, last_name)

    def register_user_with_full_username(self, username, password1, password2, first_name=None, last_name=None):
        data = {
            "username": username,
            "password1": password1,
            "password2": password2,
            "client_id": self.client_id
        }
        if first_name is not None:
            data['first_name'] = first_name
        if last_name is not None:
            data['last_name'] = last_name

        url = self.get_full_url('register/')
        response = requests.post(url, json=data, headers=self.common_headers())
        if response.status_code == 201:
            return response.json()
        elif response.status_code == 400:
            raise I2AOauth2ClientValidationError(data=response.json())
        else:
            raise I2AOauth2ClientException(
                f'Create user failed. I2A Oauth API returned HTTP {response.status_code}.'
                f' Response text: {response.text}'
            )

    def get_token_with_full_username(self, username, password):
        url = self.get_full_url('auth/token/')
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "password",
            "username": username,
            "password": password
        }
        response = requests.post(url, data, headers=self.common_headers())
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise I2AOauth2ClientValidationError(data=response.json())
        elif response.status_code == 401:
            raise I2AOauth2ClientUnauthorizedException(data=response.json())
        else:
            raise I2AOauth2ClientException(
                f'Get token operation failed.'
                f' Authentication service returned HTTP {response.status_code}. Response text: {response.text}'
            )

    def get_token(self, email, password):
        full_username = self.build_full_username(email)
        return self.get_token_with_full_username(full_username, password)

    def check_token(self, token):
        url = self.get_full_url('me/')
        headers = self.common_headers()
        headers.update({
            "Authorization": f"Bearer {token}"
        })
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise I2AOauth2ClientUnauthorizedException(data=response.json())
        else:
            raise I2AOauth2ClientException(
                f'Check token operation failed.'
                f' Authentication service returned HTTP {response.status_code}. Response text: {response.text}'
            )

    def convert_token(self, backend, access_token):
        url = self.get_full_url('auth/convert-token/')
        headers = self.common_headers()
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "convert_token",
            "backend": backend,
            "token": access_token
        }
        response = requests.post(url, data, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise I2AOauth2ClientValidationError(data=response.json())
        elif response.status_code == 401:
            raise I2AOauth2ClientUnauthorizedException(data=response.json())
        else:
            raise I2AOauth2ClientException(
                f'Convert token operation failed.'
                f' Authentication service returned HTTP {response.status_code}. Response text: {response.text}'
            )

    def password_reset_request(self, email):
        url = self.get_full_url('server-to-server/password-reset-request/')
        headers = self.common_headers_with_secret()
        json = {
            "username": self.build_full_username(email)
        }
        response = requests.post(url, json=json, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            data = response.json()
            if data.get('error_information'):
                raise I2AOauth2ClientValidationError(data={'detail': data.get('error_information')})
            raise I2AOauth2ClientValidationError(data=data)
        elif response.status_code == 401:
            raise I2AOauth2ClientUnauthorizedException(data=response.json())
        else:
            raise I2AOauth2ClientException(
                f'Password reset request operation failed.'
                f' Authentication service returned HTTP {response.status_code}. Response text: {response.text}'
            )

    def password_reset(self, code, new_password1, new_password2):
        url = self.get_full_url('server-to-server/password-reset/')
        headers = self.common_headers_with_secret()
        json = {
            "code": str(code),
            "new_password1": new_password1,
            "new_password2": new_password2
        }
        response = requests.post(url, json=json, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise I2AOauth2ClientValidationError(data=response.json())
        elif response.status_code == 401:
            raise I2AOauth2ClientUnauthorizedException(data=response.json())
        else:
            raise I2AOauth2ClientException(
                f'Password reset operation failed.'
                f' Authentication service returned HTTP {response.status_code}. Response text: {response.text}'
            )

    def password_reset_code_check(self, code):
        url = self.get_full_url('server-to-server/password-reset-code-check/')
        headers = self.common_headers_with_secret()
        json = {
            "code": str(code),
        }
        response = requests.post(url, json=json, headers=headers)
        if response.status_code == 204:
            return None
        elif response.status_code == 400:
            raise I2AOauth2ClientValidationError(data=response.json())
        elif response.status_code == 401:
            raise I2AOauth2ClientUnauthorizedException(data=response.json())
        else:
            raise I2AOauth2ClientException(
                f'Password reset code check operation failed.'
                f' Authentication service returned HTTP {response.status_code}. Response text: {response.text}'
            )

    def password_change(self, token, old_password, new_password1, new_password2):
        url = self.get_full_url('password-change/')
        headers = self.common_headers()
        headers.update({
            "Authorization": f"Bearer {token}"
        })
        json = {
            "old_password": old_password,
            "new_password1": new_password1,
            "new_password2": new_password2
        }
        response = requests.post(url, json=json, headers=headers)
        if response.status_code == 200:
            return None
        elif response.status_code == 400:
            raise I2AOauth2ClientValidationError(data=response.json())
        elif response.status_code == 401:
            raise I2AOauth2ClientUnauthorizedException(data=response.json())
        else:
            raise I2AOauth2ClientException(
                f'Password change operation failed.'
                f' Authentication service returned HTTP {response.status_code}. Response text: {response.text}'
            )

    def delete_account(self, token):
        url = self.get_full_url('password-change/')
        headers = self.common_headers()
        headers.update({
            "Authorization": f"Bearer {token}"
        })
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            return None
        elif response.status_code == 400:
            raise I2AOauth2ClientValidationError(data=response.json())
        elif response.status_code == 401:
            raise I2AOauth2ClientUnauthorizedException(data=response.json())
        elif response.status_code == 404:
            raise I2AOauth2ClientNotFoundError(data=response.json())
        else:
            raise I2AOauth2ClientException(
                f'Delete account operation failed.'
                f' Authentication service returned HTTP {response.status_code}. Response text: {response.text}'
            )
