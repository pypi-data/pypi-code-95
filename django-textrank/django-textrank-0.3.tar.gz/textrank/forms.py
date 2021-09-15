#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from textrank.analyzer import analyze_text
from textrank.models import Group, Keyword, Weight, Sample
from textrank.validators import keyword_validator


class LastEditorMixin:
    request = None

    def __init__(self, *args, request, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        user = self.request.user
        if not user.is_authenticated:
            user = None
        instance.last_editor = user
        if commit:
            instance.save()
            self._save_m2m()
        return instance


class GroupForm(LastEditorMixin, forms.ModelForm):

    class Meta:
        model = Group
        exclude = []


class KeywordForm(LastEditorMixin, forms.ModelForm):

    class Meta:
        model = Keyword
        exclude = []


class WeightForm(LastEditorMixin, forms.ModelForm):

    class Meta:
        model = Weight
        exclude = []

    def clean(self):
        cdata = super().clean()
        if 'group' in cdata and 'keyword' in cdata:
            qs = Weight.objects.filter(
                group=cdata['group'], keyword=cdata['keyword'],
            )
            pk = self.instance.pk
            if pk:
                qs = qs.exclude(pk=pk)
            if qs.exists():
                raise forms.ValidationError(
                    _('Такой вес уже зарегистрирован с другим ID.'))
        return cdata


class SampleForm(LastEditorMixin, forms.ModelForm):

    class Meta:
        model = Sample
        exclude = []

    def clean(self):
        cdata = super().clean()
        if 'group' in cdata and 'message' in cdata:
            checksum = Sample.get_checksum(cdata['message'])
            qs = Sample.objects.filter(group=cdata['group'], checksum=checksum)
            pk = self.instance.pk
            if pk:
                qs = qs.exclude(pk=pk)
            if qs.exists():
                raise forms.ValidationError(
                    _('Такой образец уже зарегистрирован для данной группы.'))
        return cdata


class RankForm(forms.Form):
    """
    Форма анализатора текста.
    """
    text = forms.CharField(label=_('Текст'), widget=forms.Textarea())
    verbose = forms.BooleanField(
        required=False, initial=True, label=_('Подробно'))
    result = None

    def analyze(self):
        cdata = self.cleaned_data
        result = analyze_text(cdata['text'])
        if not cdata['verbose']:
            result.pop('words')
            result.pop('morph')
            result.pop('other')
            result.pop('utime')
        self.result = result

    def clean(self):
        cdata = super().clean()
        if 'text' in cdata and 'verbose' in cdata:
            self.analyze()
        return cdata

    def result_as_text(self):
        return self.result['group'].get('name', '')

    def result_as_data(self):
        return self.result


class RegForm(forms.Form):
    """
    Форма регистрации слова в группе с указанием его веса.
    """
    keyword = forms.CharField(
        required=True, min_length=2, max_length=100,
        validators=[keyword_validator],
        label=_('Cлово или сочетание'),
        help_text=Keyword._meta.get_field('word').help_text,
    )
    groups = forms.CharField(
        required=True,
        label=_('Группы'),
        help_text=Group._meta.get_field('name').help_text,
    )
    weight = forms.IntegerField(
        required=True, initial=1, min_value=1, max_value=32767,
        label=_('Вес'),
    )

    def clean_groups(self):
        groups = self.cleaned_data['groups'].split(',')
        groups = set([g for g in groups if 0 < len(g) <= 50])
        if not groups:
            raise ValidationError(_('Список не содержит корректных названий.'))
        return groups

    def save(self, user):
        if not user.is_authenticated:
            user = None
        cdata = self.cleaned_data
        keyword, cr = Keyword.objects.get_or_create(
            word=cdata['keyword'].lower(),
            defaults={'last_editor': user}
        )
        for group_name in cdata['groups']:
            group, cr = Group.objects.get_or_create(
                name=group_name,
                defaults={'last_editor': user}
            )
            weight, cr = Weight.objects.get_or_create(
                group=group,
                keyword=keyword,
                defaults={'value': cdata['weight'], 'last_editor': user}
            )
            if not cr:
                weight.value = cdata['weight']
                weight.last_editor = user
                weight.save()
        return keyword
