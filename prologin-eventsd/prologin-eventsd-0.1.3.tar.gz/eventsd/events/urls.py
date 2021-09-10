from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.SimpleRouter()

router.register("events", views.EventViewset, basename="events")
router.register("forms", views.FormViewset, basename="forms")
router.register("attendees", views.AttendeeViewset, basename="attendees")

app_name = "eventsd_events"

urlpatterns = [
    path("", include(router.urls)),
]
