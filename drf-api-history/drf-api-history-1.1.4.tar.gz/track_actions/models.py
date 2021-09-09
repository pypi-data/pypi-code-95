from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models

from track_actions import constants


class History(models.Model):
    """History model to store user actions"""

    table_name = models.CharField(max_length=255, blank=False, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    instance_id = models.CharField(
        max_length=255, null=False, blank=False, editable=False
    )
    action = models.TextField(null=True, blank=True, )

    field_name = models.TextField(null=True, blank=True, )

    class Meta:
        ordering = ('-id',)
        verbose_name_plural = "History model"
