from rest_framework import serializers
# from ..models.profile_models import Profile
from ..models import get_user_profile_model

Profile = get_user_profile_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['id', 'user']
