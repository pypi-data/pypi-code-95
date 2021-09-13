from django.urls import path, include
from account.views import register, login


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', register, name='register')
]
