from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('backend/', include('kirui_devserver.backend.urls', namespace='backend')),
    path('brython/', include('django_brython.urls', namespace='brython')),
]
