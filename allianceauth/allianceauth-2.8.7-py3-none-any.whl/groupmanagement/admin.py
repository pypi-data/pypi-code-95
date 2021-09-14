from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib import admin
from django.contrib.auth.models import Group as BaseGroup, User
from django.db.models import Count
from django.db.models.functions import Lower
from django.db.models.signals import pre_save, post_save, pre_delete, \
    post_delete, m2m_changed
from django.dispatch import receiver

from .models import AuthGroup
from .models import GroupRequest

if 'eve_autogroups' in apps.app_configs:    
    _has_auto_groups = True    
else:
    _has_auto_groups = False


class AuthGroupInlineAdmin(admin.StackedInline):
    model = AuthGroup
    filter_horizontal = ('group_leaders', 'group_leader_groups', 'states',)
    fields = (
        'description', 
        'group_leaders', 
        'group_leader_groups', 
        'states', 'internal', 
        'hidden', 
        'open', 
        'public'
    )
    verbose_name_plural = 'Auth Settings'
    verbose_name = ''

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """overriding this formfield to have sorted lists in the form"""
        if db_field.name == "group_leaders":
            kwargs["queryset"] = User.objects.order_by(Lower('username'))
        elif db_field.name == "group_leader_groups":
            kwargs["queryset"] = Group.objects.order_by(Lower('name'))
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('auth.change_group')


if _has_auto_groups:
    class IsAutoGroupFilter(admin.SimpleListFilter):
        title = 'auto group'
        parameter_name = 'is_auto_group__exact'

        def lookups(self, request, model_admin):
            return (
                ('yes', 'Yes'),
                ('no', 'No'),
            )

        def queryset(self, request, queryset):
            value = self.value()
            if value == 'yes':
                return queryset.exclude(
                    managedalliancegroup__isnull=True, 
                    managedcorpgroup__isnull=True
                )
            elif value == 'no':
                return queryset.filter(
                    managedalliancegroup__isnull=True, 
                    managedcorpgroup__isnull=True
                )
            else:
                return queryset


class HasLeaderFilter(admin.SimpleListFilter):
    title = 'has leader'
    parameter_name = 'has_leader__exact'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.filter(authgroup__group_leaders__isnull=False)
        elif value == 'no':
            return queryset.filter(authgroup__group_leaders__isnull=True)
        else:
            return queryset


class GroupAdmin(admin.ModelAdmin):        
    ordering = ('name',)
    list_display = (
        'name', 
        '_description', 
        '_properties', 
        '_member_count', 
        'has_leader'
    )
    list_filter = [
        'authgroup__internal', 
        'authgroup__hidden', 
        'authgroup__open', 
        'authgroup__public',        
    ]
    if _has_auto_groups:
        list_filter.append(IsAutoGroupFilter)
    list_filter.append(HasLeaderFilter)

    search_fields = ('name', 'authgroup__description')
        
    def get_queryset(self, request):
        qs = super().get_queryset(request)                
        if _has_auto_groups:
            qs = qs.prefetch_related('managedalliancegroup_set', 'managedcorpgroup_set')
        qs = qs.prefetch_related('authgroup__group_leaders').select_related('authgroup')
        qs = qs.annotate(
            member_count=Count('user', distinct=True),
        )        
        return qs

    def _description(self, obj):
        return obj.authgroup.description

    def _member_count(self, obj):
        return obj.member_count

    _member_count.short_description = 'Members'
    _member_count.admin_order_field = 'member_count'
    
    def has_leader(self, obj):
        return obj.authgroup.group_leaders.exists() or obj.authgroup.group_leader_groups.exists()
    
    has_leader.boolean = True    

    def _properties(self, obj):
        properties = list()       
        if _has_auto_groups and (
            obj.managedalliancegroup_set.exists() 
            or obj.managedcorpgroup_set.exists()
        ):
            properties.append('Auto Group')
        elif obj.authgroup.internal:
            properties.append('Internal')
        else:
            if obj.authgroup.hidden:
                properties.append('Hidden')
            if obj.authgroup.open:
                properties.append('Open')
            if obj.authgroup.public:
                properties.append('Public')
        if not properties:
            properties.append('Default')
                    
        return properties

    _properties.short_description = "properties"

    filter_horizontal = ('permissions',)
    inlines = (AuthGroupInlineAdmin,)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "permissions":
            kwargs["queryset"] = Permission.objects.select_related("content_type").all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_formset(self, request, form, formset, change):
        for inline_form in formset:
            ag_instance = inline_form.save(commit=False)
            ag_instance.group = form.instance
            ag_instance.save()
        formset.save()


class Group(BaseGroup):
    class Meta:
        proxy = True
        verbose_name = BaseGroup._meta.verbose_name
        verbose_name_plural = BaseGroup._meta.verbose_name_plural


try:
    admin.site.unregister(BaseGroup)
finally:
    admin.site.register(Group, GroupAdmin)


@admin.register(GroupRequest)
class GroupRequestAdmin(admin.ModelAdmin):        
    search_fields = ('user__username', )
    list_display = ('id', 'group', 'user', '_leave_request', 'status')
    list_filter = (
        ('group', admin.RelatedOnlyFieldListFilter),
        ('user', admin.RelatedOnlyFieldListFilter),
        'leave_request', 
        'status'
    )

    def _leave_request(self, obj) -> True:
        return obj.leave_request
    
    _leave_request.short_description = 'is leave request'
    _leave_request.boolean = True


@receiver(pre_save, sender=Group)
def redirect_pre_save(sender, signal=None, *args, **kwargs):
    pre_save.send(BaseGroup, *args, **kwargs)


@receiver(post_save, sender=Group)
def redirect_post_save(sender, signal=None, *args, **kwargs):
    post_save.send(BaseGroup, *args, **kwargs)


@receiver(pre_delete, sender=Group)
def redirect_pre_delete(sender, signal=None, *args, **kwargs):
    pre_delete.send(BaseGroup, *args, **kwargs)


@receiver(post_delete, sender=Group)
def redirect_post_delete(sender, signal=None, *args, **kwargs):
    post_delete.send(BaseGroup, *args, **kwargs)


@receiver(m2m_changed, sender=Group.permissions.through)
def redirect_m2m_changed_permissions(sender, signal=None, *args, **kwargs):
    m2m_changed.send(BaseGroup, *args, **kwargs)
