from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from course.models import AllCourse
from django.conf import settings
from django_countries.fields import CountryField


class Admin(models.Model):
    course = models.ForeignKey(AllCourse, models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    profession = models.ForeignKey("UserProfession", on_delete=models.CASCADE, null=True, blank=True)
    speciality = models.ForeignKey("UserSpeciality", on_delete=models.CASCADE, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to='media', default='default.jpg', null=True, blank=True)
    country = CountryField(null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class RegisterCheck(models.Model):
    email = models.EmailField(unique=True)
    time = models.TimeField(default=None, blank=True, null=True)
    code = models.IntegerField()
    count = models.IntegerField(default=0)


class UserProfession(models.Model):
    title = models.CharField(max_length=245, verbose_name="Profession name")

    class Meta:
        verbose_name = "User Profession"

    def __str__(self):
        return self.title


class UserSpeciality(models.Model):
    title = models.CharField(max_length=245, verbose_name="Speciality name:")

    def __str__(self):
        return self.title


# class UserContact(CustomUser):
    #