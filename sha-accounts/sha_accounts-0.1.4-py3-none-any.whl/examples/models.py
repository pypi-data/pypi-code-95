from django.db import models
from djrest_wrapper.interfaces import BaseModel


class ExampleProfile(BaseModel):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    user = models.OneToOneField(
        'sha_accounts.User',
        related_name='profile',
        on_delete=models.CASCADE)
