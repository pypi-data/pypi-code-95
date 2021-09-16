#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django.db.models import Count
from django.http.response import (
    JsonResponse, HttpResponse, HttpResponseBadRequest, Http404)
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View

from djangokit.views.controller import Controller

from textrank.conf import JSON_DUMPS_PARAMS
from textrank.forms import (
    GroupForm, KeywordForm, RankForm, RegForm, WeightForm, SampleForm,
)
from textrank.models import Group, Keyword, Weight, Sample
from textrank.views.base import (
    get_default_context, UserAccessMixin, ApiAccessMixin, BaseModelView,
)


class IndexView(UserAccessMixin, TemplateView):
    template_name = 'textrank/index.html'

    @property
    def extra_context(self):
        ctx = get_default_context()
        # Группы
        groups = Group.objects.order_by('name')
        ctx['all_groups'] = groups
        ctx['last_groups'] = groups.order_by('-updated', 'name')[:3]
        ctx['active_groups'] = groups.filter(is_active=True)
        ctx['notactive_groups'] = groups.filter(is_active=False)
        # Ключевые слова
        keywords = Keyword.objects.order_by('word')
        ctx['all_keywords'] = keywords
        ctx['last_keywords'] = keywords.order_by('-updated', 'word')[:5]
        ctx['active_keywords'] = keywords.filter(is_active=True)
        ctx['notactive_keywords'] = keywords.filter(is_active=False)
        # Последние досбавленные веса
        weights = Weight.objects.select_related('group', 'keyword')
        ctx['last_weights'] = weights.order_by('-updated', 'keyword__word')[:8]
        return ctx

    def get(self, request):
        """Отображает главную страницу настройки анализа."""
        ctx = self.get_context_data()
        ctx['form'] = RegForm(initial=request.GET)
        return self.render_to_response(ctx)

    def post(self, request):
        """Отображает главную страницу настройки анализа."""
        ctx = self.get_context_data()
        ctx['form'] = form = RegForm(request.POST)
        if form.is_valid():
            ctx['result'] = form.save(request.user)
            cdata = form.cleaned_data
            ctx['form'] = RegForm(initial={
                'groups': ','.join(cdata['groups']),
                'weight': cdata['weight'],
            })
        return self.render_to_response(ctx)


def group_serializer(group):
    data = {
        'id': group.id,
        'created': group.created,
        'updated': group.updated,
        'name': group.name,
        'is_active': group.is_active,
        'last_editor': None,
    }
    last_editor = group.last_editor
    if last_editor:
        data['last_editor'] = [last_editor.id, str(last_editor)]
    return data


class GroupController(Controller):
    serializer = group_serializer
    select_related = ('last_editor',)
    filtering_fields = [f.name for f in Group._meta.fields] + [
        'keywords_count',
    ]
    ordering_fields = [
        f.name for f in Group._meta.fields if not f.related_model
    ] + ['keywords_count']

    def get_queryset(self):
        qs = self.model.objects.all()
        qs = qs.annotate(keywords_count=Count('weights'))
        return qs


class GroupsView(UserAccessMixin, BaseModelView):
    template_name = 'textrank/groups.html'
    ctrl = GroupController(Group)
    model = Group
    form = GroupForm


def keyword_serializer(keyword):
    data = {
        'id': keyword.id,
        'created': keyword.created,
        'updated': keyword.updated,
        'word': keyword.word,
        'is_active': keyword.is_active,
        'last_editor': None,
    }
    last_editor = keyword.last_editor
    if last_editor:
        data['last_editor'] = [last_editor.id, str(last_editor)]
    if keyword.id:
        qs = Weight.object.select_related('group', 'last_editor')
        qs = qs.filter(keyword=keyword)

        def serialize_weight(w):
            g = w.group
            dic = {
                'group': [g.id, g.name],
                'value': w.value,
            }
            le = w.last_editor
            if le:
                dic['last_editor'] = [le.id, str(le)]
            return dic

        data['weights'] = [serialize_weight(w) for w in qs]

    return data


class KeywordsView(UserAccessMixin, BaseModelView):
    template_name = 'textrank/keywords.html'
    ctrl = Controller(Keyword, serializer=keyword_serializer)
    ctrl.select_related = ('last_editor',)
    ctrl.prefetch_related = ('weights',)
    model = Keyword
    form = KeywordForm

    def get_default_context(self):
        ctx = super().get_default_context()
        ctx['groups'] = Group.objects.all()
        return ctx


class RankView(ApiAccessMixin, TemplateView):
    template_name = 'textrank/rank.html'

    def get(self, request, format='html'):
        """Отображает форму на странице."""

        if format not in ('html', 'text', 'json'):
            raise Http404(_('Неверный формат.'))

        ctx = get_default_context()
        ctx['format'] = format
        ctx['form'] = RankForm(initial=request.GET)
        return self.render_to_response(ctx)

    def post(self, request, format='html'):
        """Ранжирует текст и выдаёт результат формой, текстом или в JSON."""

        if format not in ('html', 'text', 'json'):
            raise Http404(_('Неверный формат.'))

        params = request.POST
        form = RankForm(params)
        # HTML
        if format == 'html':
            ctx = get_default_context()
            ctx['form'] = form
            ctx['format'] = format
            if form.is_valid():
                ctx['result'] = form.result_as_data()
            return self.render_to_response(ctx)
        # Plain text
        if format == 'text':
            if form.is_valid():
                return HttpResponse(form.result_as_text())
            return HttpResponseBadRequest(str(form.errors))
        # JSON
        if form.is_valid():
            data = form.result_as_data()
        else:
            data = {
                'errors': form.errors.get_json_data(),
            }
        return JsonResponse(data, json_dumps_params=JSON_DUMPS_PARAMS)


class WeightFormView(UserAccessMixin, View):
    """Представление для добавления или изменения веса."""

    def post(self, request, id=None):
        if id:
            weight = get_object_or_404(Weight, id=id)
        else:
            weight = Weight()
        form = WeightForm(request.POST, instance=weight, request=request)
        if form.is_valid():
            form.save()
            if 'next' in request.POST:
                return redirect(request.POST['next'])
            data = {'success': True}
        else:
            data = {'errors': form.errors.get_json_data(escape_html=True)}
        return JsonResponse(data, json_dumps_params=JSON_DUMPS_PARAMS)


def sample_serializer(sample):
    group = sample.group
    data = {
        'id': sample.id,
        'created': sample.created,
        'updated': sample.updated,
        'message': sample.message,
        'checksum': sample.checksum,
        'group': [group.id, str(group)],
        'last_editor': None,
    }
    last_editor = sample.last_editor
    if last_editor:
        data['last_editor'] = [last_editor.id, str(last_editor)]
    return data


class SampleController(Controller):
    serializer = sample_serializer
    select_related = ('group', 'last_editor',)
    search_fields = ['message']


class SamplesView(UserAccessMixin, BaseModelView):
    template_name = 'textrank/samples.html'
    ctrl = SampleController(Sample)
    model = Sample
    form = SampleForm

    def get_default_context(self):
        ctx = super().get_default_context()
        ctx['groups'] = Group.objects.all()
        return ctx
