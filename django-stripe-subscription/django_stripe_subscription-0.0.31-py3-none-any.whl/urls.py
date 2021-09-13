from django.urls import path

from . import views


app_name = 'stripe-subscription'

urlpatterns = [
    path('session/', views.session),
    path('subscribe/', views.subscribe),
    path('check/', views.check_subscription),
    path('cancel/', views.cancel_subscription),
    path('cancel/<str:token>/confirm/', views.cancel_subscription_confirm, name='cancel-confirm'),
]
