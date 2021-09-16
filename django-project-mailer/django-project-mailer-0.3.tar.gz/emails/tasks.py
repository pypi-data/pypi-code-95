from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from datetime import timedelta, date
import datetime
from .backends import backends, email_from
from django.template.loader import render_to_string, get_template
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from .models import *


# def shared_task(schedule)


# class FilteringPolicyUsers:
#     def __init__(self, model):
#         self.model = model
#
#     def data_filter(self, n_days, types):
#         dates = datetime.date.today() + timedelta(n_days)
#         queryset = self.model.objects.filter(end_date=dates)
#         count = queryset.count()
#         email_reminder = EmailReminderSelection(EmailReminder)
#         alert = email_reminder.alert_notification(types)
#         if alert:
#             if alert.status:
#                 for i in range(count):
#                     if alert.occurrence:
#                         send_mail_task(alert.subject, alert.body, alert.signature, queryset[i].user, queryset[i].email)
#                     else:
#                         pass
#
#             else:
#                 return None
#         else:
#             pass
#
#
# class EmailReminderSelection:
#     def __init__(self, model):
#         self.model = model
#
#     def alert_notification(self, types):
#         mail = self.model.objects.get(email_notification_type=types)
#         return mail
#
#
# @shared_task
# def filtering():
#     users = FilteringPolicyUsers(Policies)
#     users.data_filter(5, 6)
#     users.data_filter(2, 7)
#
#
@shared_task
def send_mail_task(user, emails, subject, body, signature):
    template = get_template('email.html')
    content = template.render({'user': user, 'body': body, 'signature': signature})
    email = EmailMessage(subject=subject, body=content, from_email=email_from, to=[emails],
                         connection=backends)
    email.content_subtype = "html"
    email.send()
    print("send_mail_task")
    print(user, emails, subject, body, signature,"tasks")


