# Third-Party Imports
# from django.urls import path

from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter
from track_actions.views import HistoryView

router = SimpleRouter()
router.register("history", HistoryView, "history")

urlpatterns = [
    url(r'^', include(router.urls, namespace='history')),
]
