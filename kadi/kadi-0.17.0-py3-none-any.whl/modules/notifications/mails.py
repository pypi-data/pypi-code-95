# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from flask import render_template

from .tasks import start_send_mail_task


def send_email_confirmation_mail(email, displayname, token):
    """Send an email confirmation mail in a background task.

    Uses :func:`kadi.modules.notifications.tasks.start_send_mail_task` to send the mail.

    :param email: The recipient address.
    :param displayname: The display name of the user.
    :param token: A JWT returned by :meth:`.LocalIdentity.get_email_confirmation_token`.
    :return: ``True`` if the task was started successfully, ``False`` otherwise.
    """
    text_message = render_template(
        "notifications/mails/email_confirmation.txt",
        displayname=displayname,
        token=token,
    )

    html_message = render_template(
        "notifications/mails/email_confirmation.html",
        displayname=displayname,
        token=token,
    )

    return start_send_mail_task(
        subject="[Kadi4Mat] Email confirmation",
        message=text_message,
        html_message=html_message,
        to_addresses=[email],
    )


def send_password_reset_mail(email, displayname, token):
    """Send a password reset mail in a background task.

    Uses :func:`kadi.modules.notifications.tasks.start_send_mail_task` to send the mail.

    :param email: The recipient address.
    :param displayname: The display name of the user.
    :param token: A JWT returned by :meth:`.LocalIdentity.get_password_reset_token`.
    :return: ``True`` if the task was started successfully, ``False`` otherwise.
    """
    text_message = render_template(
        "notifications/mails/password_reset.txt", displayname=displayname, token=token
    )

    html_message = render_template(
        "notifications/mails/password_reset.html", displayname=displayname, token=token
    )

    return start_send_mail_task(
        subject="[Kadi4Mat] Password reset request",
        message=text_message,
        html_message=html_message,
        to_addresses=[email],
    )
