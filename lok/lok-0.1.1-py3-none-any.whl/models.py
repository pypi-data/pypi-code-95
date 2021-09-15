from django.db import models# Create your models here.
from django.contrib.auth.models import AbstractUser

class LokUser(AbstractUser):
    """ A reflection on the real User"""
    email = models.EmailField(unique=True)
    roles = models.JSONField(null=True, blank=True)