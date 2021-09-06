#!/usr/bin/env python3
""" This module contains functions for checking if system resources are
    overloaded and then emailing a error message.

    Thresholds are passed into check functions and they return false if system
    resources are below the thresholds, indicating that the system has failed.
"""
import shutil
import psutil
from it_automation import emails
import socket


def check_cpu(cpu_percent_usage_threshold):
    """ Checks if CPU percent load is below given threshold.

    Args:
        cpu_percent_usage_threshold(int): The percent threshold you want the cpu
        to be above.

    Returns:
        (Bool): Returns true if cpu load is below the threshold.
    """
    cpu_percent_usage = psutil.cpu_percent(interval=1, percpu=False)
    return cpu_percent_usage < cpu_percent_usage_threshold


def check_disk_space(available_disk_space_percent_threshold):
    """ Checks if disk space is above given threshold.

    Args:
        available_disk_space_percent_threshold(int): The disk space threshold
        you want the root drive to be above.

    Returns:
        (Bool): Returns true if disk space is above the given threshold.
    """
    total_disk_space, used_disk_space, free_disk_space = shutil.disk_usage("/")
    available_disk_space_percent = (free_disk_space / total_disk_space) * 100
    return available_disk_space_percent > available_disk_space_percent_threshold


def check_memory(memory_threshold):
    """ Checks if system memory is above given threshold in bytes.

    Args:
        memory_threshold(int): The memory threshold in Bytes.

    Returns:
        (Bool): Returns true if memory is above given threshold.
    """
    memory = psutil.virtual_memory()
    memory_available = memory.available
    return memory_available > memory_threshold


def check_localhost_name_resolution():
    """ Checks if localhost ip resolves to 127.0.0.1

    Args:
        None:

    Returns:
        (Bool): Returns true if localhost ip is not 127.0.0.1
    """
    local_host_ip = socket.gethostbyname('localhost')
    return local_host_ip == '127.0.0.1'


def email_health_error(sender, receiver, subject, email_body):
    """ Emails a error message with the passed in subject.

        Should be used with check functions in this module to email a
        error message when computer resources are overloaded.

    Args:
        sender(string): The sender of the email.

        receiver(string): email recipient.

        subject(string): The subject of the email.

        email_body(string): The body of text in the email message.

    Returns:
        None
    """
    message = emails.generate_email(sender, receiver, subject, email_body)
    emails.send_email(message)


def check_systems(cpu_percent_usage_threshold,
                  available_disk_space_percent_threshold,
                  memory_threshold,
                  sender,
                  receiver,
                  email_body):
    """ Runs all check functions and emails a error message if any return false.

        Used in main function. Can set up a cron job with this script to monitor
        system health.

    Args:
        cpu_percent_usage_threshold(int): The percent threshold you want the cpu
        to be above.

        available_disk_space_percent_threshold(int): The disk space threshold
        you want the root drive to be above.

        memory_threshold(int): The memory threshold in Bytes.

        sender(string): The sender of the email.

        receiver(string): email recipient.

        email_body(string): The body of text in the email message.

    Returns:
        None
    """
    if not check_cpu(cpu_percent_usage_threshold):
        subject = 'Error - CPU usage is over ' + str(
            cpu_percent_usage_threshold) + 'percent'
        email_health_error(sender, receiver, subject, email_body)

    if not check_disk_space(available_disk_space_percent_threshold):
        subject = 'Error - Available disk space is less than ' + str(
            available_disk_space_percent_threshold
        )
        email_health_error(sender, receiver, subject, email_body)

    if not check_localhost_name_resolution():
        subject = 'Error - localhost cannot be resolved to 127.0.0.1'
        email_health_error(sender, receiver, subject, email_body)

    if not check_memory(memory_threshold):
        subject = 'Error - Available memory is less than ' + str(memory_threshold)
        email_health_error(sender, receiver, subject, email_body)