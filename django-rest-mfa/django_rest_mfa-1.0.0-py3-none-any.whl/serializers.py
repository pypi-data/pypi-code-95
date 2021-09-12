from rest_framework import serializers, exceptions
from .totp import verify_totp
from .fido2 import fido2_complete_registration
from .trusted_device import generate_ua_short
from .models import UserKey
from .fields import BinaryField
from .helpers import get_expirable_var


class BaseUserKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserKey
        extra_kwargs = {"properties": {"write_only": True}}


class UserKeySerializer(BaseUserKeySerializer):
    class Meta(BaseUserKeySerializer.Meta):
        fields = (
            "id",
            "user",
            "name",
            "created",
            "key_type",
            "last_used",
            "properties",
        )


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField()


class BackupCodeAuthSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=16, min_length=16)


class OTPUserKeySerializer(BaseUserKeySerializer):
    answer = serializers.CharField(write_only=True)
    secret_key = serializers.RegexField(
        r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$",
        write_only=True,
    )

    class Meta(BaseUserKeySerializer.Meta):
        fields = ("id", "name", "answer", "secret_key")
        read_only_fields = ("name",)

    def validate(self, data):
        user = self.context["request"].user
        if user.userkey_set.filter(key_type=UserKey.KeyType.TOTP).exists():
            raise serializers.ValidationError("User may only set up TOTP once")
        answer = data.pop("answer")

        if not verify_totp(data["secret_key"], answer, valid_window=60):
            raise serializers.ValidationError("Invalid Verification Answer")

        return data

    def create(self, validated_data):
        validated_data["properties"] = {"secret_key": validated_data.pop("secret_key")}
        return super().create(validated_data)


class FIDO2RegistrationSerializer(BaseUserKeySerializer):
    """
    attestationObject and clientDataJSON are specified to be ArrayBuffer and not strings.
    https://developers.yubico.com/WebAuthn/WebAuthn_Developer_Guide/WebAuthn_Client_Registration.html
    """

    attestationObject = BinaryField(write_only=True)
    clientDataJSON = BinaryField(write_only=True)

    class Meta(BaseUserKeySerializer.Meta):
        fields = ("id", "name", "attestationObject", "clientDataJSON")

    def create(self, validated_data):
        fido_state = get_expirable_var(self.context["request"].session, "fido_state")

        try:
            properties = fido2_complete_registration(
                validated_data.pop("clientDataJSON"),
                validated_data.pop("attestationObject"),
                fido_state,
            )
        except ValueError as exc:
            raise exceptions.ValidationError(str(exc))
        except TypeError:
            raise exceptions.ValidationError("Invalid data")

        validated_data["properties"] = properties
        return super().create(validated_data)


class FIDO2AuthenticateSerializer(serializers.Serializer):
    credentialId = BinaryField()
    authenticatorData = BinaryField()
    clientDataJSON = BinaryField()
    signature = BinaryField()


class TrustedDeviceSerializer(BaseUserKeySerializer):
    key = serializers.CharField(write_only=True, min_length=20, max_length=20)

    class Meta(BaseUserKeySerializer.Meta):
        fields = ("id", "name", "key")

    def create(self, validated_data):
        validated_data["properties"] = {
            "key": validated_data.pop("key"),
            "ua": generate_ua_short(self.context["request"].META["HTTP_USER_AGENT"]),
        }
        return super().create(validated_data)


class BackupCodesGenerateSerializer(serializers.Serializer):
    """Read only, generate uncommitted backup codes only serializer"""

    codes = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
        min_length=1,
        max_length=100,
        required=False,
        help_text="List of backup codes, leave blank to automatically generate"
    )


class BackupCodesSerializer(BaseUserKeySerializer, BackupCodesGenerateSerializer):
    class Meta(BaseUserKeySerializer.Meta):
        fields = ("id", "name", "codes")

    def create(self, validated_data):
        return UserKey.make_new_backup_codes_for_user(
            validated_data.get("user"), validated_data.get("name"), validated_data.get("codes")
        )
