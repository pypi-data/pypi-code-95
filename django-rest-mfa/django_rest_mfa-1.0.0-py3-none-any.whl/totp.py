from django.conf import settings
import pyotp
from .models import UserKey


def generate_totp_key(user):
    secret_key = pyotp.random_base32()
    totp = pyotp.TOTP(secret_key)
    uri = totp.provisioning_uri(
        user.get_username(), issuer_name=settings.MFA_SERVER_NAME
    )
    return {"provisioning_uri": uri, "secret_key": secret_key}


def verify_totp(secret_key: str, answer: str, valid_window=0):
    totp = pyotp.TOTP(secret_key)
    return totp.verify(answer, valid_window=valid_window)
