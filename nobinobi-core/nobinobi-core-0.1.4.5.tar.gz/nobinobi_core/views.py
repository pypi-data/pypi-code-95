#      Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# -*- coding: utf-8 -*-
import datetime

from django.contrib import messages, admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.text import capfirst
from django.utils.translation import gettext as _
from django.views.generic import FormView

from nobinobi_core.forms import AddOfficialHolidayForm
from nobinobi_core.models import Holiday
from .functions import holidays


class HolidayAddOffical(FormView, LoginRequiredMixin):
    """permet d'ajouter les jour ferie de l'annee dans la base de donnee"""

    template_name = "nobinobi_core/add_official_holiday.html"
    form_class = AddOfficialHolidayForm

    def get_context_data(self, **kwargs):
        context = super(HolidayAddOffical, self).get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        context['title'] = _('Add official holidays')
        return context

    def form_valid(self, form):
        year_selected = int(form.cleaned_data["year"])
        if year_selected:
            F, J, L = holidays(an=year_selected, sd=2)
        else:
            F, J, L = holidays(sd=2)

        for i in range(0, len(F)):
            holiday_date = datetime.datetime.strptime(F[i], "%d/%m/%Y").date()
            holiday_name = capfirst(L[i].lower())
            holiday, created = Holiday.objects.get_or_create(name=holiday_name, date=holiday_date)
            if created:
                messages.success(self.request,
                                 _("The day {0} ({1}) has been added to the database.").format(holiday_name,
                                                                                               holiday_date))
            else:
                messages.error(self.request,
                               _("The day {0} ({1}) already exists in the database.").format(holiday_name,
                                                                                             holiday_date))
        return HttpResponseRedirect(reverse("admin:nobinobi_core_holiday_changelist"))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
