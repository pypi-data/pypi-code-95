#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class UnicodeKeywordValidator(validators.RegexValidator):
    regex = r'^[\w\-\+]+$'
    message = _(
        'Введите корректное ключевое слово, цепочку слов (word1_word2_word3) '
        'или покрытие словами (word1+word2+word3). Цепочка не должна '
        'сочетается с покрытием. '
        'Значение может содержать только буквы в нижнем регистре, цифры, '
        'символы дефиса, подчёркивания или знак +, а также начинаться и '
        'заканчиваться словом.'
    )
    flags = 0

    def __call__(self, value):
        super().__call__(value)
        if (value != value.lower() or
                value.startswith('_') or value.startswith('+') or
                value.endswith('_') or value.endswith('+') or
                ('+' in value and '_' in value)):
            raise ValidationError(self.message, code=self.code)


keyword_validator = UnicodeKeywordValidator()
