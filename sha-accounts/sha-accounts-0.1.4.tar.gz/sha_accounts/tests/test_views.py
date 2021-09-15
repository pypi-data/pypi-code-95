from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase
from djrest_wrapper.exceptions.apis import errors
from ..models.user_models import User
from ..models import get_user_profile_model

class UserViewSetTestCase(APITestCase):
    def setUp(self):
        pass

    def test_create_user_view(self):
        url = reverse('user-list')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'test'
        }
        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('err'), False)
        self.assertEqual(response.json().get(
            'err_code'), errors.ERR_SUCCESSFUL)
        self.assertIsNotNone(response.json().get(
            'data').get('user').get('access_token'))

    def test_signin_user_view(self):
        self.test_create_user_view()
        url = reverse('user-signin')
        data = {
            'username': 'testuser',
            'password': 'test'
        }
        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('err'), False)
        self.assertEqual(response.json().get(
            'err_code'), errors.ERR_SUCCESSFUL)
        self.assertIsNotNone(response.json().get(
            'data').get('user').get('access_token'))
        return response.json().get('data').get('user')

    def test_retrieve_user_profile_view_succesful(self):
        user = self.test_signin_user_view()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'{settings.SHA_ACCOUNTS.get("JWT_AUTH_RAELM")} {user.get("access_token")}')
        url = reverse('user-detail', args={user.get('id')})
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('err'), False)
        self.assertEqual(response.json().get(
            'err_code'), errors.ERR_SUCCESSFUL)
        self.assertIsNotNone(response.json().get('data').get('user'))

    def test_retrieve_user_profile_view_failed(self):
        user = self.test_signin_user_view()
        url = reverse('user-detail', args={user.get('id')})
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json().get('err'), True)
        self.assertEqual(response.json().get(
            'err_code'), errors.ERR_PERMISSION_DENIED)

    def test_retrieve_user_profile_admin_view(self):
        superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='superuser')
        user = User.objects.create(
            username='testuser',
            email='testuser@example.com',
            password='testuser')
        url = reverse('user-signin')
        data = {
            'username': superuser.username,
            'password': 'superuser'
        }
        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('err'), False)
        self.assertEqual(response.json().get(
            'err_code'), errors.ERR_SUCCESSFUL)
        self.assertIsNotNone(response.json().get(
            'data').get('user').get('access_token'))
        self.client.credentials(
            HTTP_AUTHORIZATION=f'{settings.SHA_ACCOUNTS.get("JWT_AUTH_RAELM")} {response.json().get("data").get("user").get("access_token")}')
        url = reverse('user-detail', args={user.id})
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('err'), False)
        self.assertEqual(response.json().get(
            'err_code'), errors.ERR_SUCCESSFUL)
        self.assertIsNotNone(response.json().get('data').get('user'))

    def test_user_list_admin_view(self):
        superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='superuser')
        url = reverse('user-signin')
        data = {
            'username': superuser.username,
            'password': 'superuser'
        }
        response = self.client.post(path=url, data=data, format='json')

        for i in range(12):
            User.objects.create(
                username=f'test{i}',
                email=f'test{i}@example.com',
                password=f'test{i}')
        url = reverse('user-list')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'{settings.SHA_ACCOUNTS.get("JWT_AUTH_RAELM")} {response.json().get("data").get("user").get("access_token")}')
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('err'), False)
        self.assertEqual(response.json().get(
            'err_code'), errors.ERR_SUCCESSFUL)
        self.assertIsNotNone(response.json().get('data').get('page'))
        self.assertIsNotNone(response.json().get('data').get('users'))

    def test_user_update_profile_put_view(self):
        user = User.objects.create(
            username=f'test',
            email=f'test@example.com',
            password=f'test')
        access_token = self._login('test', 'test').get(
            'data').get('user').get('access_token')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'{settings.SHA_ACCOUNTS.get("JWT_AUTH_RAELM")} {access_token}')
        url = reverse('user-detail', args={user.id})
        data = {
            'profile': {
                'first_name': 'ali',
            },
        }
        response = self.client.put(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('err'), False)
        self.assertEqual(response.json().get(
            'err_code'), errors.ERR_SUCCESSFUL)
        self.assertEqual(response.json().get('data').get('user').get(
            'profile').get('first_name'), data.get('profile').get('first_name'))

    def test_user_update_profile_patch_view(self):
        user = User.objects.create(
            username=f'test',
            email=f'test@example.com',
            password=f'test')
        access_token = self._login('test', 'test').get(
            'data').get('user').get('access_token')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'{settings.SHA_ACCOUNTS.get("JWT_AUTH_RAELM")} {access_token}')
        url = reverse('user-detail', args={user.id})
        data = {
            'profile': {
                'first_name': 'ali',
            },
        }
        response = self.client.patch(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('err'), False)
        self.assertEqual(response.json().get(
            'err_code'), errors.ERR_SUCCESSFUL)
        self.assertEqual(response.json().get('data').get('user').get(
            'profile').get('first_name'), data.get('profile').get('first_name'))

    def test_delete_user_view(self):
        user = User.objects.create(
            username=f'test',
            email=f'test@example.com',
            password=f'test')
        access_token = self._login('test', 'test').get(
            'data').get('user').get('access_token')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'{settings.SHA_ACCOUNTS.get("JWT_AUTH_RAELM")} {access_token}')
        url = reverse('user-detail', args={user.id})
        response = self.client.delete(path=url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        try:
            deleting_user = User.objects.get(username=f'test')
            deleting_user_profile = get_user_profile_model().objects.get(user=user)
            self.assertIsNone(deleting_user)
            self.assertIsNone(deleting_user_profile)
        except User.DoesNotExist:
            self.assertTrue(True)

    def test_user_signout_view(self):
        user = User.objects.create(
            username=f'test',
            email=f'test@example.com',
            password=f'test')
        access_token = self._login('test', 'test').get(
            'data').get('user').get('access_token')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'{settings.SHA_ACCOUNTS.get("JWT_AUTH_RAELM")} {access_token}')
        url = reverse('user-signout')
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url = reverse('user-detail', args={user.id})
        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_view(self):
        user = User.objects.create(
            username=f'test',
            email=f'test@example.com',
            password=f'test')
        access_token = self._login('test', 'test').get(
            'data').get('user').get('access_token')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'{settings.SHA_ACCOUNTS.get("JWT_AUTH_RAELM")} {access_token}')
        url = reverse('user-change-password')
        data = {
            'old_password': 'test',
            'new_password': 'test1'
        }
        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('err'), False)
        self.assertEqual(response.json().get(
            'err_code'), errors.ERR_SUCCESSFUL)

    def _login(self, username, password):
        data = {
            'username': username,
            'password': password
        }
        url = reverse('user-signin')
        response = self.client.post(path=url, data=data, format='json')
        return response.json()
