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

import arrow
from django.contrib import messages, admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse
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
        context['title'] = _('Add official holidays')
        context.update(admin.site.each_context(self.request))
        return context

    def form_valid(self, form):
        F, J, L = holidays(arrow.now(tz="Europe/Paris").year, 3, '/')
        for i in range(0, len(F)):
            try:
                jf = Holiday(name=L[i], date=arrow.Arrow.strptime(F[i], "%d/%m/%Y").date())
                jf.save()
                messages.success(self.request, _("The day {0} ({1}) has been added to the database.").format(L[i],
                                                                                                             arrow.Arrow.strptime(
                                                                                                                 F[i],
                                                                                                                 "%d/%m/%Y").date()))
            except IntegrityError:
                messages.error(self.request, _("The day {0} ({1}) already exists in the database.").format(L[i],
                                                                                                           arrow.Arrow.strptime(
                                                                                                               F[i],
                                                                                                               "%d/%m/%Y").date()))
        return HttpResponseRedirect(reverse("nobinobi_core:add_official_holiday"))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
