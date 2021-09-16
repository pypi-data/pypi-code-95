from django.db import models
from django.db import models, signals


# Create your models here.


class EmailModel(models.Model):
    creator_name = models.CharField(max_length=20)
    email_host = models.CharField(max_length=30)
    email_use_tls = models.BooleanField(help_text="True for Gmail")
    email_use_ssl = models.BooleanField(help_text="False for Gmail")
    email_port = models.IntegerField()
    email_host_user = models.EmailField()
    email_host_password = models.CharField(max_length=50)
    data_created = models.DateField(auto_now_add=True)
    last_modified = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        if EmailModel.objects.exists():
            pass
        else:
            self.pk = 1
        super(EmailModel, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.pk} {self.email_host_user}'


class Notifications(models.Model):
    notification_type = models.CharField(max_length=30)

    def __str__(self):
        return self.notification_type


class Actions(models.Model):
    signal_action = models.CharField(max_length=25)

    def __str__(self):
        return self.signal_action


class List(models.Model):
    list = models.CharField(max_length=20)


class Modules(models.Model):
    modules = models.CharField(max_length=20)

    def __str__(self):
        return self.modules


class Policies(models.Model):
    user = models.CharField(max_length=20)
    email = models.EmailField()
    policy_name = models.CharField(max_length=30)
    purchase_date = models.DateField()
    end_date = models.DateField()
    amount = models.IntegerField()

    def __str__(self):
        return self.user


class UserEmails(models.Model):
    user = models.CharField(max_length=20)
    email = models.EmailField()
    subject = models.CharField(max_length=20)
    body = models.TextField(max_length=500)
    signature = models.TextField(max_length=100)


class EmailReminder(models.Model):
    occurrence_type = ((True, 'single'), (False, 'recurring'))
    schedule_type = ((True, 'before'), (False, 'after'))
    email_notification_type = models.ForeignKey(Notifications, on_delete=models.CASCADE)
    subject = models.CharField(max_length=20)
    body = models.TextField(max_length=500)
    signature = models.TextField(max_length=100)
    occurrence = models.BooleanField(choices=occurrence_type, help_text="True for single")
    schedule = models.BooleanField(choices=schedule_type)
    status = models.BooleanField(default=True)
    schedule_days = models.IntegerField(blank=True, null=True)
    schedule_hours = models.IntegerField(blank=True, null=True)
    schedule_minutes = models.IntegerField(blank=True, null=True)
    interval_days = models.IntegerField(blank=True, null=True)
    interval_hours = models.IntegerField(blank=True, null=True)
    interval_minutes = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField(null=True)
    modules = models.ForeignKey(Modules, on_delete=models.PROTECT)
    actions = models.ForeignKey(Actions, on_delete=models.PROTECT)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.email_notification_type)


class PushReminder(models.Model):
    occurrence_type = ((True, 'single'), (False, 'recurring'))
    schedule_type = ((True, 'before'), (False, 'after'))
    title = models.CharField(max_length=20)
    message = models.TextField(max_length=100)
    image = models.ImageField(upload_to='reminder')
    url = models.URLField()
    occurrence = models.BooleanField(choices=occurrence_type, help_text="True for single")
    schedule = models.BooleanField(choices=schedule_type)
    status = models.BooleanField(default=True)
    interval_period = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
