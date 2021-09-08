import logging
from unittest.mock import patch

from ddt import ddt
from django.test import tag

from openlxp_notifications.management.utils.notification import (
    check_if_email_verified, send_notifications)

from .test_setup import TestSetUp

logger = logging.getLogger('dict_config_logger')


@tag('unit')
@ddt
class UtilsTests(TestSetUp):
    """Unit Test cases for utils """

    # Test cases for NOTIFICATION
    def test_send_notifications(self):
        """Test for function to send emails of log file to personas"""
        with patch('openlxp_notifications.management.utils.notification'
                   '.EmailMessage') as mock_send, \
                patch('openlxp_notifications.management.utils.notification'
                      '.boto3.client'):
            send_notifications(self.receive_email_list, self.sender_email)
            self.assertEqual(mock_send.call_count, 2)

    def test_check_if_email_verified(self):
        """Test to check if email id from user is verified """
        with patch('openlxp_notifications.management.utils.notification'
                   '.list_email_verified') as mock_list:
            mock_list.return_value = self.receive_email_list
            email_value = 'receiver1@openlxp.com'
            return_val = check_if_email_verified(email_value)
            self.assertFalse(return_val)

    def test_check_if_email_not_verified(self):
        """Test to check if email id from user is verified """
        with patch('openlxp_notifications.management.utils.notification'
                   '.list_email_verified') as mock_list:
            mock_list.return_value = self.receive_email_list
            email_value = 'receiver2@openlxp.com'
            return_val = check_if_email_verified(email_value)
            self.assertTrue(return_val)
