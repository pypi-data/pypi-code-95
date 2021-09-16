from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your models here.


class EmailModel(models.Model):

    """ created for dynamic access of Mailer settings using from model"""

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

    """ for different types of notifications connection """

    notification_type = models.CharField(max_length=30)

    def __str__(self):
        return self.notification_type


class Actions(models.Model):

    """ for different types action connection"""

    signal_action = models.CharField(max_length=25)

    def __str__(self):
        return self.signal_action


class List(models.Model):

    """ for store the selected Table from Email Reminder Table"""

    list = models.CharField(max_length=20)


class Modules(models.Model):

    """ listing all the created model table for Email Reminder Table and giving user friendly name for display in front end side"""

    modules = models.CharField(max_length=20)
    user_friendly_name = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user_friendly_name


class Policies(models.Model):

    """ a policy purchase table """

    user = models.CharField(max_length=20)
    email = models.EmailField()
    policy_name = models.CharField(max_length=30)
    purchase_date = models.DateField()
    end_date = models.DateField()
    amount = models.IntegerField()

    def __str__(self):
        return self.user


class UserEmails(models.Model):

    """ user creation table """

    user = models.CharField(max_length=20)
    email = models.EmailField()
    subject = models.CharField(max_length=20, null=True)
    body = models.TextField(max_length=500, null=True)
    signature = models.TextField(max_length=100, null=True)


class EmailReminder(models.Model):

    """ Email Reminder Table for setting the periodic tasks """

    ONCE = "O"
    MINUTES = "I"
    HOURLY = "H"
    DAILY = "D"
    WEEKLY = "W"
    MONTHLY = "M"
    QUARTERLY = "Q"
    YEARLY = "Y"
    CRON = "C"
    TYPE = (
        (ONCE, _("Once")),
        (MINUTES, _("Minutes")),
        (HOURLY, _("Hourly")),
        (DAILY, _("Daily")),
        (WEEKLY, _("Weekly")),
        (MONTHLY, _("Monthly")),
        (QUARTERLY, _("Quarterly")),
        (YEARLY, _("Yearly")),
        (CRON, _("Cron")),
    )

    occurrence_type = ((True, 'single'), (False, 'recurring'))
    schedule_type = ((True, 'before'), (False, 'after'))
    email_notification_type = models.ForeignKey(Notifications, on_delete=models.CASCADE)
    subject = models.CharField(max_length=20)
    body = models.TextField(max_length=500)
    signature = models.TextField(max_length=100)
    occurrence = models.BooleanField(choices=occurrence_type, help_text="True for single")
    schedule = models.BooleanField(choices=schedule_type)
    status = models.BooleanField(default=True)
    minutes = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text=_("Number of minutes for the Minutes type")
    )
    schedule_period = models.CharField(
        max_length=1, choices=TYPE, default=TYPE[0][0], verbose_name=_("Schedule Type")
    )
    repeats = models.IntegerField(
        default=-1, verbose_name=_("Repeats"), help_text=_("n = n times, -1 = forever")
    )
    next_run = models.DateTimeField(
        verbose_name=_("Next Run"), default=timezone.now, null=True
    )
    modules = models.ForeignKey(Modules, on_delete=models.PROTECT)
    actions = models.ForeignKey(Actions, on_delete=models.PROTECT)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.email_notification_type)