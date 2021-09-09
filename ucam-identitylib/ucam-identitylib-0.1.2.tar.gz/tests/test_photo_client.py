from unittest import TestCase
from requests import Session, HTTPError
from requests_mock import Mocker
from base64 import b64encode

from identitylib import photo_client


class PhotoClientTestCase(TestCase):

    @Mocker()
    def setUp(self, request_mock: Mocker):
        """
        Setup the photo client here in order to intercept the initial auth request.

        """
        auth_request = request_mock.post(
            'https://api.apps.cam.ac.uk/oauth/client_credential/accesstoken',
            json={
                'token_type': 'Bearer',
                'access_token': 'fake-token',
            }
        )

        self.client = photo_client.PhotoClient('mock-client-id', 'mock-client-key')
        self.assertIsInstance(self.client.session, Session)

        self.assertEqual(len(auth_request.request_history), 1)
        self.assertEqual(
            auth_request.request_history[0].headers['Authorization'],
            f'Basic {b64encode(b"mock-client-id:mock-client-key").decode("utf-8")}'
        )

    @Mocker()
    def test_can_fetch_transient_photo_url(self, request_mock: Mocker):
        request_mock.get(
            f'{self.client.base_url}/photos/test-photo-uuid-123/content',
            status_code=302,
            headers={
                'Location': 'https://storage.google.com/test-photo-uuid-123?expiresIn=10'
            }
        )

        photo_url = self.client.get_transient_image_url('test-photo-uuid-123')
        self.assertEqual(photo_url, 'https://storage.google.com/test-photo-uuid-123?expiresIn=10')

    @Mocker()
    def test_will_throw_if_no_photo_for_transient_url_query(self, request_mock: Mocker):
        request_mock.get(
            f'{self.client.base_url}/photos/no-photo-available/content', status_code=404,
        )

        with self.assertRaises(photo_client.NoSuchPhotoException):
            self.client.get_transient_image_url('no-photo-available')

    @Mocker()
    def test_will_throw_if_unexpected_response_for_transient_url(self, request_mock: Mocker):
        request_mock.get(
            f'{self.client.base_url}/photos/test-photo-uuid/content', status_code=200,
            json={'success': True}
        )

        with self.assertRaisesRegex(
            RuntimeError, 'Photo API did not return a transient image url within redirect'
        ):
            self.client.get_transient_image_url('test-photo-uuid')

    @Mocker()
    def test_will_throw_if_photo_api_fails_for_transient_url_query(self, request_mock: Mocker):
        request_mock.get(
            f'{self.client.base_url}/photos/something-will-break/content', status_code=500,
            json={'success': True}
        )

        with self.assertRaises(HTTPError):
            self.client.get_transient_image_url('something-will-break')
