from django.urls import path, include
from django.views.generic.base import TemplateView
from .views import (
    UserKeyListView,
    UserKeyDeleteView,
    MFAAdminLoginView,
    MFAAdminSecondFactorView,
)


urlpatterns = [
    path("login/", MFAAdminLoginView.as_view()),
    path("login/mfa/", MFAAdminSecondFactorView.as_view(), name="login-mfa"),
    path("multi_factor_auth/", UserKeyListView.as_view(), name="user-key-list"),
    path(
        "multi_factor_auth/<pk>/delete/",
        UserKeyDeleteView.as_view(),
        name="user-key-delete",
    ),
    path(
        "multi_factor_auth/fido2/",
        TemplateView.as_view(template_name="django_rest_mfa/fido2_add.html"),
        name="fido2-add",
    ),
    path(
        "multi_factor_auth/otp/",
        TemplateView.as_view(template_name="django_rest_mfa/otp_add.html"),
        name="otp-add",
    ),
]
