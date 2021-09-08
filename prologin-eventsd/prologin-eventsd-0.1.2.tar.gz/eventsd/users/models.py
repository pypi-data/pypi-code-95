from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    address = models.TextField(
        max_length=1000,
        verbose_name=_("Adresse"),
        null=True,
        blank=True,
    )

    city = models.CharField(
        verbose_name=_("Ville"),
        max_length=150,
        null=True,
        blank=True,
    )

    zip_code = models.CharField(
        verbose_name=_("Code Postal"),
        max_length=20,
        null=True,
        blank=True,
    )

    country = models.CharField(
        verbose_name=_("Pays"),
        max_length=64,
        null=True,
        blank=True,
    )

    email = models.EmailField(
        null=False,
        blank=False,
        verbose_name=_("Adresse email"),
        unique=True,
    )

    def has_complete_address(self):
        return not any(
            f is None
            for f in (
                self.address,
                self.city,
                self.zip_code,
                self.country,
            )
        )
