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

from django.template.defaultfilters import register


@register.filter
def get(dict, key, default=''):
    """
    Usage:

    view:
    some_dict = {'keyA':'valueA','keyB':{'subKeyA':'subValueA','subKeyB':'subKeyB'},'keyC':'valueC'}
    keys = ['keyA','keyC']
    template:
    {{ some_dict|get:"keyA" }}
    {{ some_dict|get:"keyB"|get:"subKeyA" }}
    {% for key in keys %}{{ some_dict|get:key }}{% endfor %}
    """

    try:
        return dict.get(key, default)
    except:
        return default


@register.filter
def get_dict_items(dict, key, default=''):
    """
    Usage:

    view:
    some_dict = {'keyA':'valueA','keyB':{'subKeyA':'subValueA','subKeyB':'subKeyB'},'keyC':'valueC'}
    keys = ['keyA','keyC']
    template:
    {{ some_dict|get:"keyA" }}
    {{ some_dict|get:"keyB"|get:"subKeyA" }}
    {% for key in keys %}{{ some_dict|get:key }}{% endfor %}
    """
    return dict[key].items()


@register.filter
def index(List, i):
    return List[int(i)]
