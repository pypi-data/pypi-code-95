from .backends import backends, email_from

from django.template.loader import render_to_string, get_template
from django.core.mail import send_mail, EmailMessage


def send_mail_task():
    # template = get_template('email.html')
    # content = template.render({'user': instance.user, 'body': mail.body, 'signature': mail.signature})
    # email = EmailMessage(subject=mail.subject, body=content, from_email=email_from, to=[instance.email],
    #                      connection=backends)
    # email.content_subtype = "html"
    # email.send()
    print("you are done")
