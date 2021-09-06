#!/usr/bin/env python3
import email.message
import os.path
import mimetypes
import smtplib
""" This module contains functions for generating and sending emails."""


def generate_email(sender, recipient, subject, body, attachment_path=None):
    """ Generates a email message.

    Args:
        sender(string): The sender of the email message.
        recipient(string): The recipient of the email message.
        subject(string): The subject text in the email message.
        body(string): The body of text in the email message.
        attachment_path(string): Optional path of file being attached to email.

    Returns:
        email.message.EmailMessage object
    """
    # If email will not have an attachmentment
    if attachment_path is None:
        message = email.message.EmailMessage()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        return message
    else:
        message = email.message.EmailMessage()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        # Adding attachmentment to email
        attachment_filename = os.path.basename(attachment_path)
        mime_type = mimetypes.guess_type(attachment_path)[0]
        mime_type, mime_subtype = mime_type.split('/', 1)
        with open(attachment_path, 'rb') as ap:
            message.add_attachment(ap.read(),
            maintype = mime_type,
            subtype = mime_subtype,
            filename = attachment_filename)
            return message


def send_email(message):
    """ Emails the passed in email.message.EmailMessage object.

    Args:
        message(email.message.EmailMessage): email.message object to be sent

    Returns:
        None
    """
    mail_server = smtplib.SMTP('localhost')
    mail_server.send_message(message)
    mail_server.quit()
