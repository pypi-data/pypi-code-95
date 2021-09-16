"""
URLs for notices.
"""
from django.conf.urls import include
from django.urls import path

from notices.views import RenderNotice


urlpatterns = [
    path("api/", include(("notices.rest_api.urls", "rest_api"), namespace="rest_api")),
    path("render/<int:pk>/", RenderNotice.as_view(), name="notice-detail"),
]
