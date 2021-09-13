from django.urls import path, include
from .view import register
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from register.admin import UserAdmin

register_logout_url = [
    # path('administrator/',include(UserAdmin)),
    path('', register.hello, name='home'),
    path('register/', register.RegisterView.as_view()),
    path('logout/', register.LogoutView.as_view()),
    path('validate_activation_code/', register.CheckActivationCodeView.as_view()),
]

urlpatterns = [
    path('', include(register_logout_url)),
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
]
