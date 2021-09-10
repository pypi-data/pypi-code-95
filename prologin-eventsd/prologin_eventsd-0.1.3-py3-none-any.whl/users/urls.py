from django.urls import path
from . import views

app_name = "eventsd_users"

urlpatterns = [
    path("me/", views.UserMeView.as_view(), name="me"),
]
