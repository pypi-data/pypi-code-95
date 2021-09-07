from debug_toolbar.panels.sql.forms import SQLSelectForm
from django import forms


class Pev2SQLSelectForm(SQLSelectForm):
    stacktrace = forms.CharField()
