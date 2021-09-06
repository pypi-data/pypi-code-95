#!/usr/bin/env python3

import pytest
from unittest import mock
from it_automation.health_checks import check_cpu, check_disk_space, \
    check_memory, check_localhost_name_resolution, check_systems, email_health_error


@pytest.mark.parametrize("_input, expected", [(20, True), (80, False)])
@mock.patch("it_automation.health_checks.psutil.cpu_percent")
def test_check_cpu(mock_psutil_cpu_percent, _input, expected):
    mock_psutil_cpu_percent.return_value = _input
    assert check_cpu(50) == expected
    mock_psutil_cpu_percent.assert_called()


@pytest.mark.parametrize(
    "_input, expected",
    [((1000,900,100),False),
     ((1000,100,900), True)]
)
@mock.patch("it_automation.health_checks.shutil.disk_usage")
def test_check_disk_space(mock_shutil_disk_usage, _input, expected):
    mock_shutil_disk_usage.return_value = _input
    assert check_disk_space(25) == expected
    mock_shutil_disk_usage.assert_called()


@pytest.mark.parametrize("_input, expected", [(1000, True), (200, False)])
@mock.patch("it_automation.health_checks.psutil.virtual_memory")
def test_check_memory(mock_psutil_virtual_memory, _input, expected):
    mock_psutil_virtual_memory.return_value = mock.Mock(**{"available": _input})
    assert check_memory(500) == expected
    mock_psutil_virtual_memory.assert_called()


@pytest.mark.parametrize(
    "_input, expected",
    [('127.0.0.1', True),
     ('123.0.0.1', False)]
)
@mock.patch("it_automation.health_checks.socket.gethostbyname")
def test_check_localhost_name_resolution(
        mock_socket_gethostbyname,
        _input,
        expected
):
    mock_socket_gethostbyname.return_value = _input
    assert check_localhost_name_resolution() == expected
    mock_socket_gethostbyname.assert_called()


@mock.patch("it_automation.health_checks.emails")
def test_email_health_error(mock_emails):
    test_subject = "Test Subject"
    test_message = "Test Message"
    mock_emails_generate_email_arguments = (
        'automation@example.com',
        '@example.com',
        test_subject,
        'Please check your system and resolve the issue as soon as possible.'
    )

    mock_emails.return_value = mock.Mock(
        **{"generate_email.return_value": test_message,
           "send_email.return_value": "Sent Email"}
    )

    sender = "automation@example.com"
    receiver = "@example.com"
    email_body = "Please check your system and resolve the issue as soon as possible."

    email_health_error(sender, receiver, test_subject, email_body)
    mock_emails.generate_email.assert_called()
    mock_emails.send_email.assert_called()
    mock_emails.generate_email.assert_called_with(
        *mock_emails_generate_email_arguments)


@pytest.mark.parametrize(
    "_input, expected",
    [([True, True, True, True], 0), ([False, False, False, False], 4)]
)
@mock.patch("it_automation.health_checks.check_memory")
@mock.patch("it_automation.health_checks.email_health_error")
@mock.patch("it_automation.health_checks.check_cpu")
@mock.patch("it_automation.health_checks.check_disk_space")
@mock.patch("it_automation.health_checks.check_localhost_name_resolution")
def test_check_systems(
        mock_check_localhost_name_resolution,
        mock_check_disk_space,
        mock_check_cpu,
        mock_email_health_error,
        mock_check_memory,
        _input, expected
):
    cpu_percent_usage_threshold = 80
    available_disk_space_percent_threshold = 20
    memory_threshold = 500 * 1024 * 1024  # 500MB
    sender = "automation@example.com"
    receiver = "@example.com"
    email_body = "Please check your system and resolve the issue as soon as possible."

    mock_check_localhost_name_resolution.return_value = _input[0]
    mock_check_disk_space.return_value = _input[1]
    mock_check_cpu.return_value = _input[2]
    mock_check_memory.return_value = _input[3]

    mock_email_health_error_call_list = [
        mock.call(sender, receiver, 'Error - CPU usage is over ' + str(
            cpu_percent_usage_threshold) + 'percent', email_body),
        mock.call(sender, receiver, 'Error - Available disk space is less than '
                  + str(available_disk_space_percent_threshold), email_body),
        mock.call(sender, receiver, 'Error - localhost cannot be resolved to 127.0.0.1',
                  email_body),
        mock.call(sender, receiver, 'Error - Available memory is less than ' +
                  str(memory_threshold), email_body)
    ]

    check_systems(cpu_percent_usage_threshold,
                  available_disk_space_percent_threshold,
                  memory_threshold,
                  sender,
                  receiver,
                  email_body)

    assert mock_email_health_error.call_count == expected
    if mock_email_health_error.call_count == 4:
        mock_email_health_error.assert_has_calls(
            calls=mock_email_health_error_call_list
        )