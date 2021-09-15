from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from djrest_wrapper.interfaces import BaseModel
from django.conf import settings
from ..managers import UserManager


class AbstractUser(AbstractBaseUser, BaseModel):
    username_validator = UnicodeUsernameValidator()
    last_login = None
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        verbose_name='Email Address', max_length=254, unique=True)
    is_active = models.BooleanField(
        default=settings.SHA_ACCOUNTS.get('DEFAULT_ACTIVATION', True))
    is_superuser = models.BooleanField(_('superuser status'), default=False)

    USERNAME_FIELD = 'username'
    # email and password are required by default
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class User(AbstractUser):
    permissions = models.ManyToManyField('sha_accounts.Permission')
