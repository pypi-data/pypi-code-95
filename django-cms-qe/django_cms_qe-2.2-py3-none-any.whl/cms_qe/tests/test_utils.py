from unittest.mock import patch

import pytest
from django.test import override_settings
from mailqueue.models import MailerMessage
from pytest_data import use_data

from cms_qe.utils import get_base_url, get_email, get_functions, get_module, get_modules


@pytest.mark.parametrize('expect,module_name', [
    (True, 'views'),
    (True, 'views.monitoring'),
    (False, 'no_module'),
    (False, 'monitoring.get_status'),
])
def test_get_module(expect, module_name):
    module = get_module('cms_qe', module_name)
    assert module if expect else module is None


def test_get_modules():
    modules = get_modules('monitoring')
    assert [module for app_name, module in modules if app_name == 'cms_qe']


def test_get_functions():
    functions = get_functions('monitoring', 'get_status')
    assert [function for app_name, function in functions if app_name == 'cms_qe']


def test_get_functions_existing_module_without_function():
    functions = get_functions('monitoring', 'no_function')
    assert not list(functions)


@override_settings(META_SITE_PROTOCOL='https', )
def test_get_absolute_url(post_request_empty):
    request = post_request_empty
    mock_url = 'test.com'
    with patch('cms_qe.utils.get_current_site', return_value=mock_url):
        base_url = get_base_url(request)
    assert base_url == 'https://{}'.format(mock_url)


def test_sending_email_synchronously(email, mailoutbox):
    assert len(mailoutbox) == 0
    email.save()
    assert len(mailoutbox) == 1
    sent_mail = mailoutbox[0]
    assert 'Test content' in sent_mail.body
    assert 'Test' in sent_mail.subject


@override_settings(MAILQUEUE_QUEUE_UP=True)
def test_sending_email_asynchronously(email, mailoutbox):
    assert MailerMessage.objects.all().count() == 0
    email.save()
    assert len(mailoutbox) == 0
    assert MailerMessage.objects.all().count() == 1
    assert 'Test content' in MailerMessage.objects.all().first().content


@use_data(email_data={'to': ['test1@examile.com', 'test2@examile.com']})
def test_sending_email_synchronously_more_addressee(email, mailoutbox):
    email.save()
    assert len(mailoutbox) == 1
    sent_mail = mailoutbox[0]
    assert len(sent_mail.to) == 2


@use_data(email_data={'to': ['test1@examile.com', 'test2@examile.com']})
@override_settings(MAILQUEUE_QUEUE_UP=True)
def test_sending_email_asynchronously_more_to_addressee(email, mailoutbox):
    email.save()
    assert MailerMessage.objects.all().count() == 1
    assert MailerMessage.objects.all().first().to_address == 'test1@examile.com, test2@examile.com'
