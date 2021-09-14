# coding=utf-8

#  Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import arrow
from django.contrib import admin, messages
from django.contrib.admin import StackedInline
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.forms import BaseInlineFormSet
from django.utils.translation import gettext as _
from import_export import resources
from import_export.admin import ExportActionMixin
from import_export.fields import Field
from nobinobi_core.functions import AdminInlineWithSelectRelated
from rangefilter.filter import DateRangeFilter

from nobinobi_staff.forms import AbsenceAdminForm, RightTrainingAdminForm
from .models import Absence, Qualification, Team, Staff, AbsenceType, AbsenceAttachment, Training, RightTraining


class InlineAbsenceFormset(BaseInlineFormSet):
    def clean(self):
        super(InlineAbsenceFormset, self).clean()
        errors = []
        for form in self.forms:
            try:
                form.cleaned_data['start_date']
            except KeyError:
                form.cleaned_data["start_date"] = arrow.now().datetime
            else:
                if form.cleaned_data["start_date"] > form.cleaned_data["end_date"]:
                    msg = _("The start date is greater than the end date.")
                    errors.append(msg)
                    form._errors[NON_FIELD_ERRORS] = self.error_class([msg])

        if errors:
            raise ValidationError(errors)


class AbsenceInline(AdminInlineWithSelectRelated, StackedInline):
    model = Absence
    extra = 0
    verbose_name_plural = 'Absences'
    suit_classes = 'suit-tab suit-tab-absences'
    # raw_id_fields = ("abs_type",)
    suit_form_inlines_hide_original = True
    list_select_related = [
        "abs_type",
        "staff",
    ]
    formset = InlineAbsenceFormset  # line to add
    form = AbsenceAdminForm


class AbsenceAttachmentInline(StackedInline):
    model = AbsenceAttachment
    extra = 0
    verbose_name_plural = 'AbsencesAttachment'
    suit_classes = 'suit-tab suit-tab-file'


class AbsenceResource(resources.ModelResource):
    staff = Field(column_name='staff')
    # abs_type = Field(column_name='abs_type')
    all_day = Field(column_name='all_day')
    partial_disability = Field(column_name='partial_disability')

    class Meta:
        model = Absence
        fields = (
            'staff', 'abs_type__reason', 'start_date', 'end_date', 'comment', 'all_day', 'partial_disability'
        )
        export_order = (
            'staff', 'abs_type__reason', 'start_date', 'end_date', 'comment', 'all_day', 'partial_disability'
        )
        widgets = {
            'start_date': {'format': "%d/%m/%Y %H:%M"},
            'end_date': {'format': "%d/%m/%Y %H:%M"},
        }

    def dehydrate_staff(self, absence):
        return '%s' % absence.staff.full_name

    def dehydrate_all_day(self, absence):
        return _("Yes") if absence.all_day else _("No")

    def dehydrate_partial_disability(self, absence):
        return _("Yes") if absence.partial_disability else _("No")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    # on garde les filtres actif en enregistrant
    preserve_filters = True

    suit_form_tabs = (('info', _('Staff informations')), ('absences', _('Absences')),)
    list_display = (
        'last_name', 'first_name', 'qualification', 'percentage_work', 'working_time', 'status'
    )
    list_filter = ('status', 'gender', 'civil_status', "team", "qualification", "arrival_date", "departure_date")
    ordering = ('last_name',)
    inlines = (AbsenceInline,)
    search_fields = ('last_name', 'first_name', "birth_date", "social_security_number", "email",)
    readonly_fields = ('working_time',)
    fieldsets = [
        (_('Staff informations'),
         {
             'classes': ('suit-tab', 'suit-tab-info',),
             'fields': [
                 'first_name', 'last_name', 'gender', 'birth_date', 'picture', 'nationality', 'civil_status',
                 'street', 'zip', 'city',
                 'phone', 'mobile_phone', 'email', 'social_security_number',
                 'status',
                 'team', 'user'
             ]
         }),
        (_('Qualification'),
         {
             'classes': ('suit-tab', 'suit-tab-info',),
             'fields': ['qualification', ]
         }),
        (_('Date'), {
            'classes': ('suit-tab', 'suit-tab-info',),
            'fields': ['arrival_date', 'departure_date']
        }),
        (_('Planning'), {
            'classes': ('suit-tab', 'suit-tab-info',),
            'description': _("Occupancy rate (based on a 40-hour weekly schedule)"),
            'fields': ['percentage_work', 'working_time']
        }), ]

    actions = ['archive_staff']

    def archive_staff(self, request, queryset):
        rows_updated = 0
        for q in queryset:
            # pour chaque selection
            if q.status == Staff.STATUS.active:
                # Si il est actif, on l'archive
                q.status = Staff.STATUS.archived
            # on sauve
            q.save()
            rows_updated += 1

        if rows_updated == 1:
            message_bit = _("1 person has been archived")
        else:
            message_bit = _("{0} persons have been archived.").format(rows_updated)
        messages.success(request, "%s" % message_bit)

    archive_staff.short_description = _("Archive a person(s)")

    def get_formsets(self, request, obj=None):
        """
        Set extra=0 for inlines if object already exists
        """
        for inline in self.get_inline_instances(request):
            formset = inline.get_formset(request, obj)
            if obj:
                formset.extra = 0
            yield formset


@admin.register(Absence)
class AbsenceAdmin(ExportActionMixin, admin.ModelAdmin):
    form = AbsenceAdminForm
    inlines = (AbsenceAttachmentInline,)
    resource_class = AbsenceResource
    list_filter = ('abs_type', ('start_date', DateRangeFilter), ('end_date', DateRangeFilter))
    list_display = ('staff', 'abs_type', 'start_date', 'end_date')
    ordering = ('-start_date',)
    search_fields = ('staff__last_name', 'staff__first_name')
    save_as = True
    fieldsets = [
        (_('Information'),
         {
             'fields': ['staff', 'abs_type'],
         }),
        (_('Date'),
         {
             'fields': ['start_date', 'end_date', 'all_day', 'partial_disability'],
         }),
        (_('Comment'),
         {
             'fields': ['comment'],
         }),
    ]


@admin.register(AbsenceType)
class AbsenceTypeAdmin(admin.ModelAdmin):
    list_filter = ('reason', 'abbr',)
    ordering = ('reason',)
    search_fields = ('reason', 'abbr',)


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_filter = ('name', 'short_name', 'order',)
    list_display = ('name', 'short_name', 'order',)
    ordering = ('order', 'name',)
    search_fields = ('name', 'short_name',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    list_filter = ('name', 'order')
    readonly_fields = ("slug",)
    ordering = ('order', 'name',)
    search_fields = ('name',)


@admin.register(RightTraining)
class RightTrainingAdmin(admin.ModelAdmin):
    readonly_fields = ("start_month", "start_day")
    form = RightTrainingAdminForm


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    readonly_fields = ("default_number_days", "start_date", "end_date", "staff")
    fields = ("default_number_days", "number_days", "start_date", "end_date", "staff")
    list_display = ("staff", "start_date", "end_date", "default_number_days", "number_days")
