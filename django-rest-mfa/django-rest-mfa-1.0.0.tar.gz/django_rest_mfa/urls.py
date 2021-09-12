from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserKeyViewSet, FIDO2Authenticate, TOTPAuthenticate, BackupCodesAuthenticate

router = DefaultRouter()
router.register(r"user_keys", UserKeyViewSet, basename="user-keys")

urlpatterns = [
    path("authenticate/fido2/", FIDO2Authenticate.as_view(), name="authenticate-fido2"),
    path("authenticate/totp/", TOTPAuthenticate.as_view(), name="authenticate-totp"),
    path("authenticate/backup_codes/", BackupCodesAuthenticate.as_view(), name="authenticate-backup-codes"),
    path("", include(router.urls)),
]
