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
#

import datetime
import logging
from typing import List

import arrow
import pytz
from datetimerange import DateTimeRange
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _

from nobinobi_staff.models import RightTraining, Staff, Training, Absence


class Command(BaseCommand):
    help = _("Command for update training for all staff.")

    def add_arguments(self, parser):
        parser.add_argument('--year', nargs='+')

    def handle(self, *args, **options):
        years = options.get("year")
        if years:
            rt = RightTraining.objects.first()
            if rt:
                utc_tz = pytz.timezone("UTC")
                for year in years:
                    start_date = arrow.get(datetime.date(int(year), rt.start_month, rt.start_day), utc_tz)
                    end_date = start_date.shift(years=1, days=-1)
                    absences = Absence.objects.filter(start_date__lte=end_date.datetime, end_date__gte=start_date.datetime,
                                                      abs_type__abbr='FOR', )
                    for absence in absences:
                        # absence
                        # on cree le range de cette absence
                        # abs_start_date = absence.start_date
                        # abs_end_date = absence.end_date
                        absence_range = absence.range_absence

                        # on récupère que training est concerné par cette absence
                        trs = Training.objects.filter(
                            staff_id=absence.staff_id
                        )
                        if trs:
                            absence_in_tr = Absence.objects.filter(
                                staff_id=absence.staff_id,
                                abs_type__abbr='FOR',
                            )
                            for tr in trs:
                                # cree le total
                                total_form = 0.0

                                # on cree le range du tr
                                tr_start_datetime = utc_tz.localize(
                                    datetime.datetime.combine(tr.start_date, datetime.time(0, 0, 0, 0)))
                                tr_end_datetime = utc_tz.localize(
                                    datetime.datetime.combine(tr.end_date, datetime.time(23, 59, 59, 999999)))
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
                    logging.info(_("Staff training courses are updated for the year {}.".format(str(year))))
                    self.stdout.write(_("Staff training courses are updated for the year {}.".format(str(year))))
            else:
                logging.info(_("There's no right to information training."))
                self.stdout.write(_("There's no right to information training."))
