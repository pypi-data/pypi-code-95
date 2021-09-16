import pytest
from emails.views import EmailSettingAPIView
import json
from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient
from emails.models import EmailModel
from .factories import EmailFactory
from .validation import validate


class TestEmailSettingAPIView(TestCase):
    def setUp(self):
        """setUp necessary data before test begins """
        self.client = APIClient()
        self.email_data = {
            "creator_name": EmailFactory.creator_name,
            "email_host_user": EmailFactory.email_host_user,
            "email_host_password": EmailFactory.email_host_password,
            "email_host": EmailFactory.email_host,
            "email_use_tls": EmailFactory.email_use_tls,
            "email_use_ssl": EmailFactory.email_use_ssl,
            "email_port": EmailFactory.email_port
        }
        self.response = self.client.post(
            reverse("register-list"),
            self.email_data, format="json")

    def test_api_can_post(self):
        """ Test the api can post a given email data"""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED, "creation failed")

    def test_api_can_get(self):
        """ Test the api can get a given email data"""
        email_list = EmailModel.objects.get()
        response = self.client.get(
            reverse('email-register', kwargs={'pk': email_list.id}), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, email_list)

    def test_api_can_update(self):
        """ Test the api can update a given email data"""
        change_email_data = {
            "creator_name": EmailFactory.creator_name,
            "email_host_user": EmailFactory.email_host_user,
            "email_host_password": EmailFactory.email_host_password,
            "email_host": EmailFactory.email_host,
            "email_use_tls": EmailFactory.email_use_tls,
            "email_use_ssl": EmailFactory.email_use_ssl,
            "email_port": EmailFactory.email_port
        }
        email_list = EmailModel.objects.get()
        response = self.client.put(
            reverse('email-register', kwargs={'pk': email_list.id}),
            change_email_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['creator_name'], change_email_data['creator_name'])

    def test_api_can_delete(self):
        """ Test the api can delete a given email data"""
        email_list = EmailModel.objects.get()
        response = self.client.delete(
            reverse('email-register', kwargs={'pk': email_list.id}),
            format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(response.data, None)

    def test_email_saves_in_email_format(self):
        self.assertTrue(validate.validate_email(self.email_data['email_host_user']),
                        "Enter email address in valid format")

    def test_check_email_host_valid(self):
        self.assertTrue(validate.validate_email_host_address(self.email_data['email_host']),
                        f'Enter valid email host address.{self.email_data["email_host"]}')

    def test_validate_ssl_tls(self):
        self.assertTrue(validate.validate_ssl_tls(self.email_data['email_use_ssl'], self.email_data['email_use_tls']),
                        "check ssl and tls values.both can't be true or false ")

    def test_validate_email_port(self):
        self.assertTrue(validate.validate_email_port(self.email_data['email_port']), "invalid port")

    def test_creator_name(self):
        self.assertTrue(validate.validate_creator_name(self.email_data['creator_name']),
                        "enter a valid full name")
