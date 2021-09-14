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

# -*- coding: utf-8 -*-
import datetime

from django import template

register = template.Library()


@register.filter
def subtract(value, arg):
    return value - arg


@register.simple_tag(takes_context=True)
def subtractify(context, obj, obj2):
    newval = obj - obj2
    return "%.1f" % newval


@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    # you would need to do any localization of the result here
    return qty * unit_price


@register.simple_tag()
def get_pourcentage(value, pourcentage, ref, *args, **kwargs):
    # 4 × 100 ÷ 8 = 50 =====0
    if type(value) == datetime.timedelta:
        value = value.total_seconds()
    if type(ref) == datetime.timedelta:
        ref = ref.total_seconds()

    try:
        return float(value) * int(pourcentage) / float(ref)
    except ZeroDivisionError:
        return 0
