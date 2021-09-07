from copy import deepcopy

from django.contrib import messages
from django.contrib.messages import constants
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django_filters.views import FilterView

from report_designer.core.actions import FormActionGroup


class TitleMixin:
    """
    Миксин заголовка страницы
    """

    title = None

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data.update({
            'title': self.get_title()
        })
        return context_data

    def get_title(self):
        """
        Заголовок страницы
        """
        return self.title


class AjaxResponseMixin:
    """
    Миксин: Ajax-ответ
    """

    # HTTP response class
    ajax_response_class = JsonResponse
    is_only_ajax = False

    def dispatch(self, request, *args, **kwargs):
        if self.is_only_ajax and not self.is_ajax:
            raise Http404('Only allow authorized AJAX requests')
        return super().dispatch(request, *args, **kwargs)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.is_ajax = request.is_ajax()

    def render_to_response(self, context, **response_kwargs):
        """
        Подготовка ответа
        """
        if self.is_ajax:
            return self.render_to_ajax_response(context, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)

    def render_to_ajax_response(self, context=None, render_template=True, **response_kwargs):
        """
        Подготовка Ajax ответа
        """
        response_kwargs.update({
            **(render_template and {'html': self.render_template(context)} or {}),
            **self.additional_ajax_response_kwargs(context, **response_kwargs),
        })
        return self.ajax_response_class(response_kwargs)

    def render_template(self, context, template_names=None):
        """
        Рендеринг шаблона в Ajax-ответ
        """
        if not template_names:
            template_names = hasattr(self, 'get_template_names') and self.get_template_names()
        return render_to_string(template_name=template_names, context=context, request=self.request)

    def additional_ajax_response_kwargs(self, context=None, **kwargs):
        """
        Дополнительные данные для Ajax-ответа
        """
        return {}


class AjaxFormResponseMixin(AjaxResponseMixin):
    """
    Миксин: Ajax-ответ для форм
    """

    success_message = 'Данные успешно сохранены'
    error_message = 'При сохранении данных произошла ошибка'

    def _base_response(self, success, render_template, response_kwargs: dict = None, **context_kwargs):
        """
        Базовый ответ
        """
        context_data = self.get_context_data(**context_kwargs)
        message = success and self.success_message or self.error_message
        response = self.render_to_response(
            context_data,
            render_template=render_template,
            success=success,
            message=message,
            # **(response_kwargs and response_kwargs or {})
        )
        if not self.is_ajax:
            messages.add_message(self.request, success and constants.SUCCESS or constants.ERROR, message)
        return response

    def success_response(self):
        """
        Ответ при успешном действии
        """
        if self.is_ajax:
            return self._base_response(success=True, render_template=False)
        return HttpResponseRedirect(self.get_success_url())

    # def get_success_response_kwargs(self):
    #     """
    #     Дополнительные данные в успешный ответ
    #     """
    #     return {}

    def error_response(self, form):
        """
        Ответ при успешном действии
        """
        return self._base_response(success=False, render_template=True, form=form)


class ActionGroupMixin:
    """
    Пример:

    В шаблоне:
    {{ action_group }} - action_group_class.name
    """

    action_group_classes = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object_for_action_groups()
        if self.can_view_action_groups(obj):
            context.update(self.get_action_groups(obj, **kwargs))
        return context

    def get_object_for_action_groups(self):
        """
        Получение объекта для групп действий
        """
        try:
            return self.get_object_permission()
        except AttributeError:
            return None

    def can_view_action_groups(self, obj) -> bool:
        """
        Проверка, можно ли отобразить группы действий
        """
        return True

    def get_action_groups(self, obj, **kwargs) -> dict:
        """
        Получение групп действий
        """
        action_groups = dict()
        for action_group_class in self.get_action_group_classes():
            group_kwargs = self.get_action_group_kwargs(**kwargs)
            kwargs_by_name = group_kwargs.get(f'kwargs_{action_group_class.name}', dict())
            action_class = action_group_class(self.request.user, obj, **kwargs_by_name)
            action_groups.update({
                action_class.name: action_class,
            })
        return action_groups

    def get_action_group_classes(self):
        """
        Получение классов групп действий
        """
        return deepcopy(self.action_group_classes)

    def get_action_group_kwargs(self, **kwargs):
        """
        Дополнительные параметры для групп действий
        """
        return {}


class DynamicContentMixin(AjaxResponseMixin):
    """
    Представление: Динамическая загрузка контента
    """

    template_name = None
    template_name_content = None

    # URL kwargs типов
    base_type = 'base'
    content_type = 'content'

    ajax_content_name = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Тип запроса из URL
        self.type = kwargs.get('type')

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data.update({
            'content_url': self.get_content_url(),
            'ajax_content_name': self.ajax_content_name
        })
        return context_data

    @property
    def is_content_type(self):
        """
        Тип контента
        """
        return self.type == self.content_type

    @property
    def is_base_type(self):
        """
        Базовый тип
        """
        return self.type == self.base_type

    def get_template_names(self):
        """
        Получение шаблона в зависимости от типа запроса
        """
        if self.is_content_type:
            return [self.template_name_content]
        return super().get_template_names()

    def get_content_url(self):
        """
        Получение URL для контента
        """
        return reverse_lazy(self.request.resolver_match.view_name, kwargs={'type': self.content_type})


