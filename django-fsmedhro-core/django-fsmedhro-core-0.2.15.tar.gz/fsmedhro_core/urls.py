from django.urls import path
from . import views

app_name = 'fsmedhro_core'

urlpatterns = [
    path('edit/', views.FachschaftUserEdit.as_view(), name='edit'),
    path('rundmail/', views.Rundmail.as_view(), name='rundmail'),
    path('', views.FachschaftUserDetail.as_view(), name='detail'),
]
