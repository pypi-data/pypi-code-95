from .validate import is_valid_uuid
from .user_info import UserInfoClient
class DenyAny:
    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class PostWithoutAuth:
    def has_permission(self, request, view):
        return request.method == "POST"


class IsAuthenticated:
    def __is_authenticated(self, request):
        try:
            return is_valid_uuid(str(request.bartab_user))
        except:
            return False


    def has_permission(self, request, view):
        return self.__is_authenticated(request)

    def has_object_permission(self, request, view, obj):
        return self.__is_authenticated(request)


class IsAdminUser(IsAuthenticated):
    user_info_client = UserInfoClient()

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        return self.user_info_client.is_staff(str(request.bartab_user))

    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False

        return self.user_info_client.is_staff(str(request.bartab_user))


class IsSalesUser(IsAuthenticated):
    user_info_client = UserInfoClient()

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        return self.user_info_client.is_sales(str(request.bartab_user))

    def has_object_permission(self, request, view, obj):
        if not super().has_object_permission(request, view, obj):
            return False

        return self.user_info_client.is_sales(str(request.bartab_user))
