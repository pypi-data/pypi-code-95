from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from cms_qe.views import handler500
from cms_qe_test.cms import create_page


def test_page_found(client):
    create_page('Test page', page_params={'slug': 'test'})
    html = client.get('/en/test/').content
    assert b'<h1>Generic error</h1>' not in html
    assert b'<title>Test page</title>' in html


def test_page_not_found(client):
    html = client.get('/en/non-existing-page/').content
    assert b'<h1>Generic error</h1>' in html
    assert b'error404' in html


def test_page_not_found_custom_by_cms(client):
    create_page('custom page not found', page_params={'slug': 'error404'})
    html = client.get('/en/non-existing-page/').content
    assert b'<h1>Generic error</h1>' not in html
    assert b'<title>custom page not found</title>' in html


class Handler500Test(TestCase):
    def test_template_rendered(self):
        request = RequestFactory().get("/500")
        request.current_page = None
        request.session = {}
        request.user = AnonymousUser()
        response = handler500(request)
        self.assertContains(response, '<h1>Internal error</h1>', status_code=500)
        self.assertContains(response, 'Something went very wrong. Please try again later.', status_code=500)

    @patch('cms_qe.views.errors.render', side_effect=Exception("Fail!"))
    def test_template_failure(self, render_mock):
        request = RequestFactory().get("/500")
        request.current_page = None
        request.session = {}
        request.user = AnonymousUser()
        response = handler500(request)
        self.assertContains(response, '<h1>Internal error</h1>', status_code=500)
        self.assertContains(response, 'Something went very wrong. Please try again later.', status_code=500)
