from django.conf import settings
from redis import Redis
from rest_framework import serializers

from ..models import User
from ..redis import REDIS_CONNECTION_POOL
from ..rest.serializers import ModelSerializer
from ..serializers.group import GroupSerializer


class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)
    permission_group_id = serializers.SerializerMethodField()
    permission_group = GroupSerializer(read_only=True, many=True)
    online = serializers.SerializerMethodField()

    def get_online(self, obj):
        login_user_key = settings.IACS_SETTINGS["LOGIN_USER_KEY"].format(user_id=obj.id)
        redis_conn = Redis(connection_pool=REDIS_CONNECTION_POOL)
        exist = redis_conn.exists(login_user_key)
        if exist == 1:
            return True
        return False

    def get_permission_group_id(self, instance):
        return list(instance.permission_group.values_list("id", flat=True))

    class Meta:
        model = User
        exclude = ["api"]
