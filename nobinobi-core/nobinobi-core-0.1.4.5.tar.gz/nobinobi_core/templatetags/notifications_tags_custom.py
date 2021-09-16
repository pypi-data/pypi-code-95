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
import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder

try:
    from django.urls import reverse
except:
    from django.core.urlresolvers import reverse
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.simple_tag(takes_context=True)
def notifications_unread(context):
    user = user_context(context)
    if not user:
        return ''
    return user.notifications.unread().count()


# Requires vanilla-js framework - http://vanilla-js.com/
@register.simple_tag
def register_notify_callbacks(badge_id='live_notify_badge',
                              menu_id='live_notify_list',
                              refresh_period=15,
                              callbacks='',
                              fetch=5):
    refresh_period = int(refresh_period) * 1000

    definitions = """
        notify_badge_id='{badge_id}';
        notify_menu_id='{menu_id}';
        notify_api_url='{api_url}';
        notify_fetch_count='{fetch_count}';
        notify_refresh_period={refresh};
    """.format(
        badge_id=badge_id,
        menu_id=menu_id,
        refresh=refresh_period,
        api_url="suivijournalier/notification/medicaments/",
        fetch_count=fetch
    )

    script = "<script>" + definitions
    for callback in callbacks.split(','):
        script += "register_notifier(" + callback + ");"
    script += "</script>"
    return mark_safe(script)


@register.simple_tag(takes_context=True)
def live_notify_badge(context, badge_id='live_notify_badge', classes=""):
    user = user_context(context)
    if not user:
        return ''

    html = "<span id='{badge_id}' class='{classes}'>{unread}</span>".format(
        badge_id=badge_id, classes=classes, unread=user.notifications.unread().count()
    )
    return mark_safe(html)


@register.simple_tag
def live_notify_list(list_id='live_notify_list', classes=""):
    html = "<ul id='{list_id}' class='{classes}'></ul>".format(list_id=list_id, classes=classes)
    return mark_safe(html)


def user_context(context):
    if 'user' not in context:
        return None

    request = context['request']
    user = request.user
    if user.is_anonymous:
        return None
    return user


@register.simple_tag(takes_context=True)
def isAllowedClassroom(context):
    user = user_context(context)
    try:
        classroom_valid = user.classroom_set.all().values_list("id")
    except ObjectDoesNotExist:
        return False
    return json.dumps(list(classroom_valid), cls=DjangoJSONEncoder)
