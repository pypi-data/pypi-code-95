from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, render
from django.urls import path, include


def logout_with_ajax_url(request):
    ajax_url = getattr(settings, "AJAX_BEFORE_LOGOUT_URL", '')
    if ajax_url:
        return render(request, "logout_redirect.html", context={"ajax_url": ajax_url})
    else:
        return redirect("original_logout")


urlpatterns = [
    path(
        "original_logout/",
        LogoutView.as_view(next_page="landing" if not settings.LOGOUT_REDIRECT_URL else None),
        name="original_logout",
    ),
    path("logout/", logout_with_ajax_url, name="logout_with_ajax"),
    path("accounts/", include("allauth.urls")),
]
