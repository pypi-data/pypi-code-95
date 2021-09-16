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

import arrow
from bootstrap_datepicker_plus import DatePickerInput
from datetimerange import DateTimeRange
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.utils import timezone
from django.utils.translation import gettext as _
from nobinobi_staff.models import Absence, RightTraining


class AbsenceAdminForm(forms.ModelForm):
    """ Formulaire pour le admin absence"""

    class Meta:
        model = Absence
        fields = '__all__'

        """Constructor for AbsenceAdminForm"""

    def clean(self):
        cleaned_data = super().clean()
        # get value
        staff = cleaned_data.get('staff')
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        # check if start_date is before end_date else raise error
        if start_date > end_date:
            raise forms.ValidationError(_('The start date must be before the end date.'), code='invalid')
        # create a range from form
        form_absence_range = DateTimeRange(start_date, end_date)
        # get absences
        absences = Absence.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
            staff_id=staff.id
        ).exclude(pk=self.instance.pk)
        for absence in absences:
            # create a range absence
            absence_range = DateTimeRange(absence.start_date, absence.end_date)
            # if form range is intersection with absence range raise error
            if form_absence_range.is_intersection(absence_range):
                raise forms.ValidationError(_('An absence already exists on these dates.'), code='invalid')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        try:
            kwargs['instance']
        except KeyError:
            # on set le initial sur les dates
            try:
                kwargs['initial']
            except KeyError:
                kwargs['initial'] = {}
            finally:
                kwargs['initial']['all_day'] = True
                kwargs['initial']['start_date'] = arrow.now().replace(hour=6, minute=0, second=0)
                kwargs['initial']['end_date'] = arrow.now().replace(hour=20, minute=0, second=0)
        else:
            pass
        super(AbsenceAdminForm, self).__init__(*args, **kwargs)


class RightTrainingAdminForm(forms.ModelForm):
    date = forms.DateField(
        label=_("Start date"),
        widget=AdminDateWidget(),
        # widget=DatePickerInput(options={
        #     "locale": "fr",
        #     "format": "DD/MM/YYYY"
        # }),
    )

    class Meta:
        model = RightTraining
        fields = ("number_days", "date", "start_month", "start_day")

    def save(self, commit=True):
        form = self.instance
        form.start_month = self.cleaned_data.get("date").month
        form.start_day = self.cleaned_data.get("date").day
        form.save()

        return super(RightTrainingAdminForm, self).save(commit)