class CreateUpdateMixin(TitleMixin, AjaxFormResponseMixin):
    """
    Миксин создания / редактирования
    """

    create_mode = False
    edit_mode = False

    def post(self, request, *args, **kwargs):
        sid = transaction.savepoint()
        form = self.get_form()
        is_valid = self.form_is_valid(form)
        if is_valid:
            self.before_save()
            self.form_save(form)
            self.after_save()
            transaction.savepoint_commit(sid)
            return self.success_response()
        else:
            transaction.savepoint_rollback(sid)
            return self.error_response(form)

    def before_save(self):
        """
        Действие до сохранения формы
        """
        pass

    def after_save(self):
        """
        Действие после сохранения формы
        """
        pass

    def form_is_valid(self, form):
        """
        Валидация формы
        """
        return form.is_valid()

    def form_save(self, form):
        """
        Валидация формы
        """
        self.object = form.save(False)
        self.set_object_additional_values(self.object)
        self.object.save()
        form.save_m2m()

    def form_valid(self, form):
        """
        Действия при валидности формы
        """
        self.before_save()
        self.form_save(form)
        self.after_save()

    def set_object_additional_values(self, obj):
        """
        Дополнительные данные при сохранении объекта
        """
        pass

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                'create_mode': self.create_mode,
                'edit_mode': self.edit_mode,
            }
        )
        return context_data


class CustomCreateView(ActionGroupMixin, CreateUpdateMixin, CreateView):
    """
    Представления создания объекта
    """

    create_mode = True
    action_group_classes = (
        FormActionGroup,
    )

    def get(self, request, *args, **kwargs):
        self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)


class CreateAjaxView(CustomCreateView):
    """
    Представление: Ajax создание объекта
    """

    template_name = 'report_designer/modal_form_body.html'
    form_name = 'create'

    # Зависимый объект, с которым необходимо произвести
    # действие после получения успешного ответа в js
    dependent_key = None
    dependent_name = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({'form_name': self.form_name})
        return context_data

    def additional_ajax_response_kwargs(self, context=None, **kwargs):
        ajax_response_kwargs = super().additional_ajax_response_kwargs(context, **kwargs)
        if kwargs.get('success', False):
            ajax_response_kwargs.update({
                'dependent_key': self.dependent_key,
                'dependent_name': self.dependent_name,
            })
        return ajax_response_kwargs


class BaseListView(ActionGroupMixin, ListView):
    """
    Базовое представление списка объектов
    """

    is_paginate = True
    paginate_choices = (10, 20, 30)
    pagination_count_name = 'pagination_count'

    def get_paginate_by(self, queryset):
        paginate_by = (
            self.request.GET.get(self.pagination_count_name)
            or self.request.session.get(self.pagination_count_name)
            or self.paginate_choices[0]
        )
        self.save_paginate_by(paginate_by)
        return paginate_by

    def save_paginate_by(self, paginate_by):
        """
        Сохранение пагинации в сессию
        """
        self.request.session[self.pagination_count_name] = paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_paginate': self.is_paginate,
            'paginate_choices': self.paginate_choices,
            'pagination_count_name': self.pagination_count_name,
        })
        return context


class DynamicContentBaseListView(DynamicContentMixin, FilterView, BaseListView):
    """
    Представление: Динамическая загрузка списка объектов
    """

    def get_queryset(self):
        # Если указан filterset и тип запроса == self.base_type,
        # возвращается пустой queryset
        queryset = super().get_queryset()
        if self.is_base_type:
            return queryset.none()
        return queryset


class DynamicContentTableBaseView(TitleMixin, DynamicContentBaseListView):
    """
    Представление: Представление списка объектов в виду таблицы
    """

    template_name = 'report_designer/core/dynamic_tables/base.html'
    template_name_content = 'report_designer/core/dynamic_tables/table.html'
    table_class = None
    filters_clear = True

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data.update(
            {
                **self.get_table_context_data(context_data),
                'filters_clear': self.filters_clear,
            }
        )
        return context_data

    def get_table_context_data(self, context):
        """
        Таблица в контексте шаблона
        """
        if self.is_content_type:
            return {'table': self.init_table(context.get('object_list'))}
        return {}

    def init_table(self, queryset, **kwargs):
        """
        Инициализация таблицы
        """
        table_class = self.get_table_class()
        if not table_class:
            return
        table = table_class(queryset=queryset, **self.get_table_kwargs())
        table.create_table()
        return table

    def get_table_class(self):
        """
        Класс таблицы
        """
        return self.table_class

    def get_table_kwargs(self):
        """
        Параметры таблицы
        """
        return {}

    def save_paginate_by(self, paginate_by):
        if self.is_content_type:
            super().save_paginate_by(paginate_by)

