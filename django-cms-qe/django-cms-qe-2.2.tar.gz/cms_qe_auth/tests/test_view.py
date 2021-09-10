import re

from django.contrib.auth import get_user_model
from django.test import override_settings
from pytest_data import use_data


@use_data(user_data={'username': 'testuser', 'password': 'testpass'})
def test_login(client, user):
    res = client.post('/en/auth/login/', {'username': 'testuser', 'password': 'testpass'})
    assert res.status_code == 302


def test_register(mailoutbox, client):
    assert len(mailoutbox) == 0
    assert not get_user_model().objects.filter(username='testuser')

    user = _register_user(client)

    assert user.email == 'testuser@example.com'
    assert len(mailoutbox) == 1
    activation_mail = mailoutbox[0]
    assert 'activate' in activation_mail.body
    assert 'http' in activation_mail.body


@override_settings(AUTHENTICATION_BACKENDS=[
    'django.contrib.auth.backends.ModelBackend',
    'cms_qe_auth.tests.utils.TestAuthBackend',
])
def test_activation_multiple_authentication_backends(client, mailoutbox):
    _test_activation(client, mailoutbox)


def test_activation(client, mailoutbox):
    _test_activation(client, mailoutbox)


def _test_activation(client, mailoutbox):
    user = _register_user(client)
    assert not user.is_active

    # Get activation link from email
    activation_mail = mailoutbox[0]
    activate_url_pattern = '(?P<url>https?://[^\s]+/activate/[^\s]+)'
    url = re.search(activate_url_pattern, activation_mail.body).group('url')

    response = client.get(url)
    user.refresh_from_db()

    assert user.is_active
    # Test automatic login
    assert response.context['user'].is_authenticated


def _register_user(client):
    res = client.post('/en/auth/register/', {
        'username': 'testuser',
        'password1': '179ad45c6ce2cb97cf1029e212046e81',
        'password2': '179ad45c6ce2cb97cf1029e212046e81',
        'email': 'testuser@example.com',
    })
    assert res.status_code == 302
    return get_user_model().objects.get(username='testuser')
