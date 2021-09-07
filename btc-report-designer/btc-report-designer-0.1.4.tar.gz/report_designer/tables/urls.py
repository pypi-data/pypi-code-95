from django.urls import path, include

from . import views


app_name = 'tables'


ajax_urls = [
    path('table/<str:type>/', views.DBTableListView.as_view(), name='list'),
    path('create/', views.DBTableCreateView.as_view(), name='create'),
]


urlpatterns = [
    path('', views.DBTableListView.as_view(), name='list', kwargs={'type': 'base'}),
    path('ajax/', include(ajax_urls)),
]
