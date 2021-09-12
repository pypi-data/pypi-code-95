import secrets
import string
from django.conf import settings
from django.db import models
from django.utils import timezone


class UserKey(models.Model):
    class KeyType(models.TextChoices):
        FIDO2 = "FIDO2"
        TOTP = "TOTP"
        DEVICE = "Trusted Device"
        BACKUP_CODES = "Backup Codes"

    name = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    key_type = models.CharField(max_length=25, choices=KeyType.choices)
    properties = models.JSONField(default=dict)
    last_used = models.DateTimeField(null=True, default=None, blank=True)

    def __str__(self):
        return "%s - %s" % (self.name, self.key_type)

    def set_session_mfa(self, session):
        mfa = {"verified": True, "method": self.key_type, "id": self.pk}
        session["mfa"] = mfa

    def login_success(self, session):
        self.last_used = timezone.now()
        self.save()
        self.set_session_mfa(session)

    @classmethod
    def generate_backup_codes(cls, amount=10, length=16):
        return [
            "".join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(length)
            )
            for _ in range(amount)
        ]

    @classmethod
    def make_new_backup_codes_for_user(cls, user, name="Backup Codes", backup_codes=None, amount=10, length=16):
        """Create new backup codes, replace any existing"""
        # Default 10 codes of 16 chars each
        if backup_codes is None:
            backup_codes = cls.generate_backup_codes(amount=amount, length=length)
        user_key, created = cls.objects.get_or_create(
            user=user,
            key_type=cls.KeyType.BACKUP_CODES,
            defaults={"properties": {"codes": backup_codes}, "name": name},
        )
        if not created:
            user_key.properties = {"codes": backup_codes}
            user_key.name = name
            user_key.save()
        return user_key

    def codes(self):
        return self.properties.get("codes")