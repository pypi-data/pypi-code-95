from django import forms
from django.utils.translation import ugettext_lazy as _


class EventSignupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.form_object = kwargs.pop("form_object")  # noqa
        super().__init__(*args, **kwargs)
        first_name = forms.fields.CharField(
            label=_("Prénom (*)"),
            max_length=256,
            label_suffix="",
            required=True,
        )

        last_name = forms.fields.CharField(
            label=_("Nom (*)"),
            max_length=256,
            label_suffix="",
            required=True,
        )

        dob = forms.fields.DateField(
            label=_("Date de naisssance (*)"),
            required=True,
        )

        initial_fields = {
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
        }
        self.fields = initial_fields | self.form_object.get_form_fields()
