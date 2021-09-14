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

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView
from rest_framework import viewsets

from nobinobi_staff.serializers import StaffSerializer
from .models import Staff


class ViewIndex(TemplateView):
    template_name = 'base.html'


class ListStaffReadOnly(TemplateView, LoginRequiredMixin, object):
    template_name = "staff/staff_list_readonly.html"

    def get(self, request, *args, **kwargs):
        """
        Args:
            request:
            *args:
            **kwargs:
        """
        context = self.get_context_data(**kwargs)
        context['title'] = _("Staffes list")
        context["staffes"] = Staff.objects.filter(status=Staff.STATUS.active)
        return self.render_to_response(context)


class StaffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Staff.objects.filter(status=Staff.STATUS.active)
    serializer_class = StaffSerializer
