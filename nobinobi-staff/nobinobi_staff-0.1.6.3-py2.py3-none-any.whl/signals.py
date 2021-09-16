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
from datetimerange import DateTimeRange
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from nobinobi_staff.models import Staff, Training, RightTraining, Absence


def create_training_for_staff(instance: Staff):
    now = timezone.localdate()
    rt = RightTraining.objects.first()
    # +1 for accept 12 in range
    if rt:
        if rt.start_month in range(9, 12 + 1):
            if now.month in range(9, 13):
                start_date = datetime.date(timezone.localdate().year, rt.start_month, rt.start_day)
            else:
                start_date = datetime.date(timezone.localdate().year - 1, rt.start_month, rt.start_day)
        else:
            if now.month in range(9, 13):
                start_date = arrow.get(datetime.datetime(timezone.localdate().year, rt.start_month, rt.start_day))
            else:
                start_date = arrow.get(datetime.datetime(timezone.localdate().year - 1, rt.start_month, rt.start_day))
        end_date = arrow.get(start_date).shift(years=1, days=-1).date()

        training, created = Training.objects.get_or_create(
            staff=instance,
            start_date=start_date,
            end_date=end_date,
        )
        if created:
            ta = instance.percentage_work
            training.default_number_days = (rt.number_days * ta) / 100
            training.save()


@receiver(post_save, sender=Staff)
def update_training_for_staff(sender, instance, created, raw, using, **kwargs):
    create_training_for_staff(instance)


@receiver(post_save, sender=Absence)
def create_training_for_staff_after_absence(sender, instance, created, raw, using, **kwargs):
    create_training_for_staff(instance.staff)


@receiver(post_save, sender=Absence)
def update_training_for_staff_after_absence(sender, instance, **kwargs):
    # on cree le range de cette absence
    # abs_start_date = absence.start_date
    # abs_end_date = absence.end_date
    if instance.abs_type.abbr == "FOR":
        absence_range = instance.datetime_range

        old_absence_start_date = instance.tracker.previous("start_date")
        old_absence_end_date = instance.tracker.previous("end_date")
        old_absence_range = DateTimeRange(old_absence_start_date, old_absence_end_date)

        if absence_range != old_absence_range:
            # on récupère que training est concerné par cette absence
            trs = Training.objects.filter(
                staff_id=instance.staff_id
            )
            if trs:
                for tr in trs:
                    # cree le total
                    tr_range = tr.datetime_range
                    # si l'absence est en interaction avec le tr
                    if absence_range.is_intersection(tr_range):
                        for value in absence_range.range(datetime.timedelta(days=1)):
                            if tr_range.start_datetime <= value <= tr_range.end_datetime:
                                if instance.all_day:
                                    tr.number_days += 1
                                else:
                                    tr.number_days += 0.5
                        tr.save()
                    if old_absence_start_date and old_absence_end_date:
                        if old_absence_range.is_intersection(tr_range):
                            for value in old_absence_range.range(datetime.timedelta(days=1)):
                                if tr_range.start_datetime <= value <= tr_range.end_datetime:
                                    if instance.all_day:
                                        tr.number_days -= 1
                                    else:
                                        tr.number_days -= 0.5
                            tr.save()


@receiver(post_delete, sender=Absence)
def update_training_for_staff_after_absence(sender, instance, **kwargs):
    # on cree le range de cette absence
    if instance.abs_type.abbr == "FOR":
        absence_range = instance.datetime_range
        # on récupère que training est concerné par cette absence
        trs = Training.objects.filter(
            staff_id=instance.staff_id
        )
        if trs:
            for tr in trs:
                # cree le total
                tr_range = tr.datetime_range
                # si l'absence est en interaction avec le tr
                if absence_range.is_intersection(tr_range):
                    for value in absence_range.range(datetime.timedelta(days=1)):
                        if tr_range.start_datetime <= value <= tr_range.end_datetime:
                            if instance.all_day:
                                tr.number_days -= 1
                            else:
                                tr.number_days -= 0.5
                    tr.save()
