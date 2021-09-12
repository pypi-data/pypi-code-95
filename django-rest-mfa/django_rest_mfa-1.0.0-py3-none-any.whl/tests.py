from django.contrib.auth import get_user_model
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APITestCase
import pyotp
from fido2 import cbor

from .totp import generate_totp_key
from .models import UserKey
from .helpers import set_expirable_var
from .constants import USER_PK_SESSION_KEY

from django_rest_mfa.fido2 import fido2_complete_registration


class UserKeyTests(APITestCase):
    def setUp(self):
        self.user = baker.make(get_user_model())
        self.client.force_login(self.user)

    def test_list(self):
        url = reverse("user-keys-list")
        key = baker.make("django_rest_mfa.UserKey", user=self.user, name="one")
        key2 = baker.make("django_rest_mfa.UserKey", name="two")
        res = self.client.get(url)
        self.assertContains(res, key.name)
        self.assertNotContains(res, key2.name)

    def test_delete(self):
        key = baker.make("django_rest_mfa.UserKey", user=self.user)
        url = reverse("user-keys-detail", kwargs={"pk": key.pk})
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 204)

    def test_totp(self):
        url = reverse("user-keys-list") + "totp/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        totp = pyotp.TOTP(res.data["secret_key"])
        data = {"secret_key": res.data["secret_key"], "answer": totp.now()}
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(UserKey.objects.count(), 1)

    def test_invalid_totp(self):
        url = reverse("user-keys-list") + "totp/"
        res = self.client.get(url)
        totp = pyotp.TOTP(res.data["secret_key"])
        data = {"secret_key": res.data["secret_key"], "answer": "111111"}
        res = self.client.post(url, data, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(UserKey.objects.count(), 0)

    def test_fido2(self):
        url = reverse("user-keys-list") + "fido2/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = {
            "attestationObject": b"",
            "clientDataJSON": b"",
            "name": self.user.get_username(),
        }

        # Not sure how to test this
        # res = self.client.post(url, data, format="json")
        # self.assertEqual(res.status_code, 200)
        # self.assertEqual(UserKey.objects.count(), 1)

    def test_invalid_fido2(self):
        url = reverse("user-keys-list") + "fido2/"
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        data = {
            "attestationObject": b"cf",
            "clientDataJSON": b'{"challenge":"P","clientExtensions":{},"hashAlgorithm":"SHA-256","origin":"https://localhost:8000","type":"webauthn.create"}',
            "name": self.user.get_username(),
        }
        res = self.client.post(url, cbor.encode(data), format="json")
        self.assertContains(res, "Invalid data", status_code=400)
        self.assertEqual(UserKey.objects.count(), 0)

    def test_trusted_device(self):
        url = reverse("user-keys-list") + "trusted_device/"
        res = self.client.get(url, HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(res.status_code, 200)

        data = {"key": res.data["key"], "name": res.data["user_agent"]}
        res = self.client.post(url, data, HTTP_USER_AGENT="Mozilla/5.0")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(UserKey.objects.count(), 1)

    def test_backup_codes(self):
        url = reverse("user-keys-list") + "backup_codes/"
        data = {"name": "codes"}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(UserKey.objects.filter(key_type=UserKey.KeyType.BACKUP_CODES).count(), 1)

        # Should always replace codes
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(UserKey.objects.count(), 1)

    def test_premade_backup_codes(self):
        url = reverse("user-keys-list") + "backup_codes/"
        res = self.client.get(url)
        self.assertFalse(UserKey.objects.exists())
        self.assertEqual(res.status_code, 200)
        codes = res.data.get("codes")
        data = {
            "name": "codes",
            "codes": codes
        }
        res=self.client.post(url, data)
        self.assertTrue(UserKey.objects.exists())
        key = UserKey.objects.get()
        self.assertIn(codes[0], key.properties.get("codes"))


class AuthenticateTests(APITestCase):
    def setUp(self):
        self.user = baker.make(get_user_model())

    def test_authenticate_totp(self):
        url = reverse("authenticate-totp")
        totp_key = generate_totp_key(self.user)
        totp = pyotp.TOTP(totp_key["secret_key"])
        key = baker.make(
            "django_rest_mfa.UserKey",
            user=self.user,
            key_type=UserKey.KeyType.TOTP,
            properties={"secret_key": totp_key["secret_key"]},
        )
        session = self.client.session
        set_expirable_var(session, USER_PK_SESSION_KEY, self.user.pk)
        session.save()
        data = {"otp": totp.now()}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 200)

        self.client.logout()
        session = self.client.session
        set_expirable_var(session, USER_PK_SESSION_KEY, self.user.pk)
        session.save()
        res = self.client.post(url, data)
        self.assertContains(res, "OTP already used", status_code=400)

        data = {"otp": "111111"}
        res = self.client.post(url, data)
        self.assertContains(res, "Invalid TOTP code", status_code=400)

        # Refresh session
        self.client.login()
        self.client.logout()
        data = {"otp": totp.now()}
        res = self.client.post(url, data)
        self.assertContains(res, "Unknown user", status_code=400)

    def test_authenticate_fido2(self):
        url = reverse("authenticate-fido2")
        data = {}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 400)

    def test_authenticate_backup_codes(self):
        url = reverse("authenticate-backup-codes")
        codes = [
            "H4DVCQLXLSRJ098Z",
            "8QRWNBO5WHFUJQC3",
            "GL2LQAQVVOQPNELK",
            "PM2CJ5J7X8BKAX3R",
            "5457MUT07EJWH56Y",
            "WFNBXBVKQ6V0J1ZT",
            "Z0QZNQHOUN6KSWOV",
            "Q5SO1TB8LKTHDWZN",
            "4S1F9QGOJ0HMYJFT",
            "IIJ4S9SO3KKZOX4L",
        ]
        key = baker.make(
            "django_rest_mfa.UserKey",
            user=self.user,
            key_type=UserKey.KeyType.BACKUP_CODES,
            properties={"codes": codes},
        )

        data = {"code": codes[0]}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 400)

        session = self.client.session
        set_expirable_var(session, USER_PK_SESSION_KEY, self.user.pk)
        session.save()
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 200)
        key.refresh_from_db()
        self.assertNotIn(codes[0], key.properties.get("codes"))

        data = {"code": codes[0]}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 400)

        data = {"code": codes[1]}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, 200)