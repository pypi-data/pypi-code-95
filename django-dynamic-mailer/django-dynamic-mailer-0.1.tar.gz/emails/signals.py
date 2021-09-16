from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django_q.tasks import async_task


@receiver(post_save)
def send_mail_tasks(sender, instance=None, created=False, **kwargs):
    app_models = append()
    if sender.__name__ in app_models:
        if created:
            mail = EmailReminder.objects.get(actions__signal_action='Created', modules__modules=sender.__name__)
            if mail.status:
                async_task('emails.task.send_mail_task',)
                print('ok')


post_save.connect(send_mail_tasks)


def append():
    list_data = List.objects.all()
    list_pass = []
    counts = list_data.count()
    for i in range(counts):
        list_pass.append(list_data[i].list)
    return list_pass
