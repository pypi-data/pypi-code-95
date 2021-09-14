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
#

# -*- coding: utf-8 -*-
import arrow
from django import forms
from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.db.models.constants import LOOKUP_SEP
from django.http import Http404
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from dateutil.rrule import *


# from config.settings.base import PERIODE_SIESTE, PERIODE_TYPE


def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


class DateDigitConverter:
    regex = '\d{4}-\d{2}-\d{2}'

    def to_python(self, value):
        value = str(value).split("-")
        return '{0}-{1}-{2}'.format(value[0], value[1], value[2])

    def to_url(self, value):
        value = str(value).split("-")
        return '{0}-{1}-{2}'.format(value[0], value[1], value[2])


class FourDigitConverter:
    regex = '[0-9]{4}'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return '%04d' % int(value)


class TwoDigitConverter:
    regex = '[0-9]{2}'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return '%02d' % int(value)


def datepaques(an):
    """Calcule la date de Pâques d'une année donnée an (=nombre entier)"""
    a = an // 100
    b = an % 100
    c = (3 * (a + 25)) // 4
    d = (3 * (a + 25)) % 4
    e = (8 * (a + 11)) // 25
    f = (5 * a + b) % 19
    g = (19 * f + c - e) % 30
    h = (f + 11 * g) // 319
    j = (60 * (5 - d) + b) // 4
    k = (60 * (5 - d) + b) % 4
    m = (2 * j - k - g + h) % 7
    n = (g - h + m + 114) // 31
    p = (g - h + m + 114) % 31
    jour = p + 1
    mois = n
    return [jour, mois, an]


def datejeunegenevois(an):
    """Calcule la date de datejeunegenevois d'une année donnée an (=nombre entier)"""
    mois = "09"
    jour = "01"
    date = arrow.get("%s-%s-%s" % (an, mois, jour))
    date = date.replace(day=(-date.weekday() + 10))
    return [date.day, date.month, date.year]


def dateliste(c, sep='/'):
    """Transforme une date chaîne 'j/m/a' en une date liste [j,m,a]"""
    j, m, a = c.split(sep)
    return [int(j), int(m), int(a)]


def datechaine(d, sep='/'):
    """Transforme une date liste=[j,m,a] en une date chaîne 'jj/mm/aaaa'"""
    return ("%02d" + sep + "%02d" + sep + "%0004d") % (d[0], d[1], d[2])


def jourplus(d, n=1):
    """Donne la date du nième jour suivant d=[j, m, a] (n>=0)"""
    j, m, a = d
    fm = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (a % 4 == 0 and a % 100 != 0) or a % 400 == 0:  # bissextile?
        fm[2] = 29
    for i in range(0, n):
        j += 1
        if j > fm[m]:
            j = 1
            m += 1
            if m > 12:
                m = 1
                a += 1
    return [j, m, a]


def jourmoins(d, n=-1):
    """Donne la date du nième jour précédent d=[j, m, a] (n<=0)"""
    j, m, a = d
    fm = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (a % 4 == 0 and a % 100 != 0) or a % 400 == 0:  # bissextile?
        fm[2] = 29
    for i in range(0, abs(n)):
        j -= 1
        if j < 1:
            m -= 1
            if m < 1:
                m = 12
                a -= 1
            j = fm[m]
    return [j, m, a]


