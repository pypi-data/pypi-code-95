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
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext as _


class AddOfficialHolidayForm(forms.Form):
    """form de validation pour l'ajout"""

    def __init__(self, *args, **kwargs):
        super(AddOfficialHolidayForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        # self.helper.
        self.helper.form_class = 'form-horizontal blueForms'
        self.helper.label_class = ""
        self.helper.field_class = "col-lg-12"
        self.helper.add_input(Submit('submit', _("Submit")))
