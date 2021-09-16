from NEMO.urls import router
from django.urls import path

from NEMO_billing.rates import views, api

# Rest API URLs
router.register(r"rates", api.RateViewSet)
router.register(r"rate_types", api.RateTypeViewSet)

urlpatterns = [
    path("rates/", views.rates, name="rates"),
    path("rate/", views.create_or_modify_rate, name="create_rate"),
    path("rate/<str:rate_type_choice>/", views.create_or_modify_rate, name="create_rate"),
    path("rate/<str:rate_type_choice>/<int:rate_id>/", views.create_or_modify_rate, name="edit_rate"),
]
