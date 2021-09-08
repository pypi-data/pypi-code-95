import logging
from unittest.mock import patch

from ddt import ddt
from django.test import tag

from openlxp_notifications.management.commands.conformance_alerts import \
    send_log_email
from openlxp_notifications.models import (ReceiverEmailConfiguration,
                                          SenderEmailConfiguration)

from .test_setup import TestSetUp

logger = logging.getLogger('dict_config_logger')


@tag('unit')
@ddt
class CommandTests(TestSetUp):

    # Test cases for conformance_alerts

    def test_send_log_email(self):
        """Test for function to send emails of log file to personas"""
        with patch('openlxp_notifications.management.commands.'
                   'conformance_alerts.ReceiverEmailConfiguration') \
                as receive_email_cfg, \
                patch(
                    'openlxp_notifications.management.commands.'
                    'conformance_alerts.SenderEmailConfiguration') \
                as sender_email_cfg, \
                patch(
                    'openlxp_notifications.management.commands.'
                    'conformance_alerts.send_notifications',
                    return_value=None
                ) as mock_send_notification:
            receive_email = ReceiverEmailConfiguration(
                email_address=self.receive_email_list)
            receive_email_cfg.first.return_value = receive_email

            send_email = SenderEmailConfiguration(
                sender_email_address=self.sender_email)
            sender_email_cfg.first.return_value = send_email
            send_log_email()
            self.assertEqual(mock_send_notification.call_count, 1)
