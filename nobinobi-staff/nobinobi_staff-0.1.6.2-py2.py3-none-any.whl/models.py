# coding=utf-8

#  Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import uuid

import arrow
from datetimerange import DateTimeRange
from django.conf import settings
from django.db import models
from django.db.models.functions import Upper
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import StatusField, TimeStampedModel, StatusModel

GENDER_CHOICE = Choices(
    (0, "man", _('Man')),
    (1, "woman", _('Woman')),
    (2, "other", _('Other'))
)


class Staff(TimeStampedModel, StatusModel):
    """Models to store staff information"""

    STATUS = Choices(
        ('active', _("Active")),
        ('archived', _("Archived")),
    )

    class CivilStatusChoice(models.TextChoices):
        __empty__ = _('(Unknown)')
        SINGLE = "single", _('Single')
        MARRIED = "married", _('Married')
        REGPART = "registered_partnership", _('Registered Partnership')
        SEPARATED = "separate", _('Separate')
        DIVORCED = "divorced", _('Divorced')
        WIDOWER = "widower", _('Widower')

    def upload_picture(self, filename):
        f, ext = os.path.splitext(filename)
        upload_to = "staff/%s/" % self.racc
        return '%s%s%s' % (upload_to, uuid.uuid4().hex, ext)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        null=True,
        blank=True,
    )
    last_name = models.CharField(_("Last name"), max_length=255)
    first_name = models.CharField(_("First name"), max_length=255)
    gender = models.SmallIntegerField(choices=GENDER_CHOICE, verbose_name=_("Gender"), blank=False, null=True)
    birth_date = models.DateField(verbose_name=_("Birth Date"), blank=True, null=True)
    picture = models.ImageField(_("Picture"), upload_to=upload_picture, blank=True, null=True)
    street = models.CharField(_('Street'), max_length=255, null=True, blank=True)
    zip = models.PositiveIntegerField(_('ZIP'), null=True, blank=True)
    city = models.CharField(_('City'), max_length=50, null=True, blank=True)
    phone = models.CharField(_('Phone'), max_length=50, null=True, blank=True)
    mobile_phone = models.CharField(_('Mobile phone'), max_length=50, null=True, blank=True)
    nationality = models.CharField(_("Nationality"), max_length=255, blank=True, null=True)
    civil_status = models.CharField(_("Civil status"), max_length=25, choices=CivilStatusChoice.choices,
                                    default=CivilStatusChoice.__empty__, blank=True,
                                    null=True)
    social_security_number = models.CharField(_('Social security number'), max_length=50, null=True, blank=True)
    email = models.EmailField(_('Email'), null=True, blank=True)
    team = models.ForeignKey(
        to="Team",
        verbose_name=_('Team'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    qualification = models.ForeignKey(
        'Qualification',
        verbose_name=_("Qualification"),
        on_delete=models.SET_NULL,
        blank=False,
        null=True
    )
    percentage_work = models.FloatField(verbose_name=_("Percentage of work"), default=0)
    working_time = models.FloatField(_("Working time"))
    working_base = models.FloatField(verbose_name=_("Working base"), default=40)

    active_status = models.BooleanField(verbose_name=_("Active"), default=True)
    arrival_date = models.DateField(_("Arrival date"), null=True)
    departure_date = models.DateField(_("Departure Date"), null=True, blank=True)

    def _get_racc_name(self):
        """Get short name for staff"""
        return '%s%s' % (slugify(str.lower(self.first_name[:2])), slugify(str.lower(self.last_name[:1])))

    racc = property(_get_racc_name)

    @property
    def full_name(self):
        """Get fullname of staff"""
        return "{0} {1}".format(self.first_name, self.last_name)

    def __str__(self):  # __unicode__ on Python 2
        """Returns the staff's full name."""
        return '%s %s' % (self.first_name, self.last_name)  #

    def save(self, *args, **kwargs):
        """Save the Staff models

        Args:
            *args:
            **kwargs:
        """
        self.last_name = self.last_name.title()
        self.first_name = self.first_name.title()
        percentage = self.percentage_work
        # on check si le percentage est entre 0 et 100
        if percentage <= 100 or percentage > 0:
            # on init les valeurs constantes
            base_work = self.working_base
            # on defini le travail
            work = (percentage / 100) * base_work
            self.working_time = work

        return super(Staff, self).save(*args, **kwargs)

    class Meta:
        """Set information of class Staff"""
        ordering = ['first_name', 'last_name']
        verbose_name_plural = _("Staffes")
        verbose_name = _("Staff")
        permissions = (("can_read_list", "Can read list"),)


class Qualification(models.Model):
    """Models for store Qualification"""
    name = models.TextField(_("Name"))
    short_name = models.CharField(_("Short name"), max_length=255)
    order = models.IntegerField(_("Order"), default=1)

    class Meta:
        """Set information of class Qualification"""
        ordering = ('order',)

    def __str__(self):
        """return name of qualification"""
        return self.name


class Absence(models.Model):
    """Models for store Absence"""
    staff = models.ForeignKey(
        Staff,
        verbose_name=_("Staff"),
        related_name="staff",
        on_delete=models.CASCADE
    )
    abs_type = models.ForeignKey(
        "AbsenceType",
        verbose_name=_("Absence type"),
        on_delete=models.PROTECT,
        blank=False,
        null=True
    )
    start_date = models.DateTimeField(_("Start date"))
    end_date = models.DateTimeField(_("End date"))
    all_day = models.BooleanField(_("All day"), default=False)
    comment = models.TextField(_("Comment"), blank=True, null=True)
    partial_disability = models.IntegerField(_("Partial disability"), blank=True, null=True,
                                             help_text=_("In percentage %"))

    def __str__(self):
        """Return de str for absence

        Returns:
            str: ""
        """
        return '%s | %s | %s - %s' % (
            self.staff, self.abs_type, arrow.get(self.start_date).format("DD-MM-YYYY"),
            arrow.get(self.end_date).format("DD-MM-YYYY"))

    def _get_range_absence(self):
        """
        Returns:
            DateTimeRange:
        """
        return DateTimeRange(self.start_date, self.end_date)

    range_absence = property(_get_range_absence)


class AbsenceType(models.Model):
    reason = models.CharField(_("Reason"), max_length=255)
    abbr = models.CharField(_("Abbreviation"), max_length=3, default="000")

    class Meta:
        verbose_name = _("Absence type")
        verbose_name_plural = _("Absences type")

    def __str__(self):  # __unicode__ on Python 2
        return "{} - {}".format(self.abbr, self.reason)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # save abbreviation in CAPITAL
        """
        Args:
            force_insert:
            force_update:
            using:
            update_fields:
        """
        if self.abbr:
            Upper(self.abbr)
        return super(AbsenceType, self).save()


class Team(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    slug = models.SlugField(verbose_name=_("Slug"), max_length=150, unique=True)
    order = models.PositiveIntegerField(verbose_name=_("Order"), unique=True, blank=False, null=True)

    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")

    def __str__(self):
        return self.name

    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while Team.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        if not self.slug:
            self.slug = self._get_unique_slug()
        super(Team, self).save(*args, **kwargs)


class AbsenceAttachment(models.Model):
    ATTACHMENT_TYPE = Choices(
        ("medical", _("Medical certificate")),
        ("work", _("Work Certificate")),
    )

    def generate_new_filename(self, filename):
        """
        Args:
            filename:
        """
        f, ext = os.path.splitext(filename)
        upload_to = "staff/{}/absence/".format(self.absence.staff.racc)
        return '{}{}{}'.format(upload_to, uuid.uuid4().hex, ext)

    type = StatusField(_("Type"), choices_name="ATTACHMENT_TYPE")
    file = models.FileField(_("File"), upload_to=generate_new_filename, blank=True, null=True)
    absence = models.ForeignKey(
        verbose_name=_("Absence"),
        to="Absence",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Absence attachment")
        verbose_name_plural = _("Absence attachments")

    def __str__(self):
        return "".format(self.absence, self.file)


class RightTraining(models.Model):
    """Model to store variable for right to training"""
    MONTH_CHOICES = Choices(
        (1, _("January")),
        (2, _("February")),
        (3, _("Mars")),
        (4, _("April")),
        (5, _("May")),
        (6, _("June")),
        (7, _("July")),
        (8, _("August")),
        (9, _("September")),
        (10, _("October")),
        (11, _("November")),
        (12, _("December")),
    )

    number_days = models.IntegerField(_("Number of days"), help_text=_(
        "Number of days of training entitlement based on a 100% activity rate."))
    start_day = models.IntegerField(_("Start day"), choices=((x, x) for x in range(0, 32, 1)))
    start_month = models.IntegerField(_("Start month"), choices=MONTH_CHOICES)

    class Meta:
        # ordering = ('date',)
        verbose_name = _('Right to training')
        # verbose_name_plural = _('')

    def __str__(self):
        return str(self.number_days)


class Training(TimeStampedModel):
    """Models to store for a staff number exactly have"""
    default_number_days = models.FloatField(_("Number of days"), default=0.0)
    number_days = models.FloatField(_("Number of days"), default=0.0)
    start_date = models.DateField(_("Start date"), editable=False)
    end_date = models.DateField(_("End date"), editable=False)
    staff = models.ForeignKey(
        to=Staff,
        on_delete=models.CASCADE,
        verbose_name=_("Staff"),
        editable=False
    )

    class Meta:
        ordering = ('start_date', 'end_date',)
        verbose_name = _('Training')
        unique_together = ('start_date', 'end_date', 'staff')
        # verbose_name_plural = _('')

    def __str__(self):
        return "{} - {} - {}".format(self.staff.full_name, self.default_number_days, self.number_days)
