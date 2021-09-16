"""v1 API URLS"""
from django.conf.urls import url

from notices.rest_api.v1 import views


urlpatterns = [
    url(r"unacknowledged", views.ListUnacknowledgedNotices.as_view(), name="unacknowledged_notices"),
    url(r"acknowledge", views.AcknowledgeNotice.as_view(), name="acknowledge_notice"),
]
