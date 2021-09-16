from django.db import models


class ModelAddressBase(models.Model):

    street = models.CharField(
        'address_street',
        max_length=254,
        blank=False,
    )
    number = models.PositiveSmallIntegerField(
        'address_number',
        blank=False,
    )
    department = models.CharField(
        'address_department',
        max_length=254,
        blank=True,
        null=True,
        default=''
    )
    flat = models.CharField(
        'address_flat',
        max_length=254,
        blank=True,
        null=True,
        default=''
    )

    class Meta:

        abstract = True

    def __str__(self):
        return f"{self.street} {self.number} {self.department} {self.flat}"


class AbstractNameModel(models.Model):
    name = models.CharField(
        'Nombre',
        max_length=100,
        primary_key=True
        )

    class Meta:

        abstract = True

    def __str__(self):
        return f"{self.name}
