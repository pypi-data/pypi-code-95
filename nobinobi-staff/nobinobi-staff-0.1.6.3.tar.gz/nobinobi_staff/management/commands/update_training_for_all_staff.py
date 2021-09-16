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

import arrow
import pytz
from datetimerange import DateTimeRange
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from nobinobi_staff.models import RightTraining, Training, Absence


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
                    end_date = start_date.shift(years=1, days=-1).replace(hour=23, minute=59, second=59,
                                                                          microsecond=999999)

                    trs = Training.objects.filter(start_date__lte=end_date.date(), end_date__gte=start_date.date())
                    if trs.exists():
                        for tr in trs:
                            # on cree le range du tr
                            tr_start_datetime = utc_tz.localize(
                                datetime.datetime.combine(tr.start_date, datetime.time(0, 0, 0, 0)))
                            tr_end_datetime = utc_tz.localize(
                                datetime.datetime.combine(tr.end_date, datetime.time(23, 59, 59, 999999)))
                            tr_range = DateTimeRange(tr_start_datetime, tr_end_datetime)

                            absences = Absence.objects.filter(start_date__lte=tr_end_datetime,
                                                              end_date__gte=tr_start_datetime,
                                                              abs_type__abbr='FOR',
                                                              staff__id=tr.staff_id)

                            # cree le total
                            total_form = 0.0

                            for absence in absences:
                                # absence
                                # on cree le range de cette absence
                                absence_range = absence.datetime_range

                                # si l'absence est en interaction avec le tr
                                if absence_range.is_intersection(tr_range):
                                    absence_in_tr = absence_range.intersection(tr_range)
                                    for value in absence_in_tr.range(datetime.timedelta(days=1)):
                                        if tr_start_datetime <= value <= tr_end_datetime:
                                            if absence.all_day:
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
