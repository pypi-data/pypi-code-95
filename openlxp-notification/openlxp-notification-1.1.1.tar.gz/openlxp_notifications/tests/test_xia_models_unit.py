from django.test import SimpleTestCase, tag

from openlxp_notifications.models import (ReceiverEmailConfiguration,
                                          SenderEmailConfiguration)


@tag('unit')
class ModelTests(SimpleTestCase):

    def test_create_sender_email_config(self):
        """Test that creating a new Sender Email Configuration entry is
        successful with defaults """
        sender_email_address = 'example@test.com'

        sender_email_Config = SenderEmailConfiguration(
            sender_email_address=sender_email_address)

        self.assertEqual(sender_email_Config.sender_email_address,
                         sender_email_address)

    def test_create_receiver_email_config(self):
        """Test that creating a new Receiver Email Configuration entry is
        successful with defaults """
        email_address = 'example@test.com'

        receiver_email_Config = ReceiverEmailConfiguration(
            email_address=email_address)

        self.assertEqual(receiver_email_Config.email_address,
                         email_address)
