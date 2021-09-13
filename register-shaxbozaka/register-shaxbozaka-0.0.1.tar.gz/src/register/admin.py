from register.models import CustomUser, UserProfession
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from admin_interface.models import Theme
from django.contrib.auth.admin import GroupAdmin


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    notificationToUser = forms.BooleanField(help_text="Do you want to send an email to the user after registration?", label='send notification')

    class Meta:
        model = CustomUser
        fields = "__all__"

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if self.cleaned_data['notificationToUser']:
            send_mail("Registration", f"you have been registered"
                                      f" by admins from {Theme.objects.get(active=True).title}\n"
                                      f"your email: {self.cleaned_data['email']}\n"
                                      f"your password: {self.cleaned_data['password1']}",
                      recipient_list=[self.cleaned_data['email']], from_email="-no-reply@mail.ru")

        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"),
                                         help_text=_("Raw passwords are not stored, so there is no way to see "
                                                     "this user's password, but you can change the password "
                                                     "using <a href=\"../password/\">this form</a>.")
                                         )

    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'profession')
    list_filter = ('groups', 'profession')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Contact information', {'fields': ('image', 'first_name', 'last_name',"mobile_number", 'profession', 'speciality', 'country')}),
        ('Permissions', {'fields': ('is_staff', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'groups', 'password1', 'password2', 'notificationToUser'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(get_user_model(), UserAdmin)
admin.site.register(UserProfession)
admin.site.site_header = "Testquizz"