def numjoursem(d):
    """Donne le numéro du jour de la semaine d'une date d=[j,m,a]
       lundi=1, mardi=2, ..., dimanche=7
       Algorithme de Maurice Kraitchik (1882–1957)"""
    j, m, a = d
    if m < 3:
        m += 12
        a -= 1
    n = (j + 2 * m + (3 * (m + 1)) // 5 + a + a // 4 - a // 100 + a // 400 + 2) % 7
    return [6, 7, 1, 2, 3, 4, 5][n]


def joursem(d):
    """Donne le jour de semaine en texte à partir de son numéro
       lundi=1, mardi=2, ..., dimanche=7"""
    return ["", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"][numjoursem(d)]


def joursferiesliste(an, sd=0):
    """Liste des jours fériés France en date-liste de l'année an (nb entier).
         sd=0 (=defaut): tous les jours fériés.
         sd=1: idem sans les sammedis-dimanches.
         sd=2: tous + les 2 jours fériés supplémentaires d'Alsace-Moselle.
         sd=3: idem sd=2 sans les samedis-dimanches"""
    F = []  # =liste des dates des jours feries en date-liste d=[j,m,a]
    L = []  # =liste des libelles du jour ferie
    dp = datepaques(an)
    djg = datejeunegenevois(an)

    # Jour de l'an
    d = [1, 1, an]
    nj = numjoursem(d)
    if (sd == 0) or (sd == 1 and nj < 6) or (sd == 2) or (sd == 3 and nj < 6):
        F.append(d)
        L.append(u"Jour de l'an")

    # Vendredi saint (pour l'Alsace-Moselle)
    d = jourmoins(dp, -2)
    if sd >= 2:
        F.append(d)
        L.append(u"Vendredi saint")

    # Lundi de Paques
    d = jourplus(dp, +1)
    F.append(d)
    L.append(u"Lundi de Pâques")

    # Jeudi de l'Ascension
    d = jourplus(dp, +39)
    F.append(d)
    L.append(u"Jeudi de l'Ascension")

    # Lundi de Pentecote
    d = jourplus(dp, +50)
    F.append(d)
    L.append(u"Lundi de Pentecôte")

    # Fete Nationale
    d = [1, 8, an]
    nj = numjoursem(d)
    if (sd == 0) or (sd == 1 and nj < 6) or (sd == 2) or (sd == 3 and nj < 6):
        F.append(d)
        L.append(u"Fête Nationale")

    # jeune genevois
    d = datejeunegenevois(an)
    nj = numjoursem(d)
    if (sd == 0) or (sd == 1 and nj < 6) or (sd == 2) or (sd == 3 and nj < 6):
        F.append(d)
        L.append(u"Jeune genevois")

    # Jour de Noel
    d = [25, 12, an]
    nj = numjoursem(d)
    if (sd == 0) or (sd == 1 and nj < 6) or (sd == 2) or (sd == 3 and nj < 6):
        F.append(d)
        L.append(u"Jour de Noël")

    # Restauration de la république
    d = [31, 12, an]
    nj = numjoursem(d)
    if (sd == 2) or (sd == 3 and nj < 6):
        F.append(d)
        L.append(u"Restauration de la république")

    return F, L


def holidays(an, sd=0, sep='/'):
    """Liste des jours fériés France en date-chaine de l'année an (nb entier).
         sd=0 (=defaut): tous les jours fériés.
         sd=1: idem sans les sammedis-dimanches.
         sd=2: tous + les 2 jours fériés supplémentaires d'Alsace-Moselle.
         sd=3: idem sd=2 sans les samedis-dimanches"""
    C = []
    J = []
    F, L = joursferiesliste(an, sd)
    for i in range(0, len(F)):
        C.append(datechaine(F[i]))  # conversion des dates-liste en dates-chaine
        J.append(joursem(F[i]))  # ajout du jour de semaine
    return C, J, L


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class FormListView(ListView, FormMixin):
    def get(self, request, *args, **kwargs):
        # From ProcessFormMixin
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        # From BaseListView
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})

        context = self.get_context_data(object_list=self.object_list, form=self.form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


# def get_periode_type():
#     """
#     méthode pour retourner le type de période
#     :return: 0,1,2
#     :rtype: int
#     """
#     if PERIODE_TYPE == "one" or PERIODE_TYPE == 1:
#         return 1
#     elif PERIODE_TYPE == "two" or PERIODE_TYPE == 2:
#         return 2
#     else:
#         return 0
#
#
# def get_periode_sieste():
#     """
#     méthode pour retourner si la sieste dans le matin est activer
#     :return: False, True
#     :rtype: bool
#     """
#     if PERIODE_SIESTE:
#         return True
#     else:
#         return False


class CustomArrow(arrow.Arrow):
    def days_end_august(self):
        date = arrow.Arrow(self.year, 8, 31)

        if self > date:
            date = date.shift(years=1)
        return date


def fields_required(self, fields):
    """Used for conditionally marking fields as required."""
    for field in fields:
        if not self.cleaned_data.get(field, ''):
            msg = forms.ValidationError(_("This field is required."))
            self.add_error(field, msg)


def get_semaine(day):
    """
    permet de recuperer la semaine
    :param day:
    :return [arrow.arrow]:
    """
    semaine = []
    day = day.to('Europe/Paris').date()

    dateqs = arrow.Arrow.fromdate(day)
    joursemaine = dateqs.weekday()
    start = dateqs.shift(days=-joursemaine)
    end = dateqs.shift(days=+(4 - joursemaine))

    for jour_semaine in arrow.Arrow.range('day', start, end):
        semaine.append(jour_semaine)
    return semaine


class AdminBaseWithSelectRelated(BaseModelAdmin):
    """
    Admin Base using list_select_related for get_queryset related fields
    """
    list_select_related = []

    def get_queryset(self, request):
        return super(AdminBaseWithSelectRelated, self).get_queryset(request).select_related(*self.list_select_related)

    def form_apply_select_related(self, form):
        for related_field in self.list_select_related:
            splitted = related_field.split(LOOKUP_SEP)

            if len(splitted) > 1:
                field = splitted[0]
                related = LOOKUP_SEP.join(splitted[1:])
                form.base_fields[field].queryset = form.base_fields[field].queryset.select_related(related)


class AdminInlineWithSelectRelated(admin.TabularInline, AdminBaseWithSelectRelated):
    """
    Admin Inline using list_select_related for get_queryset and get_formset related fields
    """

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(AdminInlineWithSelectRelated, self).get_formset(request, obj, **kwargs)

        self.form_apply_select_related(formset.form)

        return formset


class AdminWithSelectRelated(admin.ModelAdmin, AdminBaseWithSelectRelated):
    """
    Admin using list_select_related for get_queryset and get_form related fields
    """

    def get_form(self, request, obj=None, **kwargs):
        form = super(AdminWithSelectRelated, self).get_form(request, obj, **kwargs)

        self.form_apply_select_related(form)

        return form


class FilterWithSelectRelated(admin.RelatedFieldListFilter):
    list_select_related = []

    def field_choices(self, field, request, model_admin):
        return [
            (getattr(x, field.remote_field.get_related_field().attname), str(x))
            for x in self.get_queryset(field)
        ]

    def get_queryset(self, field):
        return field.remote_field.model._default_manager.select_related(*self.list_select_related)


def weeks_between(start_date, end_date):
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()


def week_span_from_date(day):
    first_last_day_week = arrow.get(day).span('week')
    # Business days list
    week_dates = [r for r in rrule(DAILY, byweekday=(MO, TU, WE, TH, FR),
                                   dtstart=first_last_day_week[0],
                                   until=first_last_day_week[-1])]
    return week_dates
