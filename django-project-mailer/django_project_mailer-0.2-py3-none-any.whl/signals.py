# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .tasks import *
# from .models import *
# from django.apps import apps


# @receiver(post_save)
# def send_mail_tasks(sender, instance=None, created=False, **kwargs):
#     app_models = append()
#     if sender.__name__ in app_models:
#         if created:
#             mail = EmailReminder.objects.filter(actions='Created', modules=sender.__name__)
#             if mail.status:
#                 send_mail_task(instance.user, instance.email, mail.subject, mail.body, mail.signature)
#                 print("success")
#             else:
#                 print("status error")
#         else:
#             print("created error")


# post_save.connect(send_mail_tasks)


# def append():
#     list_data = List.objects.all()
#     list_pass = []
#     counts = list_data.count()
#     for i in range(counts):
#         list_pass.append(list_data[i].list)
#     return list_pass


from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import *
from .models import *
from django.apps import apps


@receiver(post_save)
def send_mail_tasks(sender, instance=None, created=False, **kwargs):
    app_models = append()
    if sender.__name__ in app_models:
        if created:
            mail = EmailReminder.objects.get(actions__signal_action='Created', modules__modules=sender.__name__)
            if mail.status:
                send_mail_task.apply_async(args=(instance.user, instance.email, mail.subject, mail.body, mail.signature),
                                           eta=mail.date_time)


post_save.connect(send_mail_tasks)


def append():
    list_data = List.objects.all()
    list_pass = []
    counts = list_data.count()
    for i in range(counts):
        list_pass.append(list_data[i].list)
    return list_pass
