# from emails.models import EmailModel
# from emails.serializers import EmailSerializers
# from django.test import TestCase
# from faker import Faker,Factory
# from .factories import EmailFactory
# faker = Factory.create()
#
#
# class TestEmailSerializers(TestCase):
#     def setUp(self):
#         """setUp necessary data before test begins """
#
#         self.email_data = {
#             "creator_name": EmailFactory.creator_name,
#             "email_host_user": EmailFactory.email_host_user,
#             "email_host_password": EmailFactory.email_host_password,
#             "email_host": EmailFactory.email_host,
#             "email_use_tls": EmailFactory.email_use_tls,
#             "email_use_ssl": EmailFactory.email_use_ssl,
#             "email_port": EmailFactory.email_port
#         }
#         self.email = EmailModel.objects.create(**self.email_data)
#         self.serializer = EmailSerializers(instance=self.email)
#
#     def test_email_serializer(self):
#         serializer_data = self.serializer.data
#         self.assertEqual(serializer_data['email_host_user'], self.email_data['email_host_user'])
#         self.assertEqual(serializer_data['email_host'], self.email_data['email_host'])
#         self.assertEqual(serializer_data['email_use_tls'], self.email_data['email_use_tls'])
#         self.assertEqual(serializer_data['email_use_ssl'], self.email_data['email_use_ssl'])
#         self.assertEqual(serializer_data['email_port'], self.email_data['email_port'])
#
#
