#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from collections import OrderedDict
from hashlib import md5
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from textrank.validators import keyword_validator


class Group(models.Model):
    """Модель группы ключевых слов."""
    created = models.DateTimeField(_('создана'), auto_now_add=True)
    updated = models.DateTimeField(_('обновлена'), auto_now=True)
    name = models.CharField(
        _('название'), max_length=150, unique=True,
        help_text=_('Обязательно. 150 символов и менее.'),
        error_messages={
            'unique': _('Такое название уже существует.'),
        },
    )
    description = models.TextField(
        _('описание'), blank=True, db_index=True,
    )
    code = models.CharField(
        _('код группы'), max_length=32, default=get_random_string, unique=True,
        help_text=_('Обязательно. 32 символа и менее, уникальное значение.'),
        error_messages={
            'unique': _('Такой код уже существует.'),
        },
    )
    is_active = models.BooleanField(
        _('активная'), default=True, db_index=True, help_text=_(
            'Отключите, если группа не используется для анализа.'
        )
    )
    # Пользователь, который последним изменил объект.
    last_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        editable=False,
        verbose_name=_('последний редактор'),
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _('группа ключевых слов')
        verbose_name_plural = _('группы ключевых слов')
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        super().save(**kwargs)
        # Обновляем все веса, чтобы анализатор перезагрузил данные.
        Weight.objects.filter(group=self).update(updated=now())

    def delete(self, **kwargs):
        # Удалять объекты в Django запрещено. Только из базы данных.
        self.is_active = False
        self.save(**kwargs)

    def get_all_keywords(self):
        return self.keyword_set.all()

    def get_active_keywords(self):
        return self.get_all_keywords().filter(is_active=True)

    def get_inactive_keywords(self):
        return self.get_all_keywords().filter(is_active=False)

    def get_all_weights(self):
        qs = self.weights.select_related('group', 'keyword')
        qs = qs.order_by('keyword__word')
        return qs

    def get_description(self):
        return self.description.replace('\r\n', ' ').replace('\n', ' ')


class Keyword(models.Model):
    """Модель ключевого слова или словосочетания."""

    created = models.DateTimeField(_('создано'), auto_now_add=True)
    updated = models.DateTimeField(_('обновлено'), auto_now=True)
    word = models.CharField(
        _('слово'), max_length=100, unique=True,
        help_text=_(
            'Обязательно. 100 символов и менее. '
            'Значение может содержать только буквы в нижнем регистре, '
            'цифры, символы дефиса, подчёркивания или знак +, а также '
            'начинаться и заканчиваться словом. Варианты: '
            'Ключевое слово (word1), цепочка слов (word1_word2_word3) '
            'или покрытие словами (word1+word2+word3).'
        ),
        validators=[keyword_validator],
        error_messages={
            'unique': _('Такое слово (сочетание) уже существует.'),
        },
    )
    is_active = models.BooleanField(
        _('активное'), default=True, db_index=True, help_text=_(
            'Отключите, если слово не используется для анализа.'
        )
    )
    # Пользователь, который последним изменил объект.
    last_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        editable=False,
        verbose_name=_('последний редактор'),
        on_delete=models.PROTECT,
    )
    groups = models.ManyToManyField(
        Group, through='Weight',
        editable=False,
        verbose_name=_('группы')
    )

    class Meta:
        verbose_name = _('ключевое слово')
        verbose_name_plural = _('ключевые слова')
        ordering = ('word',)

    def __str__(self):
        return self.word

    @staticmethod
    def validate_word(word, raise_error=False):
        try:
            keyword_validator(word)
        except ValidationError as e:
            if raise_error:
                raise e
            return False
        return True

    @property
    def is_chain(self):
        return '_' in self.word

    @property
    def is_cover(self):
        return '+' in self.word

    @property
    def chainwords(self):
        w = self.word
        if '_' in w:
            words = [x for x in w.split('_') if x]
            if len(words) >= 2:
                return words
        return []

    @property
    def coverwords(self):
        w = self.word
        if '+' in w:
            words = [x for x in w.split('+') if x]
            if len(words) >= 2:
                return words
        return []

    def get_all_groups(self):
        return self.groups.all()

    def get_active_groups(self):
        return self.get_all_groups().filter(is_active=True)

    def get_inactive_groups(self):
        return self.get_all_groups().filter(is_active=False)

    def get_weight_groups(self):
        groups = OrderedDict([(g.id, [g, None]) for g in Group.objects.all()])
        for w in self.weights.select_related('group', 'keyword'):
            groups[w.group_id][1] = w
        return groups

    def save(self, **kwargs):
        self.validate_word(self.word, True)
        super().save(**kwargs)
        # Обновляем все веса, чтобы анализатор перезагрузил данные.
        Weight.objects.filter(keyword=self).update(updated=now())

    def delete(self, **kwargs):
        # Удалять объекты в Django запрещено. Только из базы данных.
        self.is_active = False
        self.save(**kwargs)


class Weight(models.Model):
    """Модель веса ключевого слова для группы."""
    created = models.DateTimeField(_('создан'), auto_now_add=True)
    updated = models.DateTimeField(_('обновлён'), auto_now=True, db_index=True)
    group = models.ForeignKey(
        Group,
        verbose_name=_('группа'),
        on_delete=models.PROTECT,
        related_name='weights',
    )
    keyword = models.ForeignKey(
        Keyword,
        verbose_name=_('ключевое слово'),
        on_delete=models.PROTECT,
        related_name='weights',
    )
    value = models.PositiveSmallIntegerField(_('значение веса'), default=1)
    # Пользователь, который последним изменил объект.
    last_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        editable=False,
        verbose_name=_('последний редактор'),
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _('вес ключевого слова')
        verbose_name_plural = _('веса ключевых слов')
        unique_together = ('group', 'keyword')
        ordering = ('-updated',)

    def __str__(self):
        return '%s = %s' % (self.keyword, self.value)

    @property
    def is_active(self):
        return self.value and self.group.is_active and self.keyword.is_active


class Sample(models.Model):
    """
    Модель образца текста для однозначного сопоставления с группой.
    Образцы собираются для обучения моделей искусственного интеллекта.
    """
    created = models.DateTimeField(_('создан'), auto_now_add=True)
    updated = models.DateTimeField(_('обновлён'), auto_now=True, db_index=True)
    checksum = models.CharField(
        _('контрольная сумма'), max_length=32, blank=True, editable=False)
    group = models.ForeignKey(
        Group,
        verbose_name=_('группа'),
        on_delete=models.PROTECT,
        related_name='samples',
    )
    message = models.TextField(_('текст сообщения'))
    # Пользователь, который последним изменил объект.
    last_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        editable=False,
        verbose_name=_('последний редактор'),
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _('образец')
        verbose_name_plural = _('образцы')
        unique_together = ('group', 'checksum')
        ordering = ('-updated',)

    def __str__(self):
        return self.message

    @staticmethod
    def get_checksum(message):
        return md5(message.encode('utf-8')).hexdigest()

    def save(self, **kwargs):
        self.checksum = self.get_checksum(self.message)
        super().save(**kwargs)
