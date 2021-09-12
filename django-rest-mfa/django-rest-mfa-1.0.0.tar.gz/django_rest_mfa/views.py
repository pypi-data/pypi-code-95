from django.contrib.auth import get_user_model, login
from rest_framework import viewsets, mixins, permissions, renderers, exceptions, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from .constants import USER_PK_SESSION_KEY, USER_AUTH_BACKEND
from .models import UserKey
from .serializers import (
    UserKeySerializer,
    OTPUserKeySerializer,
    VerifyOTPSerializer,
    FIDO2RegistrationSerializer,
    FIDO2AuthenticateSerializer,
    TrustedDeviceSerializer,
    BackupCodesGenerateSerializer,
    BackupCodesSerializer,
    BackupCodeAuthSerializer
)
from .renderers import CBORRenderer, Base64JSONRenderer
from .parsers import CBORParser, Base64JSONParser
from .helpers import set_expirable_var, get_expirable_var
from .totp import generate_totp_key, verify_totp
from .fido2 import (
    generate_fido2_registration,
    fido2_begin_authenticate,
    fido2_complete_authenticate,
)
from .trusted_device import generate_random_key, generate_ua_short


class UserKeyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Manage User Keys, including view and delete."""

    queryset = UserKey.objects.none()
    serializer_class = UserKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [
        Base64JSONRenderer,
        renderers.BrowsableAPIRenderer,
        CBORRenderer,
        renderers.MultiPartRenderer,
    ]
    parser_classes = [Base64JSONParser, CBORParser, parsers.MultiPartParser]

    def get_queryset(self):
        return self.request.user.userkey_set.all()

    def get_serializer_class(self):
        if self.action == "totp":
            return OTPUserKeySerializer
        if self.action == "fido2":
            return FIDO2RegistrationSerializer
        if self.action == "trusted_device":
            return TrustedDeviceSerializer
        if self.action == "backup_codes":
            return BackupCodesSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["get", "post"], name="Set up TOTP")
    def totp(self, request):
        """Set up TOTP (Time-Based One Time Password)"""
        if request.method == "GET":
            result = generate_totp_key(request.user)
            return Response(result)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            key_type=UserKey.KeyType.TOTP, user=self.request.user, name="TOTP"
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get", "post"], name="Add new FIDO2 Key")
    def fido2(self, request):
        if request.method == "GET":
            registration_data, state = generate_fido2_registration(request.user)
            set_expirable_var(request.session, "fido_state", state)
            return Response(registration_data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(key_type=UserKey.KeyType.FIDO2, user=self.request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get", "post"], name="Add a trusted device")
    def trusted_device(self, request):
        if request.method == "GET":
            key = generate_random_key()
            user_agent = generate_ua_short(request.META["HTTP_USER_AGENT"])
            return Response({
                "key": key,
                "user_agent": user_agent
            })

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(key_type=UserKey.KeyType.DEVICE, user=self.request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["get", "post"], name="Set backup codes")
    def backup_codes(self, request):
        """
        Make one time backup codes for user
        Only one set up codes may exist, requesting new ones will delete existing

        GET method is optional for generating the codes in advance before commiting to the database
        POST method will commit to the database. If codes is not set, it will generate them.
        """
        if request.method == "GET":
             codes = UserKey.generate_backup_codes()
             serializer = BackupCodesGenerateSerializer({"codes": codes})
             return Response(serializer.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(key_type=UserKey.KeyType.BACKUP_CODES, user=self.request.user)
        return Response(serializer.data)


class MFAAuthenticateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_user(self, request):
        user = request.user
        if not user.is_authenticated:
            User = get_user_model()
            try:
                user_pk = get_expirable_var(request.session, USER_PK_SESSION_KEY)
                auth_backend = get_expirable_var(request.session, USER_AUTH_BACKEND)
                user = User.objects.get(pk=user_pk)
                if auth_backend:
                    user.backend=auth_backend
            except User.DoesNotExist:
                raise exceptions.ValidationError("Unknown user")
        return user
    
    def success(self, request, user, key):
        key.login_success(request.session)
        if not request.user.is_authenticated:
            res = login(request, user)



class FIDO2Authenticate(MFAAuthenticateAPIView):
    renderer_classes = [
        Base64JSONRenderer,
        renderers.BrowsableAPIRenderer,
        CBORRenderer,
    ]
    parser_classes = [Base64JSONParser, CBORParser]

    def get(self, request):
        user = self.get_user(request)
        auth_data, state = fido2_begin_authenticate(user)
        set_expirable_var(request.session, "fido_state", state)
        return Response(auth_data)

    def post(self, request):
        user = self.get_user(request)
        serializer = FIDO2AuthenticateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            key = fido2_complete_authenticate(
                user,
                data["credentialId"],
                data["clientDataJSON"],
                data["authenticatorData"],
                data["signature"],
                get_expirable_var(request.session, "fido_state"),
            )
        except ValueError as exc:
            raise exceptions.ValidationError(str(exc))

        self.success(request, user, key)
        return Response()


class TOTPAuthenticate(MFAAuthenticateAPIView):
    def post(self, request):
        user = self.get_user(request)
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data["otp"]
        try:
            key = user.userkey_set.get(key_type=UserKey.KeyType.TOTP)
        except UserKey.DoesNotExist:
            raise exceptions.ValidationError("TOTP is not enabled for user")

        if key.properties.get("last_otp") == otp:
            raise exceptions.ValidationError("OTP already used")

        success = verify_totp(
            key.properties.get("secret_key"), otp, 1
        )
        if not success:
            raise exceptions.ValidationError("Invalid TOTP code")
        key.properties["last_otp"] = otp
        self.success(request, user, key)
        return Response()


class BackupCodesAuthenticate(MFAAuthenticateAPIView):
    def post(self, request):
        user = self.get_user(request)
        serializer = BackupCodeAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get("code")
        key = user.userkey_set.filter(key_type=UserKey.KeyType.BACKUP_CODES).first()
        if not key or code not in key.properties.get("codes"):
            raise exceptions.ValidationError("Backup code not found")
        self.success(request, user, key)

        # Remove used code
        key.properties["codes"].remove(code)
        key.save()
        return Response()
