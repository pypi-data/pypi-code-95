from django.db import models

# Create your models here.
class SecretParametrizer(models.Model):
    name = models.CharField("Name", max_length=64, blank=True, null=True)
    code = models.CharField("Code", max_length=64, blank=True, null=True)
    description = models.TextField(
        "Description", null=True, blank=True
    )
    url_to_call = models.TextField(
        "URL", null=True, blank=True
    )
    token = models.TextField(
        "TOKEN", null=True, blank=True
    )
    key = models.CharField("Key", max_length=64, blank=True, null=True)
    switch = models.BooleanField("Switch On/Off", default=False)
    
    