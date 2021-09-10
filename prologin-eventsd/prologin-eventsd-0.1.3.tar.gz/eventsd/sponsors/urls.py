from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "eventsd_sponsors"

router = routers.SimpleRouter()
router.register("", views.SponsorViewset, basename="sponsors")

urlpatterns = [
    path("", include(router.urls)),
]
