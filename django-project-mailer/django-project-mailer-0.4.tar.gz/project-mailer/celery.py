import os
from celery.schedules import crontab
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Email.settings')

app = Celery('emails')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.beat_schedule = {
    # Executes every Monday morning at 7:30 a.m.
    'add-every-monday-morning': {
        'task': 'emails.tasks.filtering',
        'schedule': crontab(minute=57, hour=11),
    },
    'add-every-30-seconds': {
        'task': 'emails.tasks.send_mail_task',
        'schedule': 30.0,
        'options': {
            # ensure we don't accumulate a huge backlog of these if the workers are down
            'expires': 300,
        },
    },
}


# app.conf.beat_schedule = {
#     'add-every-30-seconds': {
#         'task': 'emails.tasks.send_mail_rec',
#         'schedule': 10.0,
#     },
# }
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
