from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import *
from rest_framework.validators import UniqueTogetherValidator


class EmailSerializers(serializers.ModelSerializer):
    creator_name = serializers.CharField(max_length=20)
    email_host = serializers.RegexField(regex=r'^(([a-z]+)\.){2}([a-z]+)$', required=True,
                                        error_messages={'required': 'Please enter valid host name',
                                                        'invalid': 'example (Smtp.gmail.com)'})
    email_host_password = serializers.CharField(max_length=50, write_only=True,
                                                required=True,
                                                style={'input_type': 'password', 'placeholder': 'Password'}
                                                )
    email_use_tls = serializers.BooleanField(help_text="True for Gmail")
    email_use_ssl = serializers.BooleanField(help_text="False for Gmail")

    # def validate(self, validated_data):
    #     if EmailModel.objects.exists():
    #         raise ValidationError("Multiple Objects is not allowed this model..")
    #     return super().validate(validated_data)
    #
    # def create(self, validated_data):
    #     validated_data['id'] = 1
    #     return super(EmailSerializers, self).create(validated_data)

    class Meta:
        model = EmailModel
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=EmailModel.objects.all(),
                fields=['email_host_user']
            )
        ]


class EmailReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailReminder
        fields = '__all__'

    def to_representation(self, instance):
        rep = super(EmailReminderSerializer, self).to_representation(instance)
        rep['modules'] = instance.modules.modules
        rep['actions'] = instance.actions.signal_action
        return rep


class PushReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushReminder
        fields = '__all__'


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policies
        fields = '__all__'


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modules
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEmails
        fields ='__all__'
