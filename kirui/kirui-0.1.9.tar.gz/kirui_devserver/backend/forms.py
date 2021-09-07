import datetime

from django import forms
from django.forms import widgets
from django_kirui.widgets import CheckboxSwitch
from kirui_devserver.backend.models import Topic, Activity


class SampleForm(forms.ModelForm):
    harmadik = forms.MultipleChoiceField(label='Harmadik', choices=[(1, "One\\aaaasdfsdfsdf'"), (2, 'Two'), (3, 'Three')], initial=[1, 2],
                                         widget=widgets.CheckboxSelectMultiple)
    masodik = forms.ChoiceField(label='Próba választó', choices=[(1, 'One'), (2, 'Two'), (3, 'Three')])
    """elso = forms.CharField(label='Próba felirat', required=False)
    
    masodik = forms.ChoiceField(label='Próba választó', choices=[(None, '-----------------'), (1, 'One'), (2, 'Two'), (3, 'Three')], initial=None)
    negyedik = forms.BooleanField(label='Valami', widget=CheckboxSwitch)
    otodik = forms.BooleanField(label='Ötödik', widget=CheckboxSwitch)
    hatodik = forms.IntegerField(label='Hatodik')
    hetedik = forms.DateField(label='Hetedik')  # , initial='2020-03-04')
    nyolcadik = forms.CharField(label='Nyolcadik', widget=widgets.Textarea)"""

    class Meta:
        model = Activity
        fields = ['topics', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['elso'].initial = str(datetime.datetime.now())
