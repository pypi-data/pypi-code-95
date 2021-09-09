from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import FachschaftUser


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class FachschaftUserForm(ModelForm):
    class Meta:
        model = FachschaftUser
        fields = ['nickname', 'studiengang', 'studienabschnitt', 'gender']
