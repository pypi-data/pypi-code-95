from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase
from django.urls import reverse

from allianceauth.tests.auth_utils import AuthUtils
from esi.models import Token

from .. import views


class TestViews(TestCase):
        
    def setUp(self):
        self.factory = RequestFactory()
        self.user = AuthUtils.create_user('Bruce Wayne')        

    def test_groups_view_can_load(self):
        request = self.factory.get(reverse('groupmanagement:groups'))
        request.user = self.user
        response = views.groups_view(request)
        self.assertEqual(response.status_code, 200)        