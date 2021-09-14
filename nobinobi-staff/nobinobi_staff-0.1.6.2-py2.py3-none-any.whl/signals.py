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

import datetime

import arrow
import pytz
from datetimerange import DateTimeRange
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import make_aware, make_naive

from nobinobi_staff.models import Staff, Training, RightTraining, Absence


@receiver(post_save, sender=Staff)
def update_training_for_staff(sender, instance, created, raw, using, **kwargs):
    now = timezone.localdate()
    rt = RightTraining.objects.first()
    # +1 for accept 12 in range
    if rt:
        if rt.start_month in range(9, 12 + 1):
            if now.month in range(9, 13):
                start_date = arrow.get(datetime.date(timezone.localdate().year, rt.start_month, rt.start_day))
            else:
                start_date = arrow.get(datetime.date(timezone.localdate().year - 1, rt.start_month, rt.start_day))
            end_date = start_date.shift(years=1, days=-1)
        else:
            if now.month in range(9, 13):
                start_date = arrow.get(datetime.datetime(timezone.localdate().year, rt.start_month, rt.start_day))
            else:
                start_date = arrow.get(datetime.datetime(timezone.localdate().year - 1, rt.start_month, rt.start_day))
            end_date = start_date.shift(years=1, days=-1)
        training, created = Training.objects.get_or_create(
            staff=instance,
            start_date=start_date.date(),
            end_date=end_date.date(),
        )
        if created:
            ta = instance.percentage_work
            training.default_number_days = (rt.number_days * ta) / 100
            training.save()


@receiver(post_save, sender=Absence)
def create_training_for_staff_after_absence(sender, instance, created, raw, using, **kwargs):
    now = timezone.localdate()
    rt = RightTraining.objects.first()
    # +1 for accept 12 in range
    if rt:
        if rt.start_month in range(9, 12 + 1):
            if now.month in range(9, 13):
                start_date = arrow.get(datetime.date(timezone.localdate().year, rt.start_month, rt.start_day))
            else:
                start_date = arrow.get(datetime.date(timezone.localdate().year - 1, rt.start_month, rt.start_day))
            end_date = start_date.shift(years=1, days=-1)
        else:
            if now.month in range(9, 13):
                start_date = arrow.get(datetime.datetime(timezone.localdate().year, rt.start_month, rt.start_day))
            else:
                start_date = arrow.get(datetime.datetime(timezone.localdate().year - 1, rt.start_month, rt.start_day))
            end_date = start_date.shift(years=1, days=-1)
        training, created = Training.objects.get_or_create(
            staff=instance.staff,
            start_date=start_date.date(),
            end_date=end_date.date(),
        )
        if created:
            ta = instance.staff.percentage_work
            training.default_number_days = (rt.number_days * ta) / 100
            training.save()


@receiver((post_save, post_delete), sender=Absence)
def update_training_for_staff_after_absence(sender, instance, **kwargs):
    # absence
    absence = instance

    # on cree le range de cette absence
    # abs_start_date = absence.start_date
    # abs_end_date = absence.end_date
    absence_range = absence.range_absence

    # on récupère que training est concerné par cette absence
    trs = Training.objects.filter(
        staff_id=instance.staff_id
    )
    utc_tz = pytz.timezone("UTC")
    if trs:
        absence_in_tr = Absence.objects.filter(
            staff_id=instance.staff_id,
            abs_type__abbr='FOR',
        )
        for tr in trs:
            # cree le total
            total_form = 0.0

            # on cree le range du tr
            tr_start_datetime = utc_tz.localize(datetime.datetime.combine(tr.start_date, datetime.time(0, 0, 0, 0)))
            tr_end_datetime = utc_tz.localize(datetime.datetime.combine(tr.end_date, datetime.time(23, 59, 59, 999999)))
            tr_range = DateTimeRange(tr_start_datetime, tr_end_datetime)
            # si l'absence est en interaction avec le tr
            if absence_range.is_intersection(tr_range):
                for abs in absence_in_tr:
                    abs_range = abs.range_absence
                    if abs_range.is_intersection(tr_range):
                        for value in abs_range.range(datetime.timedelta(days=1)):
                            if tr_start_datetime <= value <= tr_end_datetime:
                                if abs.all_day:
                                    total_form += 1
                                else:
                                    total_form += 0.5

            tr.number_days = total_form
            tr.save()
