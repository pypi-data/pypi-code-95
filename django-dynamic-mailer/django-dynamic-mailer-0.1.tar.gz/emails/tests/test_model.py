from django.test import TestCase
from emails.models import EmailModel, EmailReminder, Notifications
from faker import Faker, Factory
from .factories import EmailFactory, EmailRemainderFactory
from .validation import validate
import random

faker = Faker()


class TestEmailModel(TestCase):
    def setUp(self):
        """setUp necessary data before test begins """
        self.old_count = EmailModel.objects.all().count()
        """create a sample email instance"""

        self.email_data = {
            "creator_name": EmailFactory.creator_name,
            "email_host_user": EmailFactory.email_host_user,
            "email_host_password": EmailFactory.email_host_password,
            "email_host": EmailFactory.email_host,
            "email_use_tls": EmailFactory.email_use_tls,
            "email_use_ssl": EmailFactory.email_use_ssl,
            # "email_port": EmailFactory.email_port,
            "email_port": faker.pyint(1, 120000)
        }
        self.email = EmailModel.objects.create(**self.email_data)

    def test_object_created_or_not(self):
        """objects counts after creation"""
        self.new_count = EmailModel.objects.all().count()
        '''check the new objects count is greater than old count  '''
        self.assertEqual(self.new_count, self.old_count + 1, "object is not created")

    def test_email_object_values(self):
        email_data = EmailModel.objects.get(id=self.email.pk)

        """ check both objects values are equal """
        self.assertEqual(self.email.creator_name, email_data.creator_name)
        self.assertEqual(self.email.email_host_user, email_data.email_host_user)
        self.assertEqual(self.email.email_host_password, email_data.email_host_password)
        self.assertEqual(self.email.email_host, email_data.email_host)
        self.assertEqual(self.email.email_use_tls, email_data.email_use_tls)
        self.assertEqual(self.email.email_use_ssl, email_data.email_use_ssl)
        self.assertEqual(self.email.email_port, email_data.email_port)

    def test_string_representation(self):
        """ Method `__str__` should be equal to field `creator_name`"""
        entry = EmailModel(EmailFactory.creator_name)
        self.assertEqual(entry.__str__(), entry.creator_name)

    def test_email_saves_in_email_format(self):
        self.assertTrue(validate.validate_email(self.email.email_host_user), f"{self.email.email_host_user}"
                                                                             f"is not a valid email format")

    def test_check_email_host_valid(self):
        self.assertTrue(validate.validate_email_host_address(self.email.email_host), self.email.email_host)

    def test_validate_ssl_tls(self):
        self.assertTrue(validate.validate_ssl_tls(self.email.email_use_ssl, self.email.email_use_tls),
                        f"check ssl and tls values.both can't be true or false.values:{self.email.email_use_tls},"
                        f"{self.email.email_use_tls} ")

    def test_validate_email_port(self):
        self.assertTrue(validate.validate_email_port(self.email.email_port),
                        f"{self.email.email_port} is not a valid email port")

    def test_validate_creatogr_name(self):
        self.assertTrue(validate.validate_creator_name(self.email.creator_name),
                        "enter a valid full name")
        self.assertTrue(validate.validate_field_max_length(self.email.creator_name, 20),
                        "maximum length of creator name exceed")

    def test_validate_password(self):
        self.assertTrue(validate.validate_password(self.email.email_host_password),
                        f'{self.email.email_host_password} is not a strong password ')


class TestEmailRemainder(TestCase):
    def setUp(self):
        self.old_count = EmailReminder.objects.all().count()
        notification_type = Notifications.objects.create(
            notification_type=EmailRemainderFactory.email_notification_type)
        self.email_reminder_data = {
            "subject": EmailRemainderFactory.subject,
            "body": EmailRemainderFactory.body,
            "signature": EmailRemainderFactory.signature,
            "email_notification_type": notification_type,
            "occurrence": EmailRemainderFactory.occurrence,
            "schedule": EmailRemainderFactory.schedule,
            "interval_period": EmailRemainderFactory.interval_period,
            "status": EmailRemainderFactory.status,
            "is_deleted": EmailRemainderFactory.is_deleted
        }
        self.email_reminder_object = EmailReminder.objects.create(**self.email_reminder_data)

    def test_object_created_or_not(self):
        """objects counts after creation"""
        self.new_count = EmailReminder.objects.all().count()
        '''check the new objects count is greater than old count  '''
        self.assertEqual(self.new_count, self.old_count + 1, "object is not created")
