import uuid
from decimal import Decimal
from ool import VersionField, VersionedMixin
from django.core.validators import MinValueValidator
from django.db import models


class TicketBase(VersionedMixin, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('Title', max_length=50)
    price = models.DecimalField('Price', max_digits=10, decimal_places=4,
                                validators=[MinValueValidator(Decimal('0.01'))])
    version = VersionField()

    class Meta:
        abstract = True


class OrderBase(VersionedMixin, models.Model):
    CREATED = 'created'
    CANCELLED = 'cancelled'
    AWAITINGPAYMENT = 'awaiting_payment'
    COMPLETE = 'complete'
    STATUS_CHOICES = [
        (CREATED, 'created'),
        (CANCELLED, 'cancelled'),
        (AWAITINGPAYMENT, 'awaiting_payment'),
        (COMPLETE, 'complete')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField('User ID', max_length=36)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=CREATED)
    version = VersionField()

    class Meta:
        abstract = True
