from rest_framework import routers

from appchance_sections.views import SectionViewSet

router = routers.DefaultRouter()
router.register(r"sections", SectionViewSet)

app_name = "appchance_sections"  # pylint: disable=C0103
urlpatterns = router.urls
